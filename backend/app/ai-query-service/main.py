from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
import pandas as pd

from shared.database import engine

from ai import (
    generate_sql,
    validate_sql
)

from repository import save_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/query-history")
def get_query_history():

    query = text("""
    SELECT *
    FROM query_history
    ORDER BY created_at DESC
    LIMIT 10
    """)

    df = pd.read_sql(query, engine)

    return df.fillna("").to_dict(orient="records")

@app.delete("/query-history")
def clear_query_history():

    query = text("""
    DELETE FROM query_history
    """)

    with engine.begin() as conn:
        conn.execute(query)

    return {
        "message": "Historial borrado"
    }

@app.get("/ask")
def ask(question: str):

    try:

        sql = generate_sql(question)

        print("QUESTION:")
        print(question)

        print("SQL:")
        print(sql)

        if not validate_sql(sql):
            print("SQL inválido:", sql)
            return {"error": "SQL inválido"}

        if "LIMIT" not in sql.upper():
            sql += " LIMIT 100"

        df = pd.read_sql(text(sql), engine)

        if "team_name" in df.columns:

            logos_query = text("""
            SELECT name, logo_url
            FROM teams
            """)

            logos_df = pd.read_sql(logos_query, engine)

            logos_map = dict(
                zip(logos_df["name"], logos_df["logo_url"])
            )

            df["team_logo"] = df["team_name"].map(logos_map)
        save_query(question, sql)
        return {
            "question": question,
            "sql": sql,
            "results": df.fillna("").to_dict(orient="records")
        }

    except Exception as e:

        return {
            "error": str(e)
        }