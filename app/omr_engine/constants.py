from dotmap import DotMap

TEMPLATE_FILENAME = "template.json"
EVALUATION_FILENAME = "evaluation.json"
CONFIG_FILENAME = "config.json"

FIELD_LABEL_NUMBER_REGEX = r"([^\d]+)(\d*)"

ERROR_CODES = DotMap(
    {"MULTI_BUBBLE_WARN": 1, "NO_MARKER_ERR": 2},
    _dynamic=False,
)

FIELD_TYPES = {
    "QTYPE_INT": {
        "bubbleValues": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "direction": "vertical",
    },
    "QTYPE_INT_FROM_1": {
        "bubbleValues": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        "direction": "vertical",
    },
    "QTYPE_MCQ4": {"bubbleValues": ["A", "B", "C", "D"], "direction": "horizontal"},
    "QTYPE_MCQ5": {"bubbleValues": ["A", "B", "C", "D", "E"], "direction": "horizontal"},
    "QTYPE_MCQ4_RTL": {"bubbleValues": ["D", "C", "B", "A"], "direction": "horizontal"},
    "QTYPE_MCQ5_RTL": {"bubbleValues": ["E", "D", "C", "B", "A"], "direction": "horizontal"},
}

TEXT_SIZE = 0.95
CLR_BLACK = (50, 150, 150)
CLR_WHITE = (250, 250, 250)
CLR_GRAY = (130, 130, 130)
CLR_DARK_GRAY = (100, 100, 100)

GLOBAL_PAGE_THRESHOLD_WHITE = 200
GLOBAL_PAGE_THRESHOLD_BLACK = 100
