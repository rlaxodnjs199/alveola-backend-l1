from typing import Dict, List
from fastapi import APIRouter, Depends

from .dal import GSheetsDAL, get_gsheets_dal
from app.core.gapi.schemas import CTScanRequestSchema

from app.core.gapi.tasks import deidentify_ct_scan

gapi_router = APIRouter(
    prefix="/gapi", tags=["gapi"], responses={404: {"description": "Not found"}}
)


@gapi_router.get("/projects")
def get_project_list(gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal))) -> Dict:
    worksheets = gsheets_dal.get_project_list()
    # projects = [worksheet.title for worksheet in worksheets]
    # Remove sheets not projects
    # projects.remove("Template")
    # projects.remove("Dictionary")
    # projects.remove("Comments")
    projects = ["LHC"]

    return {"projects": projects}


@gapi_router.get("/projects/{project}")
def get_project_data(
    project: str, gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal))
) -> Dict:
    return gsheets_dal.get_project_data(project)


@gapi_router.post("/projects")
def create_project(project: str, gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal))):
    return gsheets_dal.create_project(project)


@gapi_router.post("/deidentify")
def deidentify_ct_scans(
    ct_scan_requests: List[CTScanRequestSchema],
):
    for ct_scan_request in ct_scan_requests:
        task = deidentify_ct_scan.delay(ct_scan_request.dict())
        return {"task_id": task.id}
