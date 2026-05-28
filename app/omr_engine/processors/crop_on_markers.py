import os
import cv2
import numpy as np

from app.omr_engine.image_constants import (
    DEFAULT_BLACK_COLOR,
    DEFAULT_BORDER_REMOVE,
    DEFAULT_GAUSSIAN_BLUR_PARAMS_MARKER,
    DEFAULT_LINE_WIDTH,
    DEFAULT_NORMALIZE_PARAMS,
    DEFAULT_WHITE_COLOR,
    ERODE_RECT_COLOR,
    EROSION_PARAMS,
    MARKER_RECTANGLE_COLOR,
    NORMAL_RECT_COLOR,
    QUADRANT_DIVISION,
)
from app.omr_engine.logger import logger
from app.omr_engine.processors.interfaces.ImagePreprocessor import ImagePreprocessor
from app.omr_engine.image_utils import ImageUtils


class CropOnMarkers(ImagePreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = self.tuning_config
        marker_ops = self.options
        self.threshold_circles = []

        self.marker_path = os.path.join(
            self.relative_dir or "", marker_ops.get("relativePath", "omr_marker.jpg")
        )
        self.min_matching_threshold = marker_ops.get("min_matching_threshold", 0.3)
        self.max_matching_variation = marker_ops.get("max_matching_variation", 0.41)
        self.marker_rescale_range = tuple(
            int(r) for r in marker_ops.get("marker_rescale_range", (35, 100))
        )
        self.marker_rescale_steps = int(marker_ops.get("marker_rescale_steps", 10))
        self.apply_erode_subtract = marker_ops.get("apply_erode_subtract", True)
        self.marker = None

    def set_marker_image(self, marker_image: np.ndarray):
        self.marker = marker_image

    def exclude_files(self):
        return [self.marker_path]

    def apply_filter(self, image, file_path):
        config = self.tuning_config
        image_instance_ops = self.image_instance_ops

        if self.marker is None:
            logger.error("Marker image not set. Cannot apply CropOnMarkers.")
            return None

        image_eroded_sub = ImageUtils.normalize_util(
            image if self.apply_erode_subtract
            else (image - cv2.erode(
                image, kernel=np.ones(EROSION_PARAMS["kernel_size"]),
                iterations=EROSION_PARAMS["iterations"],
            ))
        )

        h1, w1 = image_eroded_sub.shape[:2]
        midh, midw = (
            h1 // QUADRANT_DIVISION["height_factor"],
            w1 // QUADRANT_DIVISION["width_factor"],
        )
        origins = [[0, 0], [midw, 0], [0, midh], [midw, midh]]
        quads = {
            0: image_eroded_sub[0:midh, 0:midw],
            1: image_eroded_sub[0:midh, midw:w1],
            2: image_eroded_sub[midh:h1, 0:midw],
            3: image_eroded_sub[midh:h1, midw:w1],
        }

        image_eroded_sub[:, midw:midw + 2] = DEFAULT_WHITE_COLOR
        image_eroded_sub[midh:midh + 2, :] = DEFAULT_WHITE_COLOR

        best_scale, all_max_t = self._get_best_match(image_eroded_sub)
        if best_scale is None:
            return None

        optimal_marker = ImageUtils.resize_util_h(
            self.marker, u_height=int(self.marker.shape[0] * best_scale)
        )
        _h, w = optimal_marker.shape[:2]
        centres = []
        sum_t, max_t = 0, 0
        quarter_match_log = "Matching Marker:  "

        for k in range(0, 4):
            res = cv2.matchTemplate(quads[k], optimal_marker, cv2.TM_CCOEFF_NORMED)
            max_t = res.max()
            quarter_match_log += f"Quarter{str(k + 1)}: {str(round(max_t, 3))}\t"

            if max_t < self.min_matching_threshold or abs(all_max_t - max_t) >= self.max_matching_variation:
                logger.error(f"No marker found in Quad {k + 1}")
                return None

            pt = np.argwhere(res == max_t)[0]
            pt = [pt[1], pt[0]]
            pt[0] += origins[k][0]
            pt[1] += origins[k][1]

            image = cv2.rectangle(image, tuple(pt), (pt[0] + w, pt[1] + _h), MARKER_RECTANGLE_COLOR, DEFAULT_LINE_WIDTH)
            image_eroded_sub = cv2.rectangle(
                image_eroded_sub, tuple(pt), (pt[0] + w, pt[1] + _h),
                ERODE_RECT_COLOR if self.apply_erode_subtract else NORMAL_RECT_COLOR, 4,
            )
            centres.append([pt[0] + w / 2, pt[1] + _h / 2])
            sum_t += max_t

        logger.info(quarter_match_log)
        logger.info(f"Optimal Scale: {best_scale}")
        self.threshold_circles.append(sum_t / 4)

        image = ImageUtils.four_point_transform(image, np.array(centres))
        image_instance_ops.append_save_img(2, image_eroded_sub)

        return image

    def _get_best_match(self, image_eroded_sub):
        descent_per_step = (
            self.marker_rescale_range[1] - self.marker_rescale_range[0]
        ) // self.marker_rescale_steps
        _h, _w = self.marker.shape[:2]
        best_scale, all_max_t = None, 0

        for r0 in np.arange(
            self.marker_rescale_range[1], self.marker_rescale_range[0],
            -1 * descent_per_step,
        ):
            s = float(r0 * 1 / 100)
            if s == 0.0:
                continue
            rescaled_marker = ImageUtils.resize_util_h(self.marker, u_height=int(_h * s))
            res = cv2.matchTemplate(image_eroded_sub, rescaled_marker, cv2.TM_CCOEFF_NORMED)
            max_t = res.max()
            if all_max_t < max_t:
                best_scale, all_max_t = s, max_t

        if all_max_t < self.min_matching_threshold:
            logger.warning("Template matching too low!")

        return best_scale, all_max_t
