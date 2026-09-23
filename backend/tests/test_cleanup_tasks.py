import os
import time
import tempfile
from backend.app.workers.cleanup_tasks import purge_expired_temp_files
from backend.app.config import settings


def test_purge_expired_temp_files(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setattr(settings, "TEMP_MEDIA_DIR", temp_dir)

        # Create an old file
        old_file = os.path.join(temp_dir, "old_media.mp3")
        with open(old_file, "w") as f:
            f.write("old data")
        
        # Set file time to 2 hours ago
        past_time = time.time() - 7200
        os.utime(old_file, (past_time, past_time))

        # Create a fresh file
        fresh_file = os.path.join(temp_dir, "fresh_media.mp3")
        with open(fresh_file, "w") as f:
            f.write("fresh data")

        # Purge files older than 1 hour (3600 seconds)
        deleted = purge_expired_temp_files(max_age_seconds=3600)

        assert deleted == 1
        assert not os.path.exists(old_file)
        assert os.path.exists(fresh_file)
