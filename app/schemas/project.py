from pydantic import BaseModel, Field


class BaseProjectSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Name")
