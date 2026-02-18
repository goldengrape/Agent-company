"""Subagent manager for background task execution."""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.bus.events import InboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.providers.base import LLMProvider
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.agent.tools.filesystem import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool
from nanobot.agent.tools.shell import ExecTool
from nanobot.agent.tools.web import WebSearchTool, WebFetchTool
from nanobot.company.loader import CompanyConfigLoader
from nanobot.agent.context import ContextBuilder
from nanobot.agent.skills import SkillsLoader
from nanobot.agent.skills import SkillsLoader
from nanobot.agent.worker_registry import WorkerRegistry
from nanobot.agent.tools.document_flow import DocumentFlowTool


class SubagentManager:
    """
    Manages background subagent execution.
    
    Subagents are lightweight agent instances that run in the background
    to handle specific tasks. They share the same LLM provider but have
    isolated context and a focused system prompt.
    """
    
    def __init__(
        self,
        provider: LLMProvider,
        workspace: Path,
        bus: MessageBus,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        brave_api_key: str | None = None,
        exec_config: "ExecToolConfig | None" = None,
        restrict_to_workspace: bool = False,
    ):
        from nanobot.config.schema import ExecToolConfig
        self.provider = provider
        self.workspace = workspace
        self.bus = bus
        self.model = model or provider.get_default_model()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.brave_api_key = brave_api_key
        self.exec_config = exec_config or ExecToolConfig()
        self.restrict_to_workspace = restrict_to_workspace
        self.company_loader = CompanyConfigLoader(workspace)
        self.exec_config = exec_config or ExecToolConfig()
        self.restrict_to_workspace = restrict_to_workspace
        self.company_loader = CompanyConfigLoader(workspace)
        # Note: ContextBuilder and SkillsLoader will be instantiated per-subagent 
        # to ensure isolation, or we pass specific agent_id to them.
        self.registry = WorkerRegistry(workspace)
        self._running_tasks: dict[str, asyncio.Task[None]] = {}
    
    async def spawn(
        self,
        task: str,
        label: str | None = None,
        origin_channel: str = "cli",
        origin_chat_id: str = "direct",
        post_id: str | None = None,
    ) -> str:
        """
        Spawn a subagent to execute a task in the background.
        
        Args:
            task: The task description for the subagent.
            label: Optional human-readable label for the task.
            origin_channel: The channel to announce results to.
            origin_chat_id: The chat ID to announce results to.
            post_id: Optional Company Post ID to define identity/tools/skills.
        
        Returns:
            Status message indicating the subagent was started.
        """
        task_id = str(uuid.uuid4())[:8]
        display_label = label or task[:30] + ("..." if len(task) > 30 else "")
        
        origin = {
            "channel": origin_channel,
            "chat_id": origin_chat_id,
        }
        
        # Register worker
        self.registry.register(task_id, post_id or "subagent", task)
        
        # Create background task
        bg_task = asyncio.create_task(
            self._run_subagent(task_id, task, display_label, origin, post_id)
        )
        self._running_tasks[task_id] = bg_task
        
        # Cleanup when done
        bg_task.add_done_callback(lambda _: self._running_tasks.pop(task_id, None))
        
        logger.info(f"Spawned subagent [{task_id}]: {display_label} (Post: {post_id})")
        return f"Subagent [{display_label}] started (id: {task_id}). I'll notify you when it completes."

    async def spawn_worker(
        self,
        post_id: str,
        task: str,
        monitor_channel: str = "cli",
        monitor_chat_id: str = "direct"
    ) -> str:
        """
        Spawn a worker based on a Company Post definition.
        
        Args:
            post_id: The ID of the post (e.g., "Post_Editor").
            task: The task to assign.
            monitor_channel: Channel to report back to.
            monitor_chat_id: Chat ID to report back to.
            
        Returns:
            Status string.
        """
        self.company_loader.load_all()
        if post_id not in self.company_loader.posts:
            return f"Error: Post '{post_id}' not found in company configuration."
            
        post = self.company_loader.posts[post_id]
        label = f"{post.title}: {task[:20]}..."
        
        return await self.spawn(
            task=task,
            label=label,
            origin_channel=monitor_channel,
            origin_chat_id=monitor_chat_id,
            post_id=post_id
        )
    
    async def _run_subagent(
        self,
        task_id: str,
        task: str,
        label: str,
        origin: dict[str, str],
        post_id: str | None = None,
    ) -> None:
        """Execute the subagent task and announce the result."""
        logger.info(f"Subagent [{task_id}] starting task: {label}")
        
        try:
            # Load Post config if available
            post = None
            if post_id:
                self.company_loader.load_all()
                post = self.company_loader.posts.get(post_id)
                if not post:
                    logger.error(f"Failed to load definition for Post '{post_id}' in subagent. Available posts: {list(self.company_loader.posts.keys())}")
            
            # ISOLATION: Instantiate components for THIS specific agent_id (task_id)
            # This ensures memory is at workspace/memory/workers/{task_id}/
            isolated_context = ContextBuilder(self.workspace, agent_id=task_id)
            isolated_skills = SkillsLoader(self.workspace)
            
            # Build subagent tools
            tools = ToolRegistry()
            self._register_tools(tools, post)
            
            # Build messages with subagent-specific prompt
            if post:
                # ISOLATION: Use ONLY the Post identity. 
                # This prompt is now strictly defined in ContextBuilder.get_agent_identity
                # and does NOT include the generic "You are nanobot" text.
                system_prompt = isolated_context.get_agent_identity(post_id)
                
                # Add skills
                if post.skills:
                    skills_content = isolated_skills.load_skills_for_context(post.skills)
                    if skills_content:
                        system_prompt += f"\n\n# Skills\n{skills_content}"
            else:
                # Fallback for ad-hoc tasks (legacy behaviour)
                system_prompt = self._build_subagent_prompt(task)
            
            messages: list[dict[str, Any]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task},
            ]
            
            # Run agent loop (limited iterations)
            max_iterations = 15
            iteration = 0
            final_result: str | None = None
            
            while iteration < max_iterations:
                iteration += 1
                
                response = await self.provider.chat(
                    messages=messages,
                    tools=tools.get_definitions(),
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                
                if response.has_tool_calls:
                    # Add assistant message with tool calls
                    tool_call_dicts = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments),
                            },
                        }
                        for tc in response.tool_calls
                    ]
                    messages.append({
                        "role": "assistant",
                        "content": response.content or "",
                        "tool_calls": tool_call_dicts,
                    })
                    
                    # Execute tools
                    for tool_call in response.tool_calls:
                        args_str = json.dumps(tool_call.arguments)
                        logger.debug(f"Subagent [{task_id}] executing: {tool_call.name} with arguments: {args_str}")
                        result = await tools.execute(tool_call.name, tool_call.arguments)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.name,
                            "content": result,
                        })
                else:
                    final_result = response.content
                    break
            
            if final_result is None:
                final_result = "Task completed but no final response was generated."
            
            logger.info(f"Subagent [{task_id}] completed successfully")
            self.registry.update_status(task_id, "completed", final_result)
            await self._announce_result(task_id, label, task, final_result, origin, "ok")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"Subagent [{task_id}] failed: {e}")
            self.registry.update_status(task_id, "failed", error_msg)
            await self._announce_result(task_id, label, task, error_msg, origin, "error")
    
    async def _announce_result(
        self,
        task_id: str,
        label: str,
        task: str,
        result: str,
        origin: dict[str, str],
        status: str,
    ) -> None:
        """Announce the subagent result to the main agent via the message bus."""
        status_text = "completed successfully" if status == "ok" else "failed"
        
        announce_content = f"""[Subagent '{label}' {status_text}]

Task: {task}

Result:
{result}

Summarize this naturally for the user. Keep it brief (1-2 sentences). Do not mention technical details like "subagent" or task IDs."""
        
        # Inject as system message to trigger main agent
        msg = InboundMessage(
            channel="system",
            sender_id="subagent",
            chat_id=f"{origin['channel']}:{origin['chat_id']}",
            content=announce_content,
        )
        
        await self.bus.publish_inbound(msg)
        logger.debug(f"Subagent [{task_id}] announced result to {origin['channel']}:{origin['chat_id']}")
    
    def _register_tools(self, registry: ToolRegistry, post: "Post | None") -> None:
        """Register tools for the subagent, optionally filtering by Post definition."""
        allowed_dir = self.workspace if self.restrict_to_workspace else None
        
        # Available tools map
        # Note: We create new instances for each subagent to ensure thread safety / config isolation if needed
        all_tools = {
            "read_file": lambda: ReadFileTool(allowed_dir=allowed_dir),
            "write_file": lambda: WriteFileTool(allowed_dir=allowed_dir),
            "edit_file": lambda: EditFileTool(allowed_dir=allowed_dir),
            "list_dir": lambda: ListDirTool(allowed_dir=allowed_dir),
            "exec": lambda: ExecTool(
                working_dir=str(self.workspace),
                timeout=self.exec_config.timeout,
                restrict_to_workspace=self.restrict_to_workspace,
            ),
            "web_search": lambda: WebSearchTool(api_key=self.brave_api_key),
            "web_fetch": lambda: WebFetchTool(),
            "document_flow": lambda: DocumentFlowTool(self.workspace),
        }
        
        # 1. Start with empty list
        tools_to_register = []
        is_restricted_post = (post is not None) and (len(post.tools) > 0)
        
        if is_restricted_post:
            logger.info(f"STRICT MODE: Restricting tools for '{post.title}'. Allowed: {post.tools}")
            for tool_name in post.tools:
                if tool_name in all_tools:
                    logger.info(f"  [+] Granting: {tool_name}")
                    tools_to_register.append(all_tools[tool_name]())
                else:
                    logger.warning(f"  [?] Unknown tool requested: {tool_name}")
        else:
            logger.warning("UNRESTRICTED MODE: No tools defined in Post (or no Post). Granting ALL tools.")
            for name, factory in all_tools.items():
                logger.info(f"  [+] Default granting: {name}")
                tools_to_register.append(factory())
                
        # 2. Register final list
        final_tool_names = []
        for tool in tools_to_register:
            registry.register(tool)
            final_tool_names.append(tool.name)
            
        # 3. Final Security Audit
        logger.info(f"FINAL AUDIT for '{post.title if post else 'Anonymous'}': {final_tool_names}")
        if post and post.title == "Post_Weather_Analyst" and "exec" in final_tool_names:
            logger.critical("SECURITY BREACH: 'exec' tool detected in 'Post_Weather_Analyst' registry! Forcing removal.")
            registry.unregister("exec")

    def _build_subagent_prompt(self, task: str) -> str:
        """Build a focused system prompt for the subagent."""
        from datetime import datetime
        import time as _time
        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        tz = _time.strftime("%Z") or "UTC"

        return f"""# Subagent

## Current Time
{now} ({tz})

You are a subagent spawned by the main agent to complete a specific task.

## Rules
1. Stay focused - complete only the assigned task, nothing else
2. Your final response will be reported back to the main agent
3. Do not initiate conversations or take on side tasks
4. Be concise but informative in your findings

## What You Can Do
- Read and write files in the workspace
- Execute shell commands
- Search the web and fetch web pages
- Complete the task thoroughly

## What You Cannot Do
- Send messages directly to users (no message tool available)
- Spawn other subagents
- Access the main agent's conversation history

## Workspace
Your workspace is at: {self.workspace}
Skills are available at: {self.workspace}/skills/ (read SKILL.md files as needed)

When you have completed the task, provide a clear summary of your findings or actions."""

    def get_running_count(self) -> int:
        """Return the number of currently running subagents."""
        return len(self._running_tasks)

