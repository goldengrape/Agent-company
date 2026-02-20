from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime

@dataclass
class WorkerState:
    id: str
    post_id: str
    status: str  # active, completed, failed
    current_task: str
    created_at: str
    updated_at: str
    result: Optional[str] = None
    
class WorkerRegistry:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        # Move to workspace/agent_resource (HR department)
        self.registry_file = workspace / "workspace" / "agent_resource" / "workers.json"
        self._workers: Dict[str, WorkerState] = {}
        self._load()
    
    def register(self, worker_id: str, post_id: str, task: str) -> None:
        now = datetime.now().isoformat()
        state = WorkerState(
            id=worker_id,
            post_id=post_id,
            status="active",
            current_task=task,
            created_at=now,
            updated_at=now
        )
        self._workers[worker_id] = state
        self._save()
        
    def update_status(self, worker_id: str, status: str, result: Optional[str] = None) -> None:
        if worker_id in self._workers:
            worker = self._workers[worker_id]
            worker.status = status
            worker.updated_at = datetime.now().isoformat()
            if result:
                worker.result = result
            self._save()
            
    def get(self, worker_id: str) -> Optional[WorkerState]:
        return self._workers.get(worker_id)
        
    def unregister(self, worker_id: str) -> None:
        """Remove a worker from the registry."""
        if worker_id in self._workers:
            del self._workers[worker_id]
            self._save()
        
    def _save(self):
        # Ensure directory exists
        if not self.registry_file.parent.exists():
            self.registry_file.parent.mkdir(parents=True)
            
        data = {wid: asdict(w) for wid, w in self._workers.items()}
        self.registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        
    def _load(self):
        if not self.registry_file.exists():
            return
            
        try:
            content = self.registry_file.read_text(encoding="utf-8")
            data = json.loads(content)
            for wid, w_data in data.items():
                self._workers[wid] = WorkerState(**w_data)
        except Exception:
            # ignore load errors or reset
            self._workers = {}
