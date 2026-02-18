import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.getcwd())

from nanobot.agent.subagent import SubagentManager
from nanobot.providers.litellm_provider import LiteLLMProvider
from nanobot.bus.queue import MessageBus
from nanobot.config.loader import load_config
from nanobot.agent.tools.document_flow import DocumentFlowTool

async def main():
    print("Loading config...")
    config = load_config()
    workspace = Path(os.getcwd())
    
    # Setup dependencies
    bus = MessageBus()
    provider = LiteLLMProvider(
        api_key=config.providers.gemini.api_key,
        default_model=config.agents.defaults.model
    )
    
    # Manager
    manager = SubagentManager(
        provider=provider,
        workspace=workspace,
        bus=bus,
        model=config.agents.defaults.model
    )
    
    print("Creating Task Order...")
    doc_flow = DocumentFlowTool(workspace)
    task_result = await doc_flow.execute(
        "create", 
        doc_type="Doc_Task_Weather", 
        title="Live_Test_China_Weather",
        metadata={"Cities": "Beijing, Shanghai, Shenzhen"}
    )
    print(f"Task Created: {task_result}")
    
    print("Spawning Weather Analyst...")
    spawn_result = await manager.spawn_worker(
        post_id="Post_Weather_Analyst",
        task="Check weather for Beijing, Shanghai, Shenzhen for the next 7 days and report back.",
        monitor_channel="cli",
        monitor_chat_id="direct"
    )
    print(f"Spawn Result: {spawn_result}")
    
    print("Waiting for worker completion (max 120s)...")
    # In a real scenario, we'd listen to the bus. Here we check the task registry.
    
    for _ in range(24): # Poll every 5s for 120s
        await asyncio.sleep(5)
        # Check running tasks
        running = manager.get_running_count()
        print(f"Running subagents: {running}")
        if running == 0:
            break
            
    print("Done. Checking results...")
    # Check if report exists
    reports = list((workspace / "workspace" / "reports").glob("REPORT_WEATHER_*.md"))
    if reports:
        latest_report = sorted(reports, key=lambda p: p.stat().st_mtime)[-1]
        print(f"Found report: {latest_report}")
        print("--- Report Content ---")
        print(latest_report.read_text(encoding="utf-8")[:500] + "...")
    else:
        print("No report found. Check logs for errors (likely missing Brave Search API Key).")

if __name__ == "__main__":
    asyncio.run(main())
