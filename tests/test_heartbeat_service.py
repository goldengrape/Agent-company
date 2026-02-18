import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from nanobot.heartbeat.service import HeartbeatService

@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "workspace" / "tasks").mkdir(parents=True)
    (tmp_path / "src").mkdir()
    return tmp_path

@pytest.fixture
def capture_logs(caplog):
    """Fixture to capture loguru logs into standard logging."""
    from loguru import logger
    import logging
    
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)

@pytest.mark.asyncio
async def test_heartbeat_check_tasks_pending(workspace, capture_logs):
    # Create a pending task
    task_file = workspace / "workspace" / "tasks" / "TASK_test_pending.md"
    task_file.write_text("""
# TASK
**Status**: Pending
    """, encoding="utf-8")

    service = HeartbeatService(workspace=workspace, interval_s=1)
    
    # Run _check_tasks directly
    await service._check_tasks()

    assert "Inbox: Pending Task Found: TASK_test_pending.md" in capture_logs.text

@pytest.mark.asyncio
async def test_heartbeat_check_tasks_stale(workspace, capture_logs):
    # Create an active task that is old
    task_file = workspace / "workspace" / "tasks" / "TASK_test_stale.md"
    task_file.write_text("""
# TASK
**Status**: Active
    """, encoding="utf-8")
    
    # Set mtime to 25 hours ago
    old_time = datetime.now() - timedelta(hours=25)
    # timestamp must be float
    ts = old_time.timestamp()
    import os
    os.utime(task_file, (ts, ts))

    service = HeartbeatService(workspace=workspace, interval_s=1)
    
    await service._check_tasks()

    assert "Inbox: Stale Task Detected: TASK_test_stale.md" in capture_logs.text

@pytest.mark.asyncio
async def test_heartbeat_check_tasks_active_not_stale(workspace, capture_logs):
    # Create an active task that is new
    task_file = workspace / "workspace" / "tasks" / "TASK_test_active.md"
    task_file.write_text("""
# TASK
**Status**: Active
    """, encoding="utf-8")

    service = HeartbeatService(workspace=workspace, interval_s=1)
    
    await service._check_tasks()

    assert "Inbox: Stale Task Detected" not in capture_logs.text
