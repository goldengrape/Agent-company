"""Memory system for persistent agent memory."""

from pathlib import Path

import json
import time
from nanobot.utils.helpers import ensure_dir


class MemoryStore:
    """Two-layer memory: MEMORY.md (long-term facts) + HISTORY.md (grep-searchable log)."""
    
    def __init__(self, workspace: Path, agent_id: str | None = None):
        """
        Initialize memory store.
        
        Args:
            workspace: Base workspace path.
            agent_id: Optional ID for worker isolation. If provided, memory uses 
                     workspace/memory/workers/{agent_id}/.
        """
        if agent_id:
            self.memory_dir = ensure_dir(workspace / "workspace" / "memory" / "workers" / agent_id)
        else:
            self.memory_dir = ensure_dir(workspace / "workspace" / "memory")
            
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.history_file = self.memory_dir / "HISTORY.md"
        self.events_file = self.memory_dir / "EVENTS.jsonl"

    def read_long_term(self) -> str:
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def write_long_term(self, content: str) -> None:
        self.memory_file.write_text(content, encoding="utf-8")

    def append_history(self, entry: str) -> None:
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(entry.rstrip() + "\n\n")

    def get_memory_context(self) -> str:
        long_term = self.read_long_term()
        return f"## Long-term Memory\n{long_term}" if long_term else ""

    def log_event(self, event_type: str, details: dict) -> None:
        """Log a structured event for auditing."""
        event = {
            "timestamp": time.time(),
            "iso_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": event_type,
            "details": details
        }
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
