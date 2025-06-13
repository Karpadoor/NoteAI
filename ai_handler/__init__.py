import os
import json
import openai

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT") 
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# todo: allow passing more messages (dict - chain of messages)

def send_azure_openai_request(user_prompt, system_instruction, max_tokens=4096, temperature=0.7):
    try:
        client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return json.dumps(response.model_dump(), default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Failed to get response from Azure OpenAI."
        })