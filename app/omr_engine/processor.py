import cv2

from app.omr_engine.template import Template
from app.omr_engine.core import ImageInstanceOps
from app.omr_engine.defaults import CONFIG_DEFAULTS


class OMRProcessor:
    def __init__(self, template_data: dict, config_override: dict | None = None):
        tuning_config = CONFIG_DEFAULTS.copy()
        if config_override:
            for section, values in config_override.items():
                if section in tuning_config and isinstance(values, dict):
                    tuning_config[section].update(values)

        self.image_instance_ops = ImageInstanceOps(tuning_config)
        self.template = Template(template_data, self.image_instance_ops)

    def process(self, image: cv2.Mat, file_name: str = "image.jpg"):
        self.image_instance_ops.reset_all_save_img()

        processed = self.image_instance_ops.apply_preprocessors(
            file_name, image, self.template
        )
        if processed is None:
            return None

        response_dict, final_marked, multi_marked = (
            self.image_instance_ops.read_omr_response(
                self.template, image=processed, name=file_name, save_dir=None
            )
        )
        return response_dict, final_marked, multi_marked
