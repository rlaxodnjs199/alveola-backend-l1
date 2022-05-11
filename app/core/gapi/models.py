from datetime import date
from pathlib import Path
from typing import List


class CTScan:
    def __init__(
        self,
        proj: str,
        subj: str,
        mrn: int,
        study_id: str,
        ctdate: date,
        fu: int,
        dcm_path: Path,
        deid_in_path: Path,
        deid_ex_path: Path,
        row_index: int,
    ) -> None:
        self.proj = proj
        self.subj = subj
        self.ctdate = ctdate
        self.mrn = mrn
        self.study_id = study_id
        self.fu = fu
        self.dcm_path = dcm_path
        self.deid_in_path = deid_in_path
        self.deid_ex_path = deid_ex_path
        self.row_index = row_index
        self.series = []

    @classmethod
    def from_gspread(cls, gspread_ct_scan: List, row_index: int):
        return cls(
            proj=gspread_ct_scan[0],
            subj=gspread_ct_scan[1],
            mrn=gspread_ct_scan[2],
            study_id=gspread_ct_scan[3],
            ctdate=gspread_ct_scan[4],
            fu=gspread_ct_scan[5],
            dcm_path=gspread_ct_scan[6],
            deid_in_path=gspread_ct_scan[7],
            deid_ex_path=gspread_ct_scan[8],
            row_index=row_index,
        )
