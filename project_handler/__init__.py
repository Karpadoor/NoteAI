import logging
import os
import pyodbc
import uuid

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
    Raises an exception if the connection string is missing, if the project_id is not provided or not a valid GUID,
    or if the project does not exist.
    """
    if not project_id or not str(project_id).strip():
        raise ValueError("project_id must be provided and not empty.")
    try:
        uuid.UUID(str(project_id))
    except (ValueError, TypeError):
        raise ValueError(f"project_id '{project_id}' is not a valid GUID.")

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

def check_thread_exists(thread_id, project_id=None):
    """
    Check if a thread exists in the database.
    If project_id is provided, check if the thread exists for the given project.
    If project_id is not provided, check if the thread exists in any project.
    Raises an exception if the connection string is missing, if the thread_id is not provided or not a valid GUID,
    or if the thread does not exist.
    """
    if not thread_id or not str(thread_id).strip():
        raise ValueError("thread_id must be provided and not empty.")
    try:
        uuid.UUID(str(thread_id))
    except (ValueError, TypeError):
        raise ValueError(f"thread_id '{thread_id}' is not a valid GUID.")

    if project_id is not None and str(project_id).strip():
        try:
            uuid.UUID(str(project_id))
        except (ValueError, TypeError):
            raise ValueError(f"project_id '{project_id}' is not a valid GUID.")

    conn_str = get_sql_connection_string()
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            if project_id is not None and str(project_id).strip():
                query = "SELECT COUNT(*) FROM NoteAI.Threads WHERE [Id] = ? AND [Project] = ?"
                cursor.execute(query, (thread_id, project_id))
            else:
                query = "SELECT COUNT(*) FROM NoteAI.Threads WHERE [Id] = ?"
                cursor.execute(query, (thread_id,))
            count = cursor.fetchone()[0]
            if count == 0:
                if project_id is not None and str(project_id).strip():
                    raise ValueError(f"Thread with ID {thread_id} does not exist in project {project_id}.")
                else:
                    raise ValueError(f"Thread with ID {thread_id} does not exist in any project.")
    except Exception as e:
        logging.error(f"Error checking thread existence: {e}")
        raise e