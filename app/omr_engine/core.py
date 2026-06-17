import cv2
import numpy as np

from app.omr_engine.constants import (
    CLR_BLACK, CLR_DARK_GRAY, CLR_GRAY, TEXT_SIZE,
    GLOBAL_PAGE_THRESHOLD_BLACK, GLOBAL_PAGE_THRESHOLD_WHITE,
)
from app.omr_engine.image_utils import CLAHE_HELPER, ImageUtils
from app.omr_engine.logger import logger


class ImageInstanceOps:
    def __init__(self, tuning_config):
        self.tuning_config = tuning_config
        self.save_image_level = tuning_config.outputs.save_image_level
        self.save_img_list = {}

    def reset_all_save_img(self):
        self.save_img_list = {}

    def append_save_img(self, key, img):
        if self.save_image_level >= int(key):
            if key not in self.save_img_list:
                self.save_img_list[key] = []
            self.save_img_list[key].append(img.copy())

    def apply_preprocessors(self, file_path, in_omr, template):
        tuning_config = self.tuning_config
        in_omr = ImageUtils.resize_util(
            in_omr,
            tuning_config.dimensions.processing_width,
            tuning_config.dimensions.processing_height,
        )
        for pre_processor in template.pre_processors:
            in_omr = pre_processor.apply_filter(in_omr, file_path)
            if in_omr is None:
                return None
        return in_omr

    def read_omr_response(self, template, image, name, save_dir=None):
        config = self.tuning_config
        auto_align = config.alignment_params.auto_align

        try:
            img = image.copy()
            img = ImageUtils.resize_util(img, template.page_dimensions[0], template.page_dimensions[1])

            if img.max() > img.min():
                img = ImageUtils.normalize_util(img)

            transp_layer = img.copy()
            final_marked = img.copy()
            morph = img.copy()
            self.append_save_img(3, morph)

            if auto_align:
                morph = CLAHE_HELPER.apply(morph)
                self.append_save_img(3, morph)
                morph = ImageUtils.adjust_gamma(morph, config.threshold_params.GAMMA_LOW)
                _, morph = cv2.threshold(morph, 220, 220, cv2.THRESH_TRUNC)
                morph = ImageUtils.normalize_util(morph)
                self.append_save_img(3, morph)

            alpha = 0.65
            omr_response = {}
            multi_marked = False

            if auto_align:
                v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 10))
                morph_v = cv2.morphologyEx(morph, cv2.MORPH_OPEN, v_kernel, iterations=3)
                _, morph_v = cv2.threshold(morph_v, 200, 200, cv2.THRESH_TRUNC)
                morph_v = 255 - ImageUtils.normalize_util(morph_v)
                self.append_save_img(3, morph_v)

                morph_thr = 60
                _, morph_v = cv2.threshold(morph_v, morph_thr, 255, cv2.THRESH_BINARY)
                morph_v = cv2.erode(morph_v, np.ones((5, 5), np.uint8), iterations=2)
                self.append_save_img(3, morph_v)

                for field_block in template.field_blocks:
                    s, d = field_block.origin, field_block.dimensions
                    match_col = config.alignment_params.match_col
                    max_steps = config.alignment_params.max_steps
                    align_stride = config.alignment_params.stride
                    thk = config.alignment_params.thickness

                    shift, steps = 0, 0
                    while steps < max_steps:
                        left_mean = np.mean(
                            morph_v[s[1]:s[1] + d[1], s[0] + shift - thk: -thk + s[0] + shift + match_col]
                        )
                        right_mean = np.mean(
                            morph_v[
                                s[1]:s[1] + d[1],
                                s[0] + shift - match_col + d[0] + thk: thk + s[0] + shift + d[0],
                            ]
                        )
                        left_shift, right_shift = left_mean > 100, right_mean > 100
                        if left_shift:
                            if right_shift:
                                break
                            else:
                                shift -= align_stride
                        else:
                            if right_shift:
                                shift += align_stride
                            else:
                                break
                        steps += 1
                    field_block.shift = shift

            all_q_vals, all_q_strip_arrs, all_q_std_vals = [], [], []
            total_q_strip_no = 0

            for field_block in template.field_blocks:
                box_w, box_h = field_block.bubble_dimensions
                for field_block_bubbles in field_block.traverse_bubbles:
                    q_strip_vals = []
                    for pt in field_block_bubbles:
                        x, y = (pt.x + field_block.shift, pt.y)
                        rect = [y, y + box_h, x, x + box_w]
                        q_strip_vals.append(cv2.mean(img[rect[0]:rect[1], rect[2]:rect[3]])[0])
                    all_q_std_vals.append(round(np.std(q_strip_vals), 2))
                    all_q_strip_arrs.append(q_strip_vals)
                    all_q_vals.extend(q_strip_vals)
                    total_q_strip_no += 1

            global_std_thresh, _, _ = self.get_global_threshold(all_q_std_vals)
            thr_gap, _, _ = self.get_global_threshold(all_q_vals, looseness=4)
            # Blend gap-based threshold with Otsu to stabilize across lighting conditions
            try:
                vals = np.clip(np.array(all_q_vals, dtype=np.float32), 0, 255).astype(np.uint8).reshape(-1, 1)
                _ret, thr_otsu = cv2.threshold(vals, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                thr_otsu = float(thr_otsu)
            except Exception:
                thr_otsu = float(thr_gap)

            blended = 0.6 * float(thr_gap) + 0.4 * float(thr_otsu)
            global_thr = int(max(95, min(210, round(blended))))

            # Safety cap: if blended threshold would mark nearly all bubbles
            # (threshold above 90th percentile), compute Otsu on full image
            # and use it as an upper bound to avoid false positives on dark images.
            try:
                all_p = np.array(all_q_vals)
                p90 = np.percentile(all_p, 90)
                if global_thr > p90:
                    _ret, full_otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    capped = int(round(min(global_thr, float(full_otsu) + 10)))
                    if capped < global_thr:
                        logger.info(f"Thresholding: capped from {global_thr} to {capped} (full Otsu={full_otsu:.0f})")
                        global_thr = max(capped, 95)
            except Exception:
                pass

            logger.info(
                f"Thresholding: global_thr: {round(global_thr, 2)} (gap={round(thr_gap,2)}, otsu={round(thr_otsu,2)}) global_std_THR: {round(global_std_thresh, 2)}"
            )

            per_omr_threshold_avg, total_q_box_no = 0, 0
            total_q_strip_no = 0

            for field_block in template.field_blocks:
                block_q_strip_no = 1
                box_w, box_h = field_block.bubble_dimensions
                shift = field_block.shift
                key = field_block.name[:3]

                for field_block_bubbles in field_block.traverse_bubbles:
                    no_outliers = all_q_std_vals[total_q_strip_no] < global_std_thresh

                    per_q_strip_threshold = self.get_local_threshold(
                        all_q_strip_arrs[total_q_strip_no], global_thr, no_outliers,
                    )
                    per_omr_threshold_avg += per_q_strip_threshold

                    detected_bubbles = []
                    for bubble in field_block_bubbles:
                        bubble_is_marked = per_q_strip_threshold > all_q_vals[total_q_box_no]
                        total_q_box_no += 1
                        if bubble_is_marked:
                            detected_bubbles.append(bubble)
                            x, y = bubble.x + field_block.shift, bubble.y
                            cv2.rectangle(
                                final_marked,
                                (int(x + box_w / 12), int(y + box_h / 12)),
                                (int(x + box_w - box_w / 12), int(y + box_h - box_h / 12)),
                                CLR_DARK_GRAY, 3,
                            )
                            cv2.putText(
                                final_marked, str(bubble.field_value), (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, TEXT_SIZE, (20, 20, 10), int(1 + 3.5 * TEXT_SIZE),
                            )
                        else:
                            x, y = bubble.x + field_block.shift, bubble.y
                            cv2.rectangle(
                                final_marked,
                                (int(x + box_w / 10), int(y + box_h / 10)),
                                (int(x + box_w - box_w / 10), int(y + box_h - box_h / 10)),
                                CLR_GRAY, -1,
                            )

                    for bubble in detected_bubbles:
                        multi_marked_local = bubble.field_label in omr_response
                        omr_response[bubble.field_label] = (
                            omr_response[bubble.field_label] + bubble.field_value
                            if multi_marked_local else bubble.field_value
                        )
                        multi_marked = multi_marked or multi_marked_local

                    if not detected_bubbles:
                        omr_response[field_block_bubbles[0].field_label] = field_block.empty_val

                    block_q_strip_no += 1
                    total_q_strip_no += 1

            cv2.addWeighted(final_marked, alpha, transp_layer, 1 - alpha, 0, final_marked)

            return omr_response, final_marked, multi_marked

        except Exception as e:
            logger.error(f"Error reading OMR response: {e}")
            raise

    def get_global_threshold(self, q_vals_orig, looseness=1):
        config = self.tuning_config
        PAGE_TYPE_FOR_THRESHOLD = config.threshold_params.PAGE_TYPE_FOR_THRESHOLD
        MIN_JUMP = config.threshold_params.MIN_JUMP
        global_default_threshold = (
            GLOBAL_PAGE_THRESHOLD_WHITE if PAGE_TYPE_FOR_THRESHOLD == "white"
            else GLOBAL_PAGE_THRESHOLD_BLACK
        )

        q_vals = sorted(q_vals_orig)
        ls = (looseness + 1) // 2
        l = len(q_vals) - ls
        max1, thr1 = MIN_JUMP, global_default_threshold

        for i in range(ls, l):
            jump = q_vals[i + ls] - q_vals[i - ls]
            if jump > max1:
                max1 = jump
                thr1 = q_vals[i - ls] + jump / 2

        return thr1, thr1 - max1 // 2, thr1 + max1 // 2

    def get_local_threshold(self, q_vals, global_thr, no_outliers):
        config = self.tuning_config
        q_vals = sorted(q_vals)

        if len(q_vals) < 3:
            thr1 = global_thr if np.max(q_vals) - np.min(q_vals) < config.threshold_params.MIN_GAP else np.mean(q_vals)
        else:
            l = len(q_vals) - 1
            max1, thr1 = config.threshold_params.MIN_JUMP, 255
            for i in range(1, l):
                jump = q_vals[i + 1] - q_vals[i - 1]
                if jump > max1:
                    max1 = jump
                    thr1 = q_vals[i - 1] + jump / 2

            confident_jump = config.threshold_params.MIN_JUMP + config.threshold_params.CONFIDENT_SURPLUS
            if max1 < confident_jump and no_outliers:
                thr1 = global_thr

        return thr1
