"""CLI entry point - streams the agent's answer to the terminal."""
import asyncio
import sys

# Windows consoles default to cp1252 - the agents love emojis, so force UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Custom_Agents.all_agent import run_main_agent_stream


async def stream_to_terminal(user_input: str):
    async for event in run_main_agent_stream(user_input):
        if event["type"] == "token":
            print(event["text"], end="", flush=True)
        elif event["type"] == "agent":
            print(f"\n[agent] {event['name']}\n", flush=True)
        elif event["type"] == "tool":
            print(f"\n[tool] {event['name']}...\n", flush=True)
        elif event["type"] == "error":
            print(f"\n[error] {event['message']}", flush=True)
        elif event["type"] == "done":
            print("\n", flush=True)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "give me a recipe for omelette"
    asyncio.run(stream_to_terminal(query))
