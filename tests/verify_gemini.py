import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

from nanobot.config.loader import load_config
from nanobot.providers.litellm_provider import LiteLLMProvider

async def main():
    print("Loading config...")
    config = load_config()
    
    provider_name = "gemini"
    api_key = config.providers.gemini.api_key
    model = config.agents.defaults.model
    
    print(f"Provider: {provider_name}")
    print(f"Model: {model}")
    print(f"API Key present: {bool(api_key)}")
    
    if not api_key:
        print("Error: No API key found for Gemini.")
        return

    print("Connecting to LLM (LiteLLM)...")
    provider = LiteLLMProvider(
        api_key=api_key,
        default_model=model
    )
    
    messages = [{"role": "user", "content": "Say 'Hello from Gemini' if you can read this."}]
    
    try:
        response = await provider.chat(messages=messages, model=model)
        print(f"\nResponse: {response.content}")
        print("\nSUCCESS: Gemini API is working!")
    except Exception as e:
        print(f"\nERROR: Failed to connect to Gemini.\n{e}")

if __name__ == "__main__":
    asyncio.run(main())
