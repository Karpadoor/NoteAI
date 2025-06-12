import azure.functions as func
import json
import pyodbc
from project_handler import get_sql_connection_string
from memory_handler import set_memory

APPLICATION_JSON = "application/json"

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse request body
        req_body = req.get_json()
        name = req_body.get("Name")
        if not name:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'Name' in request body."}),
                status_code=400,
                mimetype=APPLICATION_JSON
            )

        # Get connection string using the shared function
        conn_str = get_sql_connection_string()

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
            # Set the new project ID in memory
            set_memory(new_id, '{}')
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