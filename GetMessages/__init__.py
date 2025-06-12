import azure.functions as func
import os
import json
import pyodbc
import uuid

APPLICATION_JSON = "application/json"

def main(GetMessages: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get Project ID and Thread ID from route parameters
        project_id = GetMessages.route_params.get("projectId")
        thread_id = GetMessages.route_params.get("threadId")
        if not project_id or not thread_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'projectId' or 'threadId' in route parameters."}),
                status_code=400,
                mimetype=APPLICATION_JSON
            )

        # Validate GUIDs
        try:
            uuid.UUID(str(project_id))
            uuid.UUID(str(thread_id))
        except (ValueError, TypeError):
            return func.HttpResponse(
                json.dumps({"error": "'projectId' and 'threadId' must be valid GUIDs."}),
                status_code=400,
                mimetype=APPLICATION_JSON
            )

        # Get connection string from environment variable
        conn_str = os.environ.get("SQL_CONNECTION_STRING")
        if not conn_str:
            return func.HttpResponse(
                json.dumps({"error": "SQL_CONNECTION_STRING not set."}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

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

            # Query messages for the given thread
            query = """
                SELECT [Thread], [Message], [Role], [SYS_INSERT]
                FROM [NoteAI].[Messages]
                WHERE [Thread] = ?
                ORDER BY [SYS_INSERT] ASC
            """
            cursor.execute(query, (thread_id,))
            columns = [column[0] for column in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

        return func.HttpResponse(
            json.dumps(results, default=str, indent=2),
            status_code=200,
            mimetype=APPLICATION_JSON
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype=APPLICATION_JSON
        )