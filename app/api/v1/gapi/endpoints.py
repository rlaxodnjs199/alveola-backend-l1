import os.path

from fastapi import APIRouter, Depends
from loguru import logger
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from app.config import config

gapi_router = APIRouter(
    prefix="/gapi", tags=["gapi"], responses={404: {"description": "Not found"}}
)


@gapi_router.get("/qctworksheet/{proj}")
async def get_qct_worksheet(proj: str):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    if os.path.exists(config.service_account_file):
        creds = service_account.Credentials.from_service_account_file(
            config.service_account_file, scopes=SCOPES
        )
    else:
        logger.error("No valid creds")

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=config.spreadsheet_id, range=proj)
            .execute()
        )
        values = result.get("values", [])
        columns = values[0]
        rows = values[1:]
    except HttpError as err:
        logger.exception(err)

    if isinstance(columns, list):
        return_columns = [
            {"Header": column.upper(), "accessor": column} for column in columns
        ]

    return_rows = []
    for row in rows:
        return_row = {col: val for col, val in zip(columns, row)}
        return_rows.append(return_row)

    return {"columns": return_columns, "rows": return_rows}
