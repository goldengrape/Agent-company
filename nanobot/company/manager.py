import asyncio
import re
from pathlib import Path
from typing import List

from loguru import logger

from nanobot.agent.subagent import SubagentManager
from nanobot.agent.worker_registry import WorkerRegistry
from nanobot.company.loader import CompanyConfigLoader
from nanobot.config.loader import load_config
from nanobot.config.schema import Config
from nanobot.agent.memory import MemoryStore
from nanobot.bus.queue import MessageBus

class CompanyManager:
    """
    Manages the high-level company operations:
    - Scans workspace/tasks for new tasks.
    - Spawns workers based on task type.
    - Monitors progress.
    """

    def __init__(self, workspace: Path, company_name: str | None = None, task_input: str | None = None, company_path: str | None = None, output_path: Path | None = None):
        self.workspace = workspace
        self.company_name = company_name
        self.task_input = task_input
        self.company_path = company_path
        self.output_path = output_path
        self.config = load_config()
        self.bus = MessageBus() # We might need a shared bus if we want to listen to events
        self.provider = self._make_provider(self.config)
        
        # Track spawned task IDs to collect results later
        self._spawned_task_ids: List[str] = []
        
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
            company_name=self.company_name,
        )
        # Propagate output_dir to SubagentManager so all sub-workers receive it
        self.subagent_manager.output_dir = self._resolve_output_dir()
        
        self.loader = CompanyConfigLoader(workspace, company_name, company_path=company_path)
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

    def _resolve_output_dir(self) -> str:
        """Resolve the output directory path string for template injection."""
        if self.output_path:
            return str(self.output_path)
        # Default: workspace/deliverables/
        default_dir = self.workspace / "workspace" / "deliverables"
        default_dir.mkdir(parents=True, exist_ok=True)
        return str(default_dir)

    def _extract_task_id_from_response(self, response: str) -> str | None:
        """Extract task_id from spawn response string like 'Subagent [...] started (id: abc12345)'."""
        match = re.search(r'\(id:\s*([a-f0-9]+)\)', response)
        return match.group(1) if match else None

    async def run(self):
        """
        Main loop for the company manager.
        If task_input is provided, process it directly.
        Otherwise, scan workspace/tasks for TASK_*.md files.
        """
        logger.info(f"Company Manager started. Company: {self.company_name or 'Default'}")
        self.loader.load_all()

        # If task_input is provided via CLI --task, process it directly
        if self.task_input:
            logger.info("Processing task from CLI --task input.")
            await self._process_direct_task(self.task_input)
        else:
            # Scan for tasks in workspace/tasks
            tasks_dir = self.workspace / "workspace" / "tasks"
            if not tasks_dir.exists():
                logger.warning(f"Tasks directory not found: {tasks_dir}")
                return

            task_files = list(tasks_dir.glob("TASK_*.md"))
            logger.info(f"Found {len(task_files)} task files.")

            for task_file in task_files:
                await self._process_task_file(task_file)

        # Wait for background tasks to complete
        while self.subagent_manager.get_running_count() > 0:
            logger.info(f"Waiting for {self.subagent_manager.get_running_count()} workers to complete...")
            await asyncio.sleep(2)
        
        logger.info("All tasks completed.")

        # Collect and output results
        self._output_results()

        # Cleanup worker records and memory
        self._cleanup_workers()

    def _output_results(self):
        """Collect results from all spawned workers and output them."""
        if not self._spawned_task_ids:
            return

        # Reload registry to get latest results
        self.registry = WorkerRegistry(self.workspace)

        results_parts: List[str] = []
        for task_id in self._spawned_task_ids:
            worker = self.registry.get(task_id)
            if worker and worker.result:
                results_parts.append(worker.result)
            else:
                results_parts.append(f"[Worker {task_id}]: No result available (status: {worker.status if worker else 'unknown'})")

        combined_result = "\n\n---\n\n".join(results_parts)

        # Always print to console
        print("\n" + "=" * 60)
        print("📋 Company Run Results")
        print("=" * 60)
        print(combined_result)
        print("=" * 60)

        # Print output directory info
        output_dir = self._resolve_output_dir()
        print(f"\n📁 Output directory: {output_dir}")

    def _cleanup_workers(self):
        """Cleanup worker registry and memory for spawned tasks."""
        if not self._spawned_task_ids:
            return

        logger.info(f"Cleaning up {len(self._spawned_task_ids)} workers...")
        for task_id in self._spawned_task_ids:
            # Unregister from workers.json
            self.registry.unregister(task_id)
            # Clear worker-specific memory directory
            memory = MemoryStore(self.workspace, agent_id=task_id)
            memory.clear()
        
        logger.info("Cleanup completed.")

    async def _process_direct_task(self, content: str):
        """Process a task provided directly via CLI --task argument."""
        if not self.loader.default_post:
            logger.warning("No default post configured. Cannot process direct task input.")
            return

        post_id = self.loader.default_post
        output_dir = self._resolve_output_dir()
        template = self.loader.default_task_template or "Task:\n{content}"
        task_prompt = template.format(
            filename="CLI_INPUT",
            content=content,
            task=content,
            output_dir=output_dir,
        )
        logger.info(f"Assigning CLI task to {post_id}...")

        response = await self.subagent_manager.spawn_worker(
            post_id=post_id,
            task=task_prompt,
            monitor_channel="cli",
            monitor_chat_id="direct"
        )
        logger.info(f"Spawn result: {response}")

        # Track task_id for result collection
        task_id = self._extract_task_id_from_response(response)
        if task_id:
            self._spawned_task_ids.append(task_id)

    async def _process_task_file(self, task_file: Path):
        filename = task_file.name
        content = task_file.read_text(encoding="utf-8")
        
        # Match task against routes
        if self.loader.default_post:
            post_id = self.loader.default_post
            output_dir = self._resolve_output_dir()
            template = self.loader.default_task_template or "Task File: {filename}\nContent:\n{content}"
            task_prompt = template.format(
                filename=filename,
                content=content,
                output_dir=output_dir,
            )
            logger.info(f"Using default post {post_id} for {filename}")
        else:
            logger.info(f"Skipping task {filename}: No default post found.")
            return
        
        logger.info(f"Assigning {filename} to {post_id}...")
        
        response = await self.subagent_manager.spawn_worker(
            post_id=post_id,
            task=task_prompt,
            monitor_channel="cli",
            monitor_chat_id="direct"
        )
        logger.info(f"Spawn result: {response}")

        # Track task_id for result collection
        task_id = self._extract_task_id_from_response(response)
        if task_id:
            self._spawned_task_ids.append(task_id)
