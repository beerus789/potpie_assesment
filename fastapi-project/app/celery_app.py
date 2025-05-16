from celery import Celery
from app.constant import CELERY_SETTINGS

celery_app = Celery(
    CELERY_SETTINGS.CELERY_PROCESSOR,
    broker=CELERY_SETTINGS.BROKER_URL,  # Change to your broker URL
    backend=CELERY_SETTINGS.RESULT_BACKEND,
)
celery_app.conf.task_routes = {"app.document_tasks.*": {"queue": "docs"}}
celery_app.conf.task_time_limit = CELERY_SETTINGS.CELERY_TASK_TIME_LIMIT
