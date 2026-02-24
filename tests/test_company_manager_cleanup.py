from nanobot.agent.memory import MemoryStore
from nanobot.agent.worker_registry import WorkerRegistry
from nanobot.company.manager import CompanyManager


def test_cleanup_workers_keeps_registry_records(tmp_path):
    manager = CompanyManager.__new__(CompanyManager)
    manager.workspace = tmp_path
    manager.registry = WorkerRegistry(tmp_path)
    manager._spawned_task_ids = ["w1234567"]

    manager.registry.register("w1234567", "Post_Test", "demo task")
    manager.registry.update_status("w1234567", "completed", "done")

    worker_memory = MemoryStore(tmp_path, agent_id="w1234567")
    worker_memory.write_long_term("temp")
    assert worker_memory.memory_dir.exists()

    manager._cleanup_workers()

    assert manager.registry.get("w1234567") is not None
    assert not worker_memory.memory_dir.exists()
