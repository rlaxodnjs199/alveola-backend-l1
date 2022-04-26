from functools import lru_cache
from typing import List
from .models import CTScan
from app.core.db.gsheets import QCTWorksheet


class GSheetsDAL:
    def __init__(self) -> None:
        self.qctworksheet = QCTWorksheet().sheet

    def get_project_list(self):
        worksheet_list = self.qctworksheet.worksheets()
        return worksheet_list

    def get_project_data(self, project: str):
        project_worksheet = self.qctworksheet.worksheet(project)
        project_data = project_worksheet.get_all_values()

        if isinstance(project_data, List) and len(project_data) > 0:
            headers = project_data[0]
            rows = project_data[1:]

            project_headers = [
                {"Header": header.upper(), "accessor": header} for header in headers
            ]
            project_rows = [
                {header: val for header, val in zip(headers, row)} for row in rows
            ]

        return {"columns": project_headers, "rows": project_rows}

    def get_ctscan(self, project: str, row: int):
        def construct_ctscan_dict_from_gsheet(gsheet_ctscan: List, row: int):
            return {
                "proj": gsheet_ctscan[0],
                "subj": gsheet_ctscan[1],
                "ctdate": gsheet_ctscan[3],
                "fu": gsheet_ctscan[4],
                "dcm_in_path": gsheet_ctscan[5],
                "dcm_ex_path": gsheet_ctscan[6],
                "qctworksheet_row": row,
            }

        project_worksheet = self.qctworksheet.worksheet(project)
        gsheet_ctscan = project_worksheet.row_values(row)
        ctscan = CTScan(**construct_ctscan_dict_from_gsheet(gsheet_ctscan, row))

        return ctscan


@lru_cache
def get_gsheets_dal() -> GSheetsDAL:
    return GSheetsDAL()
