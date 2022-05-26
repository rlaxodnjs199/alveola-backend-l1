from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __mapper_args__ = {"eager_defaults": True}
