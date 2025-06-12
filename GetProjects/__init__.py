import azure.functions as func
import json
import pyodbc
from ProjectHandler import get_sql_connection_string

APPLICATION_JSON = "application/json"

def main(GetProjects: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get connection string using the shared function
        try:
            conn_str = get_sql_connection_string()
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500,
                mimetype=APPLICATION_JSON
            )

        # Connect to SQL Server
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = """
                SELECT ID, Name, SYS_INSERT
                FROM [NoteAI].[Projects]
                WHERE SYS_DELETED IS NULL
                ORDER BY [SYS_INSERT] ASC
            """
            cursor.execute(query)
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