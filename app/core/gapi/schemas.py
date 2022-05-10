from pydantic import BaseModel, Field


class CTScanRequestSchema(BaseModel):
    project: str = Field(..., description="Project")
    row_index: int = Field(..., description="QCTWorksheet row index")
    type: str = Field(..., description="Scan Type")
