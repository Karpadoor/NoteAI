import azure.functions as func
import os
import json
import pyodbc
import uuid

APPLICATION_JSON = "application/json"

def main(NewThread: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get Project ID from route parameters
        project_id = NewThread.route_params.get("projectId")
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
            # Validate if project exists
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

            # Insert new thread and get the new ID
            insert_query = """
                INSERT INTO [NoteAI].[Threads] ([Project])
                OUTPUT INSERTED.ID
                VALUES (?)
            """
            cursor.execute(insert_query, (project_id,))
            new_id_row = cursor.fetchone()
            conn.commit()

        if new_id_row:
            new_id = new_id_row[0]
            return func.HttpResponse(
                json.dumps({"Thread": new_id}),
                status_code=201,
                mimetype=APPLICATION_JSON
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to insert new thread."}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype=APPLICATION_JSON
        )