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

        # Get connection string using the shared function
        conn_str = project_handler.get_sql_connection_string()

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            # Query messages for the given thread
            query = """
                SELECT [Message], [Role], [SYS_INSERT]
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
            for item in results:
                if 'SYS_INSERT' in item:
                    value = item['SYS_INSERT']
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    item['Timestamp'] = value
                    del item['SYS_INSERT']

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