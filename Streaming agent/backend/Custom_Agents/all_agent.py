import os
from typing import AsyncGenerator, Dict, Any

from openai.types.responses import ResponseTextDeltaEvent

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    handoff,
    Runner,
)

from utils.helpers import load_prompt
from utils.agent_client import get_agent_client

from dotenv import load_dotenv
load_dotenv()

from Custom_Agents.Custom_tools.email_generator_tool import email_sender
from Custom_Agents.Custom_tools.cook_tool import get_recipe

from Custom_loggers import logger


def build_main_agent():
    """Build the main agent (with its handoffs) and return it."""
    agent_client, model_name = get_agent_client()

    instructions = load_prompt("prompts/main_agent_instruction.md")

    email_agent = get_email_generator(agent_client, model_name)
    cook_agent = get_cook_agent(agent_client, model_name)

    main_agent = Agent(
        name="Main Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model=model_name,
            openai_client=agent_client,
        ),
        handoffs=[
            handoff(email_agent),
            handoff(cook_agent),
        ],
    )
    return main_agent


async def run_main_agent_stream(user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Run the main agent and *yield* events as they happen.

    Every yielded item is a dict: {"type": ..., ...}
      - {"type": "agent",  "name": "cook Agent"}      -> agent started / handoff
      - {"type": "tool",   "name": "get_recipe"}      -> tool call started
      - {"type": "tool_output", "name": ..., "output": ...}
      - {"type": "token",  "text": "..."}             -> streamed text delta
      - {"type": "done",   "output": "<final text>"}
      - {"type": "error",  "message": "..."}
    """
    main_agent = build_main_agent()
    logger.info(f"Streaming run started for input: {user_input!r}")

    final_text = []

    try:
        result = Runner.run_streamed(main_agent, input=user_input)

        async for event in result.stream_events():
            # 1. raw token deltas from the model
            if event.type == "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent) and event.data.delta:
                    final_text.append(event.data.delta)
                    yield {"type": "token", "text": event.data.delta}

            # 2. which agent is currently running (handoffs show up here)
            elif event.type == "agent_updated_stream_event":
                logger.info(f"Agent switched to: {event.new_agent.name}")
                yield {"type": "agent", "name": event.new_agent.name}

            # 3. tool calls and their outputs
            elif event.type == "run_item_stream_event":
                item = event.item
                if item.type == "tool_call_item":
                    name = getattr(item.raw_item, "name", "tool")
                    logger.info(f"Tool called: {name}")
                    yield {"type": "tool", "name": name}
                elif item.type == "tool_call_output_item":
                    yield {
                        "type": "tool_output",
                        "name": "tool",
                        "output": str(item.output),
                    }

        output = result.final_output or "".join(final_text)
        logger.info("Streaming run finished")
        yield {"type": "done", "output": output}

    except Exception as exc:  # surface failures to the UI instead of dying silently
        logger.exception("Streaming run failed")
        yield {"type": "error", "message": str(exc)}


def get_email_generator(agent_client, model_name):
    instructions = load_prompt("prompts/email_generator.md")

    return Agent(
        name="email Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model=model_name,
            openai_client=agent_client,
        ),
        tools=[email_sender],
    )


def get_cook_agent(agent_client, model_name):
    instructions = load_prompt("prompts/cook.md")

    return Agent(
        name="cook Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model=model_name,
            openai_client=agent_client,
        ),
        tools=[get_recipe],
    )
