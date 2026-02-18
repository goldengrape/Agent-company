import asyncio
import re
from pathlib import Path
from typing import List

from loguru import logger

from nanobot.agent.subagent import SubagentManager
from nanobot.agent.worker_registry import WorkerRegistry
from nanobot.company.loader import CompanyConfigLoader
from nanobot.config.loader import load_config
from nanobot.bus.queue import MessageBus
from nanobot.config.loader import load_config
from nanobot.bus.queue import MessageBus
from nanobot.config.schema import Config

class CompanyManager:
    """
    Manages the high-level company operations:
    - Scans workspace/tasks for new tasks.
    - Spawns workers based on task type.
    - Monitors progress.
    """

    def __init__(self, workspace: Path, company_name: str | None = None):
        self.workspace = workspace
        self.company_name = company_name
        self.config = load_config()
        self.bus = MessageBus() # We might need a shared bus if we want to listen to events
        self.provider = self._make_provider(self.config)
        
        self.subagent_manager = SubagentManager(
            provider=self.provider,
            workspace=self.workspace,
            bus=self.bus,
            model=self.config.agents.defaults.model,
            temperature=self.config.agents.defaults.temperature,
            max_tokens=self.config.agents.defaults.max_tokens,
            brave_api_key=self.config.tools.web.search.api_key or None,
            exec_config=self.config.tools.exec,
            restrict_to_workspace=self.config.tools.restrict_to_workspace,
        )
        
        self.loader = CompanyConfigLoader(workspace, company_name)
        self.registry = WorkerRegistry(workspace)

    def _make_provider(self, config: Config):
        """Create LiteLLMProvider from config."""
        from nanobot.providers.litellm_provider import LiteLLMProvider
        from nanobot.providers.openai_codex_provider import OpenAICodexProvider

        model = config.agents.defaults.model
        provider_name = config.get_provider_name(model)
        p = config.get_provider(model)

        # OpenAI Codex (OAuth): don't route via LiteLLM
        if provider_name == "openai_codex" or model.startswith("openai-codex/"):
            return OpenAICodexProvider(default_model=model)

        return LiteLLMProvider(
            api_key=p.api_key if p else None,
            api_base=config.get_api_base(model),
            default_model=model,
            extra_headers=p.extra_headers if p else None,
            provider_name=provider_name,
        )

    async def run(self):
        """
        Main loop for the company manager.
        For now, this is a one-shot scan and execute.
        """
        logger.info(f"Company Manager started. Company: {self.company_name or 'Default'}")
        self.loader.load_all()
        
        # 1. Scan for tasks
        tasks_dir = self.workspace / "workspace" / "tasks"
        if not tasks_dir.exists():
            logger.warning(f"Tasks directory not found: {tasks_dir}")
            return

        task_files = list(tasks_dir.glob("TASK_*.md"))
        logger.info(f"Found {len(task_files)} task files.")

        for task_file in task_files:
            await self._process_task_file(task_file)

        # 2. Wait for background tasks to complete
        while self.subagent_manager.get_running_count() > 0:
            logger.info(f"Waiting for {self.subagent_manager.get_running_count()} workers to complete...")
            await asyncio.sleep(2)
        
        logger.info("All tasks completed.")

    async def _process_task_file(self, task_file: Path):
        filename = task_file.name
        content = task_file.read_text(encoding="utf-8")
        
        # Match task against routes
        matched_route = None
        for route in self.loader.routes:
            if re.match(route.pattern, filename):
                matched_route = route
                break
        
        if not matched_route:
            logger.info(f"Skipping task {filename}: No matching route found.")
            return

        post_id = matched_route.post_id


        # Check if already assigned (simple check)
        # TODO: Implement proper state tracking for tasks
        
        task_prompt = matched_route.context_template.format(
            filename=filename,
            content=content
        )
        
        logger.info(f"Assigning {filename} to {post_id}...")
        
        response = await self.subagent_manager.spawn_worker(
            post_id=post_id,
            task=task_prompt,
            monitor_channel="cli",
            monitor_chat_id="direct"
        )
        logger.info(f"Spawn result: {response}")
