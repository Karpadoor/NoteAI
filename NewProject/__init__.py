import azure.functions as func
import os
import json
import pyodbc

APPLICATION_JSON = "application/json"

def main(NewProject: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse request body
        req_body = NewProject.get_json()
        name = req_body.get("Name")
        if not name:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'Name' in request body."}),
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

        # Insert new project and get the new ID
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO [NoteAI].[Projects] (Name)
                OUTPUT INSERTED.ID
                VALUES (?)
            """
            cursor.execute(insert_query, (name,))
            new_id_row = cursor.fetchone()
            conn.commit()

        if new_id_row:
            new_id = new_id_row[0]
            return func.HttpResponse(
                json.dumps({"Project": new_id}),
                status_code=201,
                mimetype=APPLICATION_JSON
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to insert new project."}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype=APPLICATION_JSON
        )