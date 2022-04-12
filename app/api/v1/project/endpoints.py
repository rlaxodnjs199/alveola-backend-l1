from typing import List, Optional, Union
from fastapi import APIRouter
from app.api.v1.project.dal import ProjectDAL
from app.models.project import Project
from app.core.db.pgsql import async_session

project_router = APIRouter(
    tags=["project"], responses={404: {"description": "Not found"}}
)


@project_router.post("/projects")
async def create_project(name: str):
    async with async_session() as session:
        async with session.begin():
            project_dal = ProjectDAL(session)
            return await project_dal.create_project(name)


@project_router.get("/projects")
async def get_all_projects() -> List[Project]:
    async with async_session() as session:
        async with session.begin():
            project_dal = ProjectDAL(session)
            return await project_dal.get_all_projects()


@project_router.get("/projects/{project_id_or_name}")
async def get_project(project_id_or_name: Union[int, str]) -> Project:
    async with async_session() as session:
        async with session.begin():
            project_dal = ProjectDAL(session)
            return await project_dal.get_project(project_id_or_name)


@project_router.put("/projects/{project_id}")
async def update_project(id: int, name: Optional[str] = None):
    async with async_session() as session:
        async with session.begin():
            project_dal = ProjectDAL(session)
            return await project_dal.update_project(id, name)


@project_router.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    async with async_session() as session:
        async with session.begin():
            project_dal = ProjectDAL(session)
            return await project_dal.delete_project(project_id)
