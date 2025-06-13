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
        name = req_body.get("name")
        purpose = req_body.get("purpose")
        stakeholders = req_body.get("stakeholders")
        components = req_body.get("components")
        lifecycle = req_body.get("lifecycle")
        limitations = req_body.get("limitations")

        # Validate required fields
        if not all([name, purpose, stakeholders, components, lifecycle, limitations]):
            return func.HttpResponse(
                json.dumps({"error": "Missing one or more required fields: name, purpose, stakeholders, components, lifecycle, limitations."}),
                status_code=400,
                mimetype=APPLICATION_JSON
            )

        # Create initial_memory
        initial_memory = {
            "project": {
                "name": name,
                "purpose": purpose,
                "stakeholders": stakeholders,
                "components": components,
                "lifecycle": lifecycle,
                "limitations": limitations
            }
        }

        # Get connection string using the shared function
        conn_str = get_sql_connection_string()

        # Insert new project and get the new ID
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO [NoteAI].[Projects] 
                    (Name, Purpose, Stakeholders, Components, Lifecycle, Limitations)
                OUTPUT INSERTED.ID
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (name, purpose, stakeholders, components, lifecycle, limitations))
            new_project_id_row = cursor.fetchone()
            conn.commit()

        if new_project_id_row:
            new_id = new_project_id_row[0]
            set_memory(new_id, initial_memory)
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