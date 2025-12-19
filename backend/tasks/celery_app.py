"""
Celery application configuration for F1 Sculpture Gallery.
"""

from celery import Celery
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'f1_sculpture',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['backend.tasks.sculpture_tasks']
)

# Configure Celery
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=300,          # 5 minutes max
    task_soft_time_limit=270,     # Soft limit for cleanup
    worker_prefetch_multiplier=1,  # One task at a time per worker

    # Results
    result_expires=settings.task_result_ttl,
    result_extended=True,          # Store task args in result

    # Worker
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory cleanup)
    worker_disable_rate_limits=False,

    # Optimization
    task_acks_late=True,           # Acknowledge after task completion
    task_reject_on_worker_lost=True,

    # Monitoring
    task_send_sent_event=True,
)

logger.info(f"Celery app configured with broker: {settings.celery_broker_url}")

# Optional: Auto-discover tasks
# celery_app.autodiscover_tasks(['backend.tasks'])
