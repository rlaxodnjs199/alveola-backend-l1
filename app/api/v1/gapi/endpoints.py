import os.path

from fastapi import APIRouter, Depends
from loguru import logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from app.config import Settings, get_settings

gapi_router = APIRouter(prefix="/gapi", tags=['gapi'], responses={404: {"description": "Not found"}})

@gapi_router.get('/QCT-worksheet/{proj}')
async def get_qct_worksheet(proj: str, settings: Settings = Depends(get_settings)):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    if os.path.exists(settings.service_account_file):
        creds = service_account.Credentials.from_service_account_file(settings.service_account_file, scopes=SCOPES)
    else:
        logger.error('No valid creds')

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=settings.spreadsheetId, range=proj).execute()
        values = result.get('values', [])
        logger.info(values)
    except HttpError as err:
        logger.error(err)