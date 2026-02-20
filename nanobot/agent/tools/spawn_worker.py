"""Spawn worker tool — allows a Manager subagent to create other workers."""

from typing import Any

from nanobot.agent.tools.base import Tool


class SpawnWorkerTool(Tool):
    """Tool to spawn a worker subagent by Post ID.

    This tool is exclusively for Manager-type Posts that need to
    delegate sub-tasks to other Company Posts (e.g., analysts, engineers, auditors).
    The spawned worker runs asynchronously and its result is returned when complete.
    """

    def __init__(self, subagent_manager: Any):
        self._manager = subagent_manager

    @property
    def name(self) -> str:
        return "spawn_worker"

    @property
    def description(self) -> str:
        return (
            "Spawn a worker agent based on a Company Post definition. "
            "The worker will execute the given task and return a result. "
            "Use this to delegate sub-tasks to specific roles like analysts, architects, designers, etc."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "post_id": {
                    "type": "string",
                    "description": (
                        "The Post ID of the worker to spawn, "
                        "e.g. 'Post_Requirements_Analyst', 'Post_Company_Architect'. "
                        "Must match a Post defined in the company's POSTS.md."
                    ),
                },
                "task": {
                    "type": "string",
                    "description": (
                        "The task description to assign to the worker. "
                        "Be specific and provide all necessary context."
                    ),
                },
            },
            "required": ["post_id", "task"],
        }

    async def execute(self, post_id: str, task: str, **kwargs: Any) -> str:
        try:
            result = await self._manager.spawn_worker(
                post_id=post_id,
                task=task,
                monitor_channel="subagent",
                monitor_chat_id="internal",
            )
            return result
        except Exception as e:
            return f"Error spawning worker '{post_id}': {str(e)}"
