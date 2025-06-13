import azure.functions as func
import json
import logging
import project_handler
import memory_handler
import ai_handler

APPLICATION_JSON = "application/json"

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get Project ID and Thread ID from route parameters
        project_id = req.route_params.get("projectId")

        # Use the shared validation and existence check (handles all validation)
        try:
            project_handler.check_project_exists(project_id)
        except ValueError as ve:
            return func.HttpResponse(
                json.dumps({"error": str(ve)}),
                status_code=400 if "not a valid GUID" in str(ve) or "must be provided" in str(ve) else 404,
                mimetype=APPLICATION_JSON
            )

        # Parse request body for message content
        try:
            req_body = req.get_json()
            message_content = req_body.get("Message")
        except Exception:
            message_content = None

        if not message_content:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'Message' in request body."}),
                status_code=400,
                mimetype=APPLICATION_JSON
            )

        try:
            system_prompt = ai_handler.get_system_prompt("train")
            memory = memory_handler.get_memory(project_id)
            if memory:
                system_prompt = f"{system_prompt}\n\nMemory JSON:\n{memory}"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_content}
            ]

            response_json = ai_handler.send_azure_openai_request(messages=messages)
            if isinstance(response_json, str):
                response_json = json.loads(response_json)

            logging.info(f"Response prompt tokens: {response_json.get('prompt_tokens')}")
            logging.info(f"Response completion tokens: {response_json.get('completion_tokens')}")
            logging.info(f"Reasoning tokens: {response_json.get('reasoning_tokens')}")

            memory_handler.set_memory(project_id, json.dumps(response_json.get("content")))

            return func.HttpResponse(
                status_code=200,
                mimetype=APPLICATION_JSON
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": f"Failed to process chat: {str(e)}"}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype=APPLICATION_JSON
        )