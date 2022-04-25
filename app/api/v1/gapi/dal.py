from functools import lru_cache
from typing import List
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


@lru_cache
def get_gsheets_dal() -> GSheetsDAL:
    return GSheetsDAL()
