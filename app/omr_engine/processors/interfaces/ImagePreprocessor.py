class Processor:
    def __init__(self, options=None, relative_dir=None, image_instance_ops=None):
        self.options = options or {}
        self.relative_dir = relative_dir
        self.image_instance_ops = image_instance_ops
        self.tuning_config = image_instance_ops.tuning_config if image_instance_ops else None
        self.description = "UNKNOWN"


class ImagePreprocessor(Processor):
    def apply_filter(self, image, filename):
        raise NotImplementedError

    @staticmethod
    def exclude_files():
        return []


class ProcessorManager:
    def __init__(self):
        self.processors = {}
        self._load_builtins()

    def _load_builtins(self):
        from app.omr_engine.processors.crop_on_markers import CropOnMarkers
        self.processors["CropOnMarkers"] = CropOnMarkers

    def get_processor(self, name):
        if name not in self.processors:
            raise ValueError(f"Unknown processor: {name}")
        return self.processors[name]


PROCESSOR_MANAGER = ProcessorManager()
