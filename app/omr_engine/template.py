from app.omr_engine.logger import logger
from app.omr_engine.processors.interfaces.ImagePreprocessor import PROCESSOR_MANAGER


class Bubble:
    def __init__(self, pt, field_label, field_type, field_value):
        self.x = round(pt[0])
        self.y = round(pt[1])
        self.field_label = field_label
        self.field_type = field_type
        self.field_value = field_value

    def __str__(self):
        return str([self.x, self.y])


class FieldBlock:
    def __init__(self, block_name, field_block_object):
        self.name = block_name
        self.shift = 0
        self._setup(field_block_object)

    def _setup(self, obj):
        self.bubble_dimensions = obj["bubbleDimensions"]
        self.bubble_values = obj["bubbleValues"]
        self.bubbles_gap = obj["bubblesGap"]
        self.direction = obj.get("direction", "vertical")
        self.field_labels = obj["fieldLabels"]
        self.field_type = obj.get("fieldType", "__CUSTOM__")
        self.labels_gap = obj["labelsGap"]
        self.origin = obj["origin"]
        self.empty_val = obj.get("emptyValue", "")

        self.parsed_field_labels = self.field_labels[:]
        self._calculate_dimensions()
        self._generate_bubble_grid()

    def _calculate_dimensions(self):
        _h, _v = (1, 0) if self.direction == "vertical" else (0, 1)
        values_dim = int(self.bubbles_gap * (len(self.bubble_values) - 1) + self.bubble_dimensions[_h])
        fields_dim = int(self.labels_gap * (len(self.parsed_field_labels) - 1) + self.bubble_dimensions[_v])
        self.dimensions = (
            [fields_dim, values_dim] if self.direction == "vertical" else [values_dim, fields_dim]
        )

    def _generate_bubble_grid(self):
        _h, _v = (1, 0) if self.direction == "vertical" else (0, 1)
        self.traverse_bubbles = []
        lead_point = [float(self.origin[0]), float(self.origin[1])]

        for field_label in self.parsed_field_labels:
            bubble_point = lead_point.copy()
            field_bubbles = []
            for bubble_value in self.bubble_values:
                field_bubbles.append(Bubble(bubble_point.copy(), field_label, self.field_type, bubble_value))
                bubble_point[_h] += self.bubbles_gap
            self.traverse_bubbles.append(field_bubbles)
            lead_point[_v] += self.labels_gap


class Template:
    def __init__(self, template_data: dict, image_instance_ops):
        self.tuning_config = image_instance_ops.tuning_config
        self.image_instance_ops = image_instance_ops
        self.template_data = template_data

        self.page_dimensions = template_data["pageDimensions"]
        self.bubble_dimensions = template_data["bubbleDimensions"]
        self.custom_labels = template_data.get("customLabels", {})
        self.global_empty_val = template_data.get("emptyValue", "")
        self.output_columns = template_data.get("outputColumns", [])

        self._setup_pre_processors(template_data.get("preProcessors", []))
        self._setup_field_blocks(template_data.get("fieldBlocks", {}))
        self._setup_output_columns()

    def _setup_pre_processors(self, pre_processors_list):
        self.pre_processors = []
        for pp_conf in pre_processors_list:
            ProcessorClass = PROCESSOR_MANAGER.get_processor(pp_conf["name"])
            instance = ProcessorClass(
                options=pp_conf.get("options", {}),
                relative_dir=None,
                image_instance_ops=self.image_instance_ops,
            )
            self.pre_processors.append(instance)

    def _setup_field_blocks(self, field_blocks_obj):
        from app.omr_engine.constants import FIELD_TYPES

        self.field_blocks = []
        self.all_parsed_labels = set()

        for block_name, block_obj in field_blocks_obj.items():
            if "fieldType" in block_obj:
                field_type_defaults = FIELD_TYPES.get(block_obj["fieldType"], {})
                merged = {**field_type_defaults, **block_obj}
            else:
                merged = {**block_obj, "fieldType": "__CUSTOM__"}

            merged.setdefault("direction", "vertical")
            merged.setdefault("emptyValue", self.global_empty_val)
            merged.setdefault("bubbleDimensions", self.bubble_dimensions)

            block = FieldBlock(block_name, merged)
            self.field_blocks.append(block)

            for label in block.parsed_field_labels:
                self.all_parsed_labels.add(label)

    def _setup_output_columns(self):
        non_custom = sorted(self.all_parsed_labels - set(self.custom_labels.keys()))
        custom_keys = list(self.custom_labels.keys())

        if not self.output_columns:
            self.output_columns = sorted(non_custom + custom_keys)
