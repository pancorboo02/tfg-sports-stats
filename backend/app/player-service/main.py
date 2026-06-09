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

@app.get("/player/{name}")
def get_player(name: str):

    query = text("""
    SELECT
        ps.name,
        ps.season,

        STRING_AGG(
            DISTINCT ps.team_name || '@@' || COALESCE(t.logo_url, ''),
            '||'
        ) AS team_data,

        MAX(ps.nationality) AS nationality,
        MAX(ps.pos) AS pos,
        MAX(ps.age) AS age,
        MAX(ps.competition) AS competition,
        MAX(ps.born) AS born,

        SUM(ps.goals) AS goals,
        SUM(ps.assists) AS assists,
        SUM(ps.goal_contributions) AS goal_contributions,
        SUM(ps.non_penalty_goals) AS non_penalty_goals,
        SUM(ps.non_penalty_goal_contributions) AS non_penalty_goal_contributions,

        SUM(ps.penalties_scored) AS penalties_scored,
        SUM(ps.penalties_attempted) AS penalties_attempted,

        SUM(ps.yellow_cards) AS yellow_cards,
        SUM(ps.red_cards) AS red_cards,

        SUM(ps.matches_played) AS matches_played,
        SUM(ps.starts) AS starts,
        SUM(ps.minutes) AS minutes,
        SUM(ps.matches_90s) AS matches_90s,

        AVG(ps.per90_goals) AS per90_goals,
        AVG(ps.per90_assists) AS per90_assists,
        AVG(ps.per90_goal_contributions) AS per90_goal_contributions,
        AVG(ps.per90_non_penalty_goals) AS per90_non_penalty_goals,
        AVG(ps.per90_non_penalty_goal_contributions) AS per90_non_penalty_goal_contributions

    FROM player_stats ps

    LEFT JOIN teams t
        ON ps.team_name = t.name

    WHERE ps.name = :name

    GROUP BY ps.name, ps.season

    ORDER BY ps.season DESC
    """)

    df = pd.read_sql(
        query,
        engine,
        params={
            "name": name
        }
    )

    return df.fillna("").to_dict(orient="records")