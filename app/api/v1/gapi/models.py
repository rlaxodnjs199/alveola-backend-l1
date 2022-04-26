from datetime import date
from pathlib import Path


class CTScan:
    def __init__(
        self,
        proj: str,
        subj: str,
        ctdate: date,
        fu: str,
        dcm_in_path: Path,
        dcm_ex_path: Path,
        qctworksheet_row: int,
    ) -> None:
        self.proj = proj
        self.subj = subj
        self.ctdate = ctdate
        self.fu = fu
        self.in_ex = ""
        self.dcm_in_path = dcm_in_path
        self.dcm_ex_path = dcm_ex_path
        self.qctworksheet_row = qctworksheet_row
