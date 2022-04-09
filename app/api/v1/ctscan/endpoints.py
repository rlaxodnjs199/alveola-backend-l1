from fastapi import APIRouter
from app.schemas.ctscan import CTScan
from .util.deidentification import deidentify

ctscan_router = APIRouter(prefix="/ctscan", tags=['ctscan'], responses={404: {"description": "Not found"}})

@ctscan_router.post('/deidentify')
async def deidentify_ctscan(ctscan: CTScan):
    deidentify(ctscan)
    return {'message': 'success'}