import cv2
import numpy as np

from app.omr_engine.logger import logger

CLAHE_HELPER = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))


class ImageUtils:
    @staticmethod
    def save_img(path, final_marked):
        logger.info(f"Saving Image to '{path}'")
        cv2.imwrite(path, final_marked)

    @staticmethod
    def resize_util(img, u_width, u_height=None):
        if u_height is None:
            h, w = img.shape[:2]
            u_height = int(h * u_width / w)
        return cv2.resize(img, (int(u_width), int(u_height)))

    @staticmethod
    def resize_util_h(img, u_height, u_width=None):
        if u_width is None:
            h, w = img.shape[:2]
            u_width = int(w * u_height / h)
        return cv2.resize(img, (int(u_width), int(u_height)))

    @staticmethod
    def grab_contours(cnts):
        if len(cnts) == 2:
            return cnts[0]
        elif len(cnts) == 3:
            return cnts[1]
        raise Exception("Contours tuple must have length 2 or 3")

    @staticmethod
    def normalize_util(img, alpha=0, beta=255):
        return cv2.normalize(img, None, alpha, beta, norm_type=cv2.NORM_MINMAX)

    @staticmethod
    def auto_canny(image, sigma=0.93):
        v = np.median(image)
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        return cv2.Canny(image, lower, upper)

    @staticmethod
    def adjust_gamma(image, gamma=1.0):
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)

    @staticmethod
    def four_point_transform(image, pts):
        rect = ImageUtils.order_points(pts)
        (tl, tr, br, bl) = rect

        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))

        dst = np.array(
            [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
            dtype="float32",
        )

        transform_matrix = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(image, transform_matrix, (max_width, max_height))

    @staticmethod
    def order_points(pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
