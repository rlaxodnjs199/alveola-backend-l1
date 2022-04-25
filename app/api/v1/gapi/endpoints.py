from typing import Dict
from fastapi import APIRouter, Depends

from .dal import GSheetsDAL, get_gsheets_dal

gapi_router = APIRouter(
    prefix="/gapi", tags=["gapi"], responses={404: {"description": "Not found"}}
)


@gapi_router.get("/projects")
def get_project_list(gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal))) -> Dict:
    worksheets = gsheets_dal.get_project_list()
    projects = [worksheet.title for worksheet in worksheets]
    # Remove sheets not relavant
    projects.remove("Dictionary")
    projects.remove("Template")

    return {"projects": projects}


@gapi_router.get("/projects/{project}")
def get_project_data(
    project: str, gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal))
) -> Dict:
    return gsheets_dal.get_project_data(project)
