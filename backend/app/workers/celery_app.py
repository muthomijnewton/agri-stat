import os
from celery import Celery
from celery.schedules import crontab
from app.core.config import SECRET_KEY  # Load configured environment before worker settings.

celery_app = Celery("agricstat", broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                    include=["app.workers.tasks"])
celery_app.conf.update(
    timezone=os.getenv("APP_TIMEZONE", "Africa/Nairobi"), enable_utc=True,
    task_serializer="json", result_serializer="json", accept_content=["json"],
    task_default_queue="agricstat-phase1",
    task_routes={"foundation.refresh_markets": {"queue": "agricstat-markets"}},
    result_expires=86400, worker_prefetch_multiplier=1,
    task_soft_time_limit=540, task_time_limit=600,
    broker_connection_retry_on_startup=True,
    broker_transport_options={"socket_connect_timeout": 2, "socket_timeout": 2, "global_keyprefix": "agristat:phase1:"},
    result_backend_transport_options={"global_keyprefix": "agristat:phase1:"},
    beat_schedule={
        "weather-at-0500-local": {"task": "foundation.refresh_weather", "schedule": crontab(hour=5, minute=0)},
        "batch-status-at-0505-local": {"task": "foundation.refresh_batches", "schedule": crontab(hour=5, minute=5)},
        "market-data-at-0600-local": {"task": "foundation.refresh_markets", "schedule": crontab(hour=6, minute=0)},
    },
)
