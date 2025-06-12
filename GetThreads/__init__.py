import azure.functions as func
import os
import json
import pyodbc
import uuid

APPLICATION_JSON = "application/json"

def main(GetThreads: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get Project ID from route parameters
        project_id = GetThreads.route_params.get("projectId")
        if not project_id:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'projectId' in route parameters."}),
                status_code=400,
                mimetype=APPLICATION_JSON
            )

        # Validate project_id is a GUID
        try:
            uuid.UUID(str(project_id))
        except (ValueError, TypeError):
            return func.HttpResponse(
                json.dumps({"error": "'projectId' must be a valid GUID."}),
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
            # Check if project exists
            cursor.execute(
                "SELECT 1 FROM [NoteAI].[Projects] WHERE ID = ? AND SYS_DELETED IS NULL",
                (project_id,)
            )
            if not cursor.fetchone():
                return func.HttpResponse(
                    json.dumps({"error": "Project does not exist."}),
                    status_code=404,
                    mimetype=APPLICATION_JSON
                )

            # Query threads for the given project
            query = """
                SELECT ID, Name, SYS_INSERT
                FROM [NoteAI].[Threads]
                WHERE [Project] = ? AND SYS_DELETED IS NULL
                ORDER BY [SYS_INSERT] ASC
            """
            cursor.execute(query, (project_id,))
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