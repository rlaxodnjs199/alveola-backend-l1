from functools import lru_cache
from typing import List
from app.core.gapi.models import CTScan
from app.core.gapi.qctworksheet import QCTWorksheet
from app.core.gapi.schemas import CTScanRequestSchema


class GSheetsDAL:
    qctworksheet = QCTWorksheet().sheet

    def get_project_list(self):
        worksheet_list = GSheetsDAL.qctworksheet.worksheets()
        return worksheet_list

    def get_project_data(self, project: str):
        project_worksheet = GSheetsDAL.qctworksheet.worksheet(project)
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

    def create_project(self, project: str):
        GSheetsDAL.qctworksheet.duplicate_sheet(
            source_sheet_id=0, new_sheet_name=project
        )

    def get_ctscan(self, ct_scan_request: CTScanRequestSchema):
        project_worksheet = GSheetsDAL.qctworksheet.worksheet(ct_scan_request.project)
        gspread_ct_scan = project_worksheet.row_values(ct_scan_request.row_index)
        # Pad list with empty value, need to update hard-coded length later
        gspread_ct_scan += [""] * (13 - len(gspread_ct_scan))
        ct_scan = CTScan.from_gspread(gspread_ct_scan, ct_scan_request.row_index)

        return ct_scan

    # def get_all_subjects(project: str, subject: str):
    #     subjects = GSheetsDAL.qctworksheet.worksheet(project).findall(subject)

    #     return subjects

    # def update_scan_on_deidentification(ctscan: CTScan):
    #     project_worksheet = GSheetsDAL.qctworksheet.worksheet(ctscan.proj)
    #     print(ctscan.__dict__)


@lru_cache
def get_gsheets_dal() -> GSheetsDAL:
    return GSheetsDAL()
