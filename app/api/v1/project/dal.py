from multiprocessing import synchronize
from multiprocessing.sharedctypes import synchronized
from typing import List, Optional, Union
from requests import delete
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectDAL:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    async def create_project(self, name: str) -> None:
        new_project = Project(name=name)
        self.db_session.add(new_project)
        await self.db_session.flush()

    async def get_all_projects(self) -> List[Project]:
        q = await self.db_session.execute(select(Project).order_by(Project.id))
        return q.scalars().all()

    async def get_project(self, project_id_or_name: Union[int, str]) -> Project:
        if isinstance(project_id_or_name, int):
            q = await self.db_session.execute(
                select(Project).where(Project.id == project_id_or_name)
            )
        else:
            q = await self.db_session.execute(
                select(Project).where(Project.name == project_id_or_name)
            )
        return q.scalars().first()

    async def update_project(self, project_id: int, name: Optional[str]):
        q = update(Project).where(Project.id == project_id)
        if name:
            q = q.values(name=name)
            q.execution_options(synchronize_session="fetch")
            await self.db_session.execute(q)

    async def delete_project(self, project_id: int):
        q = (
            delete(Project)
            .where(Project.id == project_id)
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(q)
