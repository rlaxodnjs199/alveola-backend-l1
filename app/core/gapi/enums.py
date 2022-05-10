from enum import Enum
from typing import List


class ScanTypeEnum(str, Enum):
    IN = "IN"
    EX = "EX"


class ValidProtocolEnum(Enum):
    IN: List = ["TLC", "IN"]
    EX: List = ["FRC", "RV", "EX"]
