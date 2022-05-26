from celery import Celery

from app.config import config

celery = Celery(
    "tasks",
    broker=config.celery_broker_url,
    backend=config.celery_result_backend,
    include=["app.core.gapi.tasks"],
)
