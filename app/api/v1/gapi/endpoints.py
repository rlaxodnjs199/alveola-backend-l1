from typing import Dict, List
from fastapi import APIRouter, Depends

from app.core.gapi.schemas import CTScanRequestSchema
from .dal import GSheetsDAL, get_gsheets_dal
from .util import deidentify_ctscan
from ....core.gapi.enums import ScanTypeEnum

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
    projects = ["New Template"]

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
    ctscans: List[CTScanRequestSchema],
    gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal)),
) -> Dict:
    for ctscan in ctscans:
        ctscan_model = gsheets_dal.get_ctscan(ctscan.project, ctscan.row_index)
        deidentify_ctscan(ctscan_model, ScanTypeEnum(ctscan.type), gsheets_dal)

    return ctscan
