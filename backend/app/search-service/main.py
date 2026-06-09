from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
import pandas as pd

from shared.database import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tables")
def get_tables():

    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """

    df = pd.read_sql(query, engine)

    return df["table_name"].tolist()


@app.get("/search")
def search(q: str, competition: str = None):

    if len(q) < 2:
        return []

    query = text("""
    (
        SELECT DISTINCT
            t.name,
            'team' AS type,
            t.competition,
            t.logo_url

        FROM teams t

        WHERE t.name ILIKE :q
        AND (:competition IS NULL OR t.competition = :competition)
    )

    UNION

    (
        SELECT DISTINCT ON (ps.name)
            ps.name,
            'player' AS type,
            ps.competition,
            '' AS logo_url

        FROM player_stats ps

        WHERE ps.name ILIKE :q
        AND (:competition IS NULL OR ps.competition = :competition)

        ORDER BY ps.name, ps.season DESC
    )

    LIMIT 10
    """)

    df = pd.read_sql(
        query,
        engine,
        params={
            "q": f"%{q}%",
            "competition": competition if competition != "" else None
        }
    )

    return df.fillna("").to_dict(orient="records")