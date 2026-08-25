import os
import json
from agents import(
    Agent,
    HandoffInputData,
    OpenAIChatCompletionsModel,
    handoff,
    set_default_openai_client,
    function_tool,
    set_tracing_disabled,
    Runner,
)
from utils.helpers import load_prompt
from utils.agent_client import get_agent_client

from dotenv import load_dotenv
load_dotenv()

from Custom_Agents.Custom_tools.email_generator_tool import email_sender
from Custom_Agents.Custom_tools.cook_tool import get_recipe

from Custom_loggers import logger

# logger.info("Hello World")
# num = 1234
# logger.info(f"Hello World-{num}")
# test_details = {
#     "sample" : "value1",
#     "sample2" : {
#         'sub-sample1' : 12345,
#     }
# }
# logger.info(json.dumps(test_details, indent=2))

async def run_main_agent(user_input: str):
    # single client reused across agents
    agent_client, model_name = get_agent_client()

    instructions = load_prompt("prompts/main_agent_instruction.md")

    # create agents using the same client
    email_agent = get_email_generator(agent_client, model_name)
    cook_agent = get_cook_agent(agent_client, model_name)

    main_agent = Agent(
        name = "Main Agent",
        instructions = instructions,
        model = OpenAIChatCompletionsModel(
            model = model_name,
            openai_client = agent_client,
        ),
        handoffs =[
            handoff(email_agent),
            handoff(cook_agent),
        ],
    )

    result = await Runner.run(main_agent, input=user_input)
    print(result.final_output)


def get_email_generator(agent_client, model_name):
    instructions = load_prompt("prompts/email_generator.md")

    email_agent = Agent(
        name = "email Agent",
        instructions = instructions,
        model = OpenAIChatCompletionsModel(
            model = model_name,
            openai_client = agent_client,
        ),
        tools = [email_sender]
    )
    return email_agent



def get_cook_agent(agent_client, model_name):
    # agent_client, model_name = get_agent_client()
    instructions = load_prompt("prompts/cook.md")

    cook_agent = Agent(
        name = "cook Agent",
        instructions = instructions,
        model = OpenAIChatCompletionsModel(
            model = model_name,
            openai_client = agent_client,
        ),
        tools = [get_recipe]
    )
    return cook_agent

