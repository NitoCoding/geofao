import logging
import os
import shutil
import time

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)

TEMP_MAX_AGE_SECONDS = 5 * 60 * 60


@shared_task
def cleanup_old_temp_files() -> dict:
    """Hapus entri di MEDIA_ROOT/temp yang lebih tua dari 5 jam."""
    temp_root = os.path.join(settings.MEDIA_ROOT, "temp")
    if not os.path.isdir(temp_root):
        return {"removed": 0, "skipped": 0}

    cutoff = time.time() - TEMP_MAX_AGE_SECONDS
    removed = skipped = 0

    for name in os.listdir(temp_root):
        path = os.path.join(temp_root, name)
        try:
            if os.path.getmtime(path) >= cutoff:
                continue
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            removed += 1
        except OSError as e:
            skipped += 1
            logger.warning(f"Gagal menghapus temp '{path}': {e}")

    logger.info(f"Cleanup temp selesai: {removed} dihapus, {skipped} dilewati")
    return {"removed": removed, "skipped": skipped}
