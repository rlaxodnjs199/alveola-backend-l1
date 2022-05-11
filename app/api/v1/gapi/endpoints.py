from typing import Dict, List
from fastapi import APIRouter, Depends

from app.core.gapi.schemas import CTScanRequestSchema
from .dal import GSheetsDAL, get_gsheets_dal
from .util import deidentify_ctscan

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
    ctscan_requests: List[CTScanRequestSchema],
    gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal)),
) -> Dict:
    for ctscan_request in ctscan_requests:
        ctscan = gsheets_dal.get_ctscan(ctscan_request)
        deidentify_ctscan(ctscan, gsheets_dal)

    return ctscan
