"""
Temporary Media Auto-Cleanup Worker Tasks.
"""

import os
import time
import logging
from backend.app.workers.celery_app import celery_app
from backend.app.config import settings

logger = logging.getLogger(__name__)


def purge_expired_temp_files(max_age_seconds: int = 3600) -> int:
    """
    Deletes files in the temp scratch directory older than max_age_seconds.
    Returns count of removed files.
    """
    temp_dir = settings.TEMP_MEDIA_DIR
    if not os.path.exists(temp_dir):
        return 0

    now = time.time()
    deleted_count = 0

    try:
        for root, _, files in os.walk(temp_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    stat = os.stat(file_path)
                    file_age = now - stat.st_mtime
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Purged expired temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error scanning temp directory for cleanup: {e}")

    return deleted_count


@celery_app.task(name="cleanup_temporary_media_files")
def cleanup_temporary_media_files(max_age_seconds: int = 3600) -> dict:
    """Hourly periodic Celery task to purge stale media files."""
    count = purge_expired_temp_files(max_age_seconds=max_age_seconds)
    return {"purged_files": count, "timestamp": time.time()}
