from typing import Dict, List
from fastapi import APIRouter, Depends

from app.core.gapi.schemas import CTScanRequestSchema
from .dal import GSheetsDAL, get_gsheets_dal
from .util import Deidentifier

gapi_router = APIRouter(
    prefix="/gapi", tags=["gapi"], responses={404: {"description": "Not found"}}
)


@gapi_router.get("/projects")
def get_project_list(gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal))) -> Dict:
    worksheets = gsheets_dal.get_project_list()
    # projects = [worksheet.title for worksheet in worksheets]
    # # Remove sheets not projects
    # projects.remove("Dictionary")
    # projects.remove("Template")
    # projects.remove("New Template")
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
def deidentify_ctscans(
    ct_scan_requests: List[CTScanRequestSchema],
    gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal)),
) -> Dict:
    for ct_scan_request in ct_scan_requests:
        qct_scan = gsheets_dal.get_ctscan(ct_scan_request)
        Deidentifier(qct_scan).run()

    return {"message": "success!"}
