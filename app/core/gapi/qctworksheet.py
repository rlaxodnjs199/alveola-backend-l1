import gspread
from loguru import logger

from app.config import config
from app.core.gapi.models import CTScan


class QCTWorksheet:
    def __init__(self) -> None:
        try:
            gsheet_client = gspread.service_account(
                filename=config.service_account_file
            )
        except:
            logger.exception("gsheet client initialization failed")

        self.sheet = gsheet_client.open_by_key(config.qctworksheet_id)

    def update_on_deidentification(ct_scan: CTScan):
        pass
