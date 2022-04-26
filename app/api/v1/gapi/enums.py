from enum import Enum
from typing import List


class ScanTypeEnum(Enum):
    IN: str = "IN"
    EX: str = "EX"


class ValidProtocolEnum(Enum):
    IN: List = ["TLC", "IN"]
    EX: List = ["FRC", "RV", "EX"]
