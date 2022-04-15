from typing import Dict, List
from fastapi import APIRouter, Depends

from .dal import GSheetsDAL, get_gsheets_dal

gsheets_router = APIRouter(
    prefix="/gapi",
    tags=["project-gapi"],
    responses={404: {"description": "Not found"}},
)


@gsheets_router.get("/projects")
def get_projects_list(
    gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal)),
) -> Dict:
    worksheets = gsheets_dal.get_projects_list()
    projects = [worksheet.title for worksheet in worksheets]
    # Remove sheet names which are not projects
    projects.remove("Dictionary")
    projects.remove("Template")
    return {"projects": projects}


@gsheets_router.get("/projects/{project}")
def get_project_data(
    project: str,
    gsheets_dal: GSheetsDAL = (Depends(get_gsheets_dal)),
) -> Dict:
    return gsheets_dal.get_project_data(project)
