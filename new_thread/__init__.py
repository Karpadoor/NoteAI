import azure.functions as func
import json
import pyodbc
import project_handler

APPLICATION_JSON = "application/json"

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get Project ID from route parameters
        project_id = req.route_params.get("projectId")

        # Use shared validation and existence check
        try:
            project_handler.check_project_exists(project_id)
        except ValueError as ve:
            return func.HttpResponse(
                json.dumps({"error": str(ve)}),
                status_code=400 if "not a valid GUID" in str(ve) or "must be provided" in str(ve) else 404,
                mimetype=APPLICATION_JSON
            )
        
        # Get connection string using the shared function
        conn_str = project_handler.get_sql_connection_string()

        # Insert new thread and get the new ID
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
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