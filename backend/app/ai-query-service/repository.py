from sqlalchemy import text

from shared.database import engine


def save_query(question: str, sql: str):

    query = text("""
    INSERT INTO query_history (
        question,
        sql_query
    )
    VALUES (
        :question,
        :sql
    )
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "question": question,
                "sql": sql
            }
        )