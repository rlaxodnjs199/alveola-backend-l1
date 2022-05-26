from enum import Enum
from typing import List


class ScanType(str, Enum):
    IN = "IN"
    EX = "EX"
    ALL = "ALL"


class ValidProtocol(Enum):
    IN: List = ["TLC", "IN"]
    EX: List = ["FRC", "RV", "EX"]


class SeriesType(str, Enum):
    IN = "IN"
    EX = "EX"
    SCOUT = "SCOUT"
    DOSE = "DOSE"


class ProjectSeriesRequirement(Enum):
    LHC: List = ["IN", "EX", "SCOUT", "DOSE"]
