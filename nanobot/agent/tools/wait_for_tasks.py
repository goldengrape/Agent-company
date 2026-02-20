"""Wait for tasks tool — allows a Manager subagent to wait for spawned workers."""

import asyncio
from typing import Any

from nanobot.agent.tools.base import Tool


class WaitForTasksTool(Tool):
    """Tool to wait for spawned worker subagents to complete.

    This tool is used by Manager-type Posts after they have spawned 
    multiple subtasks using `spawn_worker`. It blocks execution until
    the specified tasks are finished, then returns their final status
    and results, enabling Map-Reduce style workflows.
    """

    def __init__(self, subagent_manager: Any):
        self._manager = subagent_manager

    @property
    def name(self) -> str:
        return "wait_for_tasks"

    @property
    def description(self) -> str:
        return (
            "Wait for one or more previously spawned tasks to complete. "
            "Pass the task IDs you received from `spawn_worker`. "
            "This will block your execution until ALL specified tasks finish, "
            "and then return a summary of their results."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "A list of task IDs to wait for. These IDs are "
                        "returned by the spawn_worker tool. Example: ['abc12345', 'def67890']."
                    ),
                },
                "timeout_seconds": {
                    "type": "integer",
                    "description": (
                        "Optional timeout in seconds. If exceeded, returns the "
                        "current status of all tasks, even if incomplete. Default is 300 (5 mins)."
                    ),
                },
            },
            "required": ["task_ids"],
        }

    async def execute(self, task_ids: list[str], timeout_seconds: int = 300, **kwargs: Any) -> str:
        if not task_ids:
            return "Error: task_ids list cannot be empty."
            
        try:
            result = await self._manager.wait_for_tasks(
                task_ids=task_ids,
                timeout_seconds=timeout_seconds
            )
            return result
        except Exception as e:
            return f"Error waiting for tasks: {str(e)}"
