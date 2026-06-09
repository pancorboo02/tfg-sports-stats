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

@app.get("/standings")
def get_standings(competition: str, season: int):

    query = text("""
    SELECT
        s.*,
        t.logo_url

    FROM standings s

    LEFT JOIN teams t
        ON s.team_name = t.name

    WHERE s.competition = :competition
    AND s.season = :season

    ORDER BY s.points DESC
    """)

    df = pd.read_sql(
        query,
        engine,
        params={
            "competition": competition,
            "season": season
        }
    )

    if df.empty:
        return []

    return df.fillna("").to_dict(orient="records")