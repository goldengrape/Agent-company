import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

from nanobot.config.loader import load_config
from nanobot.agent.tools.web import WebSearchTool

async def main():
    print("Loading config...")
    config = load_config()
    
    api_key = config.tools.web.search.api_key
    print(f"Brave API Key present: {bool(api_key)}")
    print(f"Key preview: {api_key[:5]}...")
    
    if not api_key or "YOUR_" in api_key:
        print("Error: Invalid API key for Brave Search.")
        return

    print("Executing Web Search...")
    tool = WebSearchTool(api_key=api_key)
    
    try:
        result = await tool.execute(query="Shanghai weather forecast")
        print(f"\nResult:\n{result[:500]}...")
        if "Error" in result:
             print("\nFAILED: Search returned error.")
        else:
             print("\nSUCCESS: Brave Search API is working!")
    except Exception as e:
        print(f"\nERROR: Failed to connect to Brave Search.\n{e}")

if __name__ == "__main__":
    asyncio.run(main())
