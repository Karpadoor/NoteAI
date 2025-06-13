import os
import json
import openai

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT") 
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

def send_azure_openai_request(messages, max_completion_tokens=100000, reasoning_effort="medium"):  
    """
    Sends a chat completion request to Azure OpenAI using the provided messages.

    Args:
        messages (list): List of message dictionaries, each with "role" ("system", "user", or "assistant") and "content".
        max_completion_tokens (int, optional): Maximum number of tokens allowed in the response. Defaults to 100000.
        reasoning_effort (str, optional): Level of reasoning effort for the model ("low", "medium", "high"). Defaults to "medium".

    Returns:
        str: JSON string containing the response from Azure OpenAI, or an error message if the request fails.
    """
    try:
        client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            reasoning_effort = reasoning_effort
        )

        return json.dumps(response.model_dump(), default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Failed to get response from Azure OpenAI."
        })