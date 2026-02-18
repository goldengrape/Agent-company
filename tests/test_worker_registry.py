import pytest
from pathlib import Path
from nanobot.agent.worker_registry import WorkerRegistry, WorkerState

@pytest.fixture
def registry(tmp_path):
    return WorkerRegistry(tmp_path)

def test_register_worker(registry):
    registry.register("worker-123", "Post_Dev", "Do something")
    worker = registry.get("worker-123")
    assert worker.id == "worker-123"
    assert worker.post_id == "Post_Dev"
    assert worker.status == "active"
    assert worker.current_task == "Do something"

def test_update_status(registry):
    registry.register("worker-123", "Post_Dev", "Task")
    registry.update_status("worker-123", "completed", result="Done")
    
    worker = registry.get("worker-123")
    assert worker.status == "completed"
    assert worker.result == "Done"

def test_persistence(tmp_path):
    # Create one registry, register a worker
    reg1 = WorkerRegistry(tmp_path)
    reg1.register("worker-persisted", "Post_Test", "Persist me")
    
    # Create another registry instance from same path
    reg2 = WorkerRegistry(tmp_path)
    worker = reg2.get("worker-persisted")
    
    assert worker is not None
    assert worker.post_id == "Post_Test"
