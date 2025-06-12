import azure.functions as func
import json
import pyodbc
import project_handler

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

        # Get connection string using the shared function
        conn_str = project_handler.get_sql_connection_string()

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            # Check if thread exists for the given project
            cursor.execute(
                "SELECT 1 FROM [NoteAI].[Threads] WHERE ID = ? AND [Project] = ? AND SYS_DELETED IS NULL",
                (thread_id, project_id)
            )
            if not cursor.fetchone():
                return func.HttpResponse(
                    json.dumps({"error": "Thread does not exist for the given project."}),
                    status_code=404,
                    mimetype=APPLICATION_JSON
                )

            # Insert new message
            insert_query = """
                INSERT INTO [NoteAI].[Messages] ([Thread], [Message], [Role])
                OUTPUT INSERTED.Thread, INSERTED.Message, INSERTED.Role, INSERTED.SYS_INSERT
                VALUES (?, ?, ?)
            """
            cursor.execute(insert_query, (thread_id, message_content, "USER"))
            inserted_row = cursor.fetchone()
            conn.commit()

        if inserted_row:
            columns = [column[0] for column in cursor.description]
            result = dict(zip(columns, inserted_row))
            return func.HttpResponse(
                json.dumps(result, default=str, indent=2),
                status_code=201,
                mimetype=APPLICATION_JSON
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to insert new message."}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype=APPLICATION_JSON
        )