from typing import Optional
from pydantic import BaseModel
from pathlib import Path
from datetime import date

class CTScan(BaseModel):
  project: str
  subject_id: str
  ctdate: date
  download_path: Path
  deidentify_path: Optional[Path] = None