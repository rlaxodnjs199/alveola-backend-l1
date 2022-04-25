from fastapi import APIRouter
from app.schemas.ctscan import CTScan

ctscan_router = APIRouter(
    tags=["ctscan"], responses={404: {"description": "Not found"}}
)
