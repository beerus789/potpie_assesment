from celery import Celery

celery_app = Celery(
    "doc_processor",
    broker="redis://localhost:6379/0",  # Change to your broker URL
    backend="redis://localhost:6379/1",
)
celery_app.conf.task_routes = {"app.document_tasks.*": {"queue": "docs"}}
celery_app.conf.task_time_limit = 60 * 10  # 10 minutes
