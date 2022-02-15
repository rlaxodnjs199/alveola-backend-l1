from fastapi import APIRouter

dicom_router = APIRouter(prefix="/dicom", tags=['dicom'], responses={404: {"description": "Not found"}})

@dicom_router.get('/deidentify')
async def deidentify_dicom():
    pass