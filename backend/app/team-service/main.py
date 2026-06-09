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

@app.get("/team/{name}")
def get_team(name: str):

    query = text("""
    SELECT
        ts.*,
        t.logo_url

    FROM team_stats ts

    LEFT JOIN teams t
        ON ts.team_name = t.name

    WHERE ts.team_name = :name

    ORDER BY ts.season DESC
    """)

    df = pd.read_sql(
        query,
        engine,
        params={
            "name": name
        }
    )

    return df.fillna("").to_dict(orient="records")