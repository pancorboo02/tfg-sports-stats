from fastapi import FastAPI
from sqlalchemy import create_engine
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import pandas as pd

app = FastAPI()

engine = create_engine("postgresql://tfg:1234@localhost:5432/tfg_db")

# CORS ARREGLADO :D
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
    SELECT *
    FROM player_stats
    WHERE name = :name
    ORDER BY season DESC
    """)

    df = pd.read_sql(query, engine, params={"name": name})
    return df.to_dict(orient="records")

@app.get("/tables")
def get_tables():
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """
    df = pd.read_sql(query, engine)
    return df["table_name"].tolist()

@app.get("/table/{table_name}")
def get_table(table_name: str, limit: int = 100, offset: int = 0):
    allowed_tables = ["players", "player_stats"]

    if table_name not in allowed_tables:
        return {"error": "Tabla no permitida"}

    limit = min(limit, 200)  # 🔥 evitar locuras

    query = f"""
    SELECT * FROM {table_name}
    ORDER BY id
    LIMIT {limit} OFFSET {offset}
    """
    
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")

from sqlalchemy import text

@app.get("/search")
def search(q: str, competition: str = None):
    if len(q) < 2:
        return []

    query = text("""
    (
        SELECT DISTINCT name, 'team' AS type, competition
        FROM teams
        WHERE name ILIKE :q
        AND (:competition IS NULL OR competition = :competition)
    )

    UNION

    (
        SELECT DISTINCT name, 'player' AS type, competition
        FROM player_stats
        WHERE name ILIKE :q
        AND (:competition IS NULL OR competition = :competition)
    )

    LIMIT 10
    """)

    df = pd.read_sql(query, engine, params={
        "q": f"%{q}%",
        "competition": competition if competition != "" else None
    })

    return df.fillna("").to_dict(orient="records")

@app.get("/team/{name}")
def get_team(name: str):
    query = """
    SELECT *
    FROM team_stats
    WHERE team_name = %s
    ORDER BY season DESC
    """
    
    df = pd.read_sql(query, engine, params=(name,))
    return df.fillna("").to_dict(orient="records")

@app.get("/standings")
def get_standings(competition: str, season: int):
    query = f"""
    SELECT *
    FROM standings
    WHERE competition = '{competition}'
    AND season = {season}
    ORDER BY points DESC
    """
    
    df = pd.read_sql(query, engine)

    if df.empty:
        return []

    return df.to_dict(orient="records")