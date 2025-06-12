import azure.functions as func
import json
import pyodbc
import ProjectHandler

APPLICATION_JSON = "application/json"

def main(GetThreads: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get Project ID from route parameters
        project_id = GetThreads.route_params.get("projectId")

        # Use shared validation and existence check
        try:
            ProjectHandler.check_project_exists(project_id)
        except ValueError as ve:
            return func.HttpResponse(
                json.dumps({"error": str(ve)}),
                status_code=400 if "not a valid GUID" in str(ve) or "must be provided" in str(ve) else 404,
                mimetype=APPLICATION_JSON
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

        # Get connection string using the shared function
        try:
            conn_str = ProjectHandler.get_sql_connection_string()
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
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