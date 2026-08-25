from openai import AsyncAzureOpenAI
import os
from agents import set_default_openai_client, set_tracing_disabled


def get_agent_client():
    """Create and return a single AsyncAzureOpenAI client and model name.

    This centralizes creation so callers reuse the same client/config.
    """
    agent_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_GPT_4O_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_GPT_4O_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_GPT_4O_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_GPT_4O_DEPLOYMENT_NAME"),
    )

    model_name = os.getenv("AZURE_OPENAI_GPT_4O_DEPLOYMENT_NAME")

    # set global defaults used by your agents
    set_default_openai_client(agent_client)
    set_tracing_disabled(True)

    return agent_client, model_name