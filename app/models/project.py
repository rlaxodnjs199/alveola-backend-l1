from sqlalchemy import Column, Integer, String
from app.core.db.pgsql import Base
from app.core.db.pgsql.mixins import TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
