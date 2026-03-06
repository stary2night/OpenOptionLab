"""
Celery Application Configuration
"""
from celery import Celery
from celery.signals import worker_ready

from app.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "openoptions",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.data_collector",
        "app.tasks.market_data",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_store_eager_result=False,
    task_ignore_result=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Result backend
    result_expires=3600,
    result_backend=settings.CELERY_RESULT_BACKEND,
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        "collect-market-data-5s": {
            "task": "app.services.data_collector.collect_market_data",
            "schedule": 5.0,  # Every 5 seconds
            "options": {"queue": "market"}
        },
        "collect-market-data-1m": {
            "task": "app.services.data_collector.collect_market_data",
            "schedule": 60.0,  # Every 1 minute
            "options": {"queue": "market"}
        },
        "cleanup-old-data": {
            "task": "app.services.data_collector.cleanup_old_data",
            "schedule": 3600.0,  # Every hour
            "options": {"queue": "maintenance"}
        },
    }
)


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Called when worker is ready"""
    print("✅ Celery worker is ready")


# Task definitions
@celery_app.task(bind=True, max_retries=3)
def debug_task(self):
    """Debug task"""
    print(f"Request: {self.request!r}")
    return {"status": "ok"}
