import pyodbc
import project_handler

def get_messages(thread_id):
    project_handler.check_thread_exists(thread_id)
    conn_str = project_handler.get_sql_connection_string()
    query = """
        SELECT Role, Message
        FROM NoteAI.Messages
        WHERE Thread = ?
          AND (Role = 'user' OR Role = 'assistant')
        ORDER BY SYS_INSERT
    """
    messages = []
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (thread_id,))
        for row in cursor.fetchall():
            messages.append({
                "role": row.Role,
                "content": row.Message
            })
    return messages

def add_message(thread_id, model, role, source, content, prompt_tokens=0, completion_tokens=0, reasoning_tokens=0):
    project_handler.check_thread_exists(thread_id)
    conn_str = project_handler.get_sql_connection_string()
    query = """
        INSERT INTO NoteAI.Messages (Thread, Model, Role, Source, Message, PromptTokens, CompletionTokens, ReasoningTokens)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(
            query,
            (thread_id, model, role, source, content, prompt_tokens, completion_tokens, reasoning_tokens)
        )
        conn.commit()