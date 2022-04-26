from pydantic import BaseModel, Field


class CTScanRequestSchema(BaseModel):
    project: str = Field(..., description="Project")
    row: int = Field(..., description="SheetRowIndex")
    in_ex: str = Field(..., description="IN/EX")
