import azure.functions as func
import json
import project_handler
import chat_handler
import memory_handler
import ai_handler

APPLICATION_JSON = "application/json"

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get Project ID and Thread ID from route parameters
        project_id = req.route_params.get("projectId")
        thread_id = req.route_params.get("threadId")

        # Use the shared validation and existence check (handles all validation)
        try:
            project_handler.check_thread_exists(thread_id, project_id)
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

        # Use the shared validation and existence check (handles all validation)
        try:
            project_handler.check_thread_exists(thread_id, project_id)
        except ValueError as ve:
            return func.HttpResponse(
                json.dumps({"error": str(ve)}),
                status_code=400 if "not a valid GUID" in str(ve) or "must be provided" in str(ve) else 404,
                mimetype=APPLICATION_JSON
            )

        try:
            system_prompt = ai_handler.get_system_prompt("Ask")
            memory = memory_handler.get_memory(project_id)
            if memory:
                system_prompt = f"{system_prompt}\n\nMemory JSON:\n{memory}"
            messages = chat_handler.get_messages(thread_id)
            messages.insert(0, {"role": "system", "content": system_prompt})

            chat_handler.add_message(
                thread_id=thread_id,
                role="system",
                source="ask",
                content=system_prompt
            )

            chat_handler.add_message(
                thread_id=thread_id,
                role="user",
                source="ask",
                content=message_content
            )

            response_json = ai_handler.send_azure_openai_request(messages=messages)
            # Ensure response_json is a dict
            if isinstance(response_json, str):
                response_json = json.loads(response_json)

            chat_handler.add_message(
                thread_id=thread_id,
                role="assistant",
                source="ask",
                content=response_json.get("content"),
                model=response_json.get("model"),
                prompt_tokens=response_json.get("prompt_tokens"),
                completion_tokens=response_json.get("completion_tokens"),
                reasoning_tokens=response_json.get("reasoning_tokens")
            )

            return func.HttpResponse(
                json.dumps({"response": response_json}),
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