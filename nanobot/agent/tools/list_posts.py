"""List company posts tool."""

import json
from typing import Any

from nanobot.agent.tools.base import Tool


class ListPostsTool(Tool):
    """List available company posts for reliable delegation."""

    def __init__(self, subagent_manager: Any):
        self._manager = subagent_manager

    @property
    def name(self) -> str:
        return "list_posts"

    @property
    def description(self) -> str:
        return (
            "List valid post IDs from current company configuration. "
            "Use this before spawn_worker to avoid unknown-role errors."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "include_details": {
                    "type": "boolean",
                    "description": (
                        "When true, include summary details for each post "
                        "(description, tools, skills)."
                    ),
                }
            },
            "required": [],
        }

    async def execute(self, include_details: bool = False, **kwargs: Any) -> str:
        try:
            self._manager.company_loader.load_all()
            posts = self._manager.company_loader.posts
            ordered_ids = sorted(posts.keys())
            if not include_details:
                return json.dumps({"posts": ordered_ids}, ensure_ascii=False)

            details: dict[str, dict[str, Any]] = {}
            for post_id in ordered_ids:
                post = posts[post_id]
                details[post_id] = {
                    "description": post.description,
                    "tools": post.tools,
                    "skills": post.skills,
                }
            return json.dumps({"posts": details}, ensure_ascii=False)
        except Exception as e:
            return f"Error listing posts: {str(e)}"

