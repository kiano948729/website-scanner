"""
Celery application configuration for background task processing.
"""

from celery import Celery
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "scanner",
    broker=get_settings().REDIS_URL,
    backend=get_settings().REDIS_URL,
    include=[
        "app.services.tasks.crawl_tasks",
        "app.services.tasks.website_check_tasks",
        "app.services.tasks.data_processing_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Amsterdam',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    task_annotations={
        '*': {
            'rate_limit': '10/m',  # 10 tasks per minute
        }
    },
    beat_schedule={
        'crawl-google-maps-daily': {
            'task': 'app.services.tasks.crawl_tasks.crawl_google_maps',
            'schedule': 86400.0,  # 24 hours
        },
        'check-websites-daily': {
            'task': 'app.services.tasks.website_check_tasks.check_all_websites',
            'schedule': 86400.0,  # 24 hours
        },
        'cleanup-old-data': {
            'task': 'app.services.tasks.data_processing_tasks.cleanup_old_data',
            'schedule': 604800.0,  # 7 days
        },
    },
)

# Task routing
celery_app.conf.task_routes = {
    'app.services.tasks.crawl_tasks.*': {'queue': 'crawling'},
    'app.services.tasks.website_check_tasks.*': {'queue': 'website_checking'},
    'app.services.tasks.data_processing_tasks.*': {'queue': 'data_processing'},
}

# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing."""
    logger.info(f'Request: {self.request!r}')


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks."""
    logger.info("Setting up periodic tasks") 