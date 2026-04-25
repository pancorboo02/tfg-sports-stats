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

from sqlalchemy import text

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

@app.get("/search")
def search(q: str):
    if len(q) < 2:
        return []

    query = text("""
    (
        SELECT DISTINCT name, 'player' as type
        FROM player_stats
        WHERE name ILIKE :q
        LIMIT 5
    )

    UNION

    (
        SELECT DISTINCT team as name, 'team' as type
        FROM player_stats
        WHERE team ILIKE :q
        LIMIT 5
    )

    LIMIT 8
    """)

    df = pd.read_sql(query, engine, params={"q": f"%{q}%"})
    return df.to_dict(orient="records")