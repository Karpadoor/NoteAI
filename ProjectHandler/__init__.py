import logging
import os
import pyodbc

def get_sql_connection_string():
    """
    Retrieve the SQL connection string from environment variables.
    Raises an exception if not set.
    """
    conn_str = os.environ.get("SQL_CONNECTION_STRING")
    if not conn_str:
        logging.error("SQL_CONNECTION_STRING environment variable not set.")
        raise EnvironmentError("SQL_CONNECTION_STRING environment variable not set.")
    return conn_str

def check_project_exists(project_id):
    """
    Check if a project exists in the database.
    Raises an exception if the connection string is missing or if the project does not exist.
    """
    conn_str = get_sql_connection_string()
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM NoteAI.Projects WHERE [Id] = ?"
            cursor.execute(query, (project_id,))
            count = cursor.fetchone()[0]
            if count == 0:
                raise ValueError(f"Project with ID {project_id} does not exist.")
    except Exception as e:
        logging.error(f"Error checking project existence: {e}")
        raise e

def check_thread_exists(thread_id, project_id):
    """
    Check if a thread exists in the database for a given project.
    Raises an exception if the connection string is missing or if the thread does not exist.
    """
    conn_str = get_sql_connection_string()
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM NoteAI.Threads WHERE [Id] = ? AND [Project] = ?"
            cursor.execute(query, (thread_id, project_id))
            count = cursor.fetchone()[0]
            if count == 0:
                raise ValueError(f"Thread with ID {thread_id} does not exist in project {project_id}.")
    except Exception as e:
        logging.error(f"Error checking thread existence: {e}")
        raise e