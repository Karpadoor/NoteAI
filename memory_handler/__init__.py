import logging
import pyodbc
import json
import project_handler

class MemoryHandlerError(Exception):
    pass

def get_memory(project_id):
    """
    Fetch the JSON field from the latest (highest Version) record for the given project.
    Raises MemoryHandlerError if connection string is missing or no memory is found.
    """
    project_handler.check_project_exists(project_id)
    conn_str = project_handler.get_sql_connection_string()

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = """
                SELECT TOP 1 [JSON]
                FROM [NoteAI].[Memory]
                WHERE [Project] = ?
                ORDER BY [Version] DESC
            """
            cursor.execute(query, (project_id,))
            row = cursor.fetchone()
            if row:
                return row.JSON
            else:
                logging.info(f"No memory found for project: {project_id}")
                raise MemoryHandlerError(f"No memory found for project: {project_id}")
    except Exception as e:
        logging.error(f"Error fetching memory: {e}")
        raise MemoryHandlerError(f"Error fetching memory: {e}")
    
def set_memory(project_id, memory_json, prompt_tokens=0, completion_tokens=0, reasoning_tokens=0):
    """
    Validate memory_json is valid JSON, then insert a new row into NoteAI.Memory
    with Version = last version for this project + 1.
    Optionally accepts prompt_tokens, completion_tokens, reasoning_tokens (default 0).
    Raises MemoryHandlerError on failure.
    """
    project_handler.check_project_exists(project_id)
    conn_str = project_handler.get_sql_connection_string()

    # Validate JSON
    try:
        json.loads(memory_json)
    except Exception as e:
        logging.error(f"Invalid JSON provided: {e}")
        raise MemoryHandlerError(f"Invalid JSON provided: {e}")

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            # Get last version
            cursor.execute(
                "SELECT ISNULL(MAX([Version]), 0) FROM [NoteAI].[Memory] WHERE [Project] = ?",
                (project_id,)
            )
            last_version = cursor.fetchone()[0]
            new_version = last_version + 1

            # Insert new row with optional token columns
            cursor.execute(
                """
                INSERT INTO [NoteAI].[Memory] 
                    ([Project], [Version], [JSON], [PromptTokens], [CompletionTokens], [ReasoningTokens])
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, new_version, memory_json, prompt_tokens, completion_tokens, reasoning_tokens)
            )
            conn.commit()
            logging.info(f"Inserted memory for project {project_id} with version {new_version}")
            return new_version
    except Exception as e:
        logging.error(f"Error setting memory: {e}")
        raise MemoryHandlerError(f"Error setting memory: {e}")