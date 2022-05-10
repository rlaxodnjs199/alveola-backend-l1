from datetime import date
from pathlib import Path


class CTScan:
    def __init__(
        self,
        proj: str,
        subj: str,
        mrn: int,
        study_id: str,
        ctdate: date,
        fu: str,
        dcm_in_path: Path,
        dcm_ex_path: Path,
        row_index: int,
        type=None,
    ) -> None:
        self.proj = proj
        self.subj = subj
        self.ctdate = ctdate
        self.mrn = mrn
        self.study_id = study_id
        self.fu = fu
        self.dcm_in_path = dcm_in_path
        self.dcm_ex_path = dcm_ex_path
        self.row_index = row_index
