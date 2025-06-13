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
        str: JSON string containing the relevant response fields from Azure OpenAI, or an error message if the request fails.
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
            reasoning_effort=reasoning_effort
        )

        result = {
            "content": response.choices[0].message.content if response.choices and response.choices[0].message else None,
            "model": getattr(response, "model", None),
            "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
            "completion_tokens": getattr(response.usage, "completion_tokens", None),
            "reasoning_tokens": getattr(response.usage.completion_tokens_details, "reasoning_tokens", None)
        }

        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Failed to get response from Azure OpenAI."
        })
    
def get_system_prompt(system_prompt):
    """
    Reads a prompt from a .txt file in the root/system_prompts/ directory and returns it as plain text.

    Args:
        system_prompt (str): The filename (without extension) of the prompt to load.

    Returns:
        str: The contents of the prompt file as plain text.

    Raises:
        FileNotFoundError: If the specified prompt file does not exist.
        OSError: If there is an error reading the prompt file.
    """
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "system_prompts",
        f"{system_prompt}.txt"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file '{prompt_path}' not found.")
    except Exception as e:
        raise OSError(f"Error reading prompt file: {e}")