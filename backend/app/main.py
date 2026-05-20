from fastapi import FastAPI
from sqlalchemy import create_engine
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import pandas as pd
from google import genai
import re
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Eres un experto en PostgreSQL.

Tu tarea es convertir preguntas de fútbol en consultas SQL.

REGLAS IMPORTANTES:

- SOLO puedes generar consultas SELECT. 
- NUNCA uses DELETE, UPDATE, INSERT, DROP o ALTER.
- Responde SOLO con SQL.
- NO uses markdown.
- NO uses ```sql.
- Añade SIEMPRE LIMIT 100.

Tablas disponibles:

player_stats:
- name
- team_name
- nationality
- pos
- season
- competition
- goals
- assists
- Playing Time_MP (partidos jugados)
- Playing Time_Starts (titularidades)
- Playing Time_Min
- Playing Time_90s (partidos completos equivalentes)
- Performance_G+A (contribuciones de gol)
- Performance_G-PK (contribuciones de gol sin penalti)
- Performance_PK (penaltis marcados)
- Performance_PKatt (penaltis intentados)
- Performance_CrdY
- Performance_CrdR
- Per 90 Minutes_Gls
- Per 90 Minutes_Ast
- Per 90 Minutes_G+A (contribuciones de gol por 90 mins)
- Per 90 Minutes_G-PK (goles por 90 mins sin penaltis)
- Per 90 Minutes_G+A-PK (contribuciones de gol sin penaltis por 90 mins)


team_stats (estadísticas colectivas de equipos por temporada):

- team_name (nombre equipo)
- competition (liga)
- season (temporada)
- 90s (partidos jugados)

- players_used (jugadores utilizados)
- goals (goles marcados)
- shots (tiros totales)
- shots_on_target (tiros a puerta)

- Standard_SoT% (precisión de tiro)
- Standard_Sh/90 (tiros por partido)
- Standard_SoT/90 (tiros a puerta por partido)

- Standard_G/Sh (conversión de tiros en gol)
- Standard_G/SoT (conversión de tiros a puerta en gol)

- Standard_PK (penaltis marcados)
- Standard_PKatt (penaltis intentados)

standings:
- team_name
- competition
- season
- matches
- wins
- draws
- losses
- goals_for
- goals_against
- goal_diff
- points

REGLAS SEMÁNTICAS:

- “liga española” -> La Liga
- “liga inglesa” -> Premier League
- “liga italiana” -> Serie A
- “liga alemana” -> Bundesliga
- "liga francesa" -> Ligue 1

FORMATO EXACTO:

- 20-21 -> '2021'
- 21-22 -> '2122'
- 22-23 -> '2223'
- 23-24 -> '2324'
- 24-25 -> '2425'
- 25-26 -> '2526'


Cuando uses IN sobre columnas TEXT, los valores deben ir entre comillas simples.

Ejemplo:
season IN ('2122', '2223')

- Cuando el usuario pregunte:
  "equipos con más..."
  "equipos con menos..."
  "ranking..."
  "top..."
  "peores..."
  "mejores..."

NO debes buscar únicamente el valor mínimo o máximo absoluto usando MIN() o MAX().

Debes generar un ranking ordenado usando:
ORDER BY ... ASC/DESC

Ejemplo correcto:
SELECT team_name, SUM(shots_on_target) AS total_tiros_puerta
FROM team_stats
GROUP BY team_name
ORDER BY total_tiros_puerta ASC
LIMIT 100

- Las nacionalidades de los jugadores están guardadas en formato Alfa-3 Iso 3166-1, es decir
ESPAÑA = ESP, ARGENTINA = ARG

- Usa SIEMPRE nombres exactos de columnas.
- NO inventes columnas.
- NO inventes tablas.
- PostgreSQL requiere comillas dobles para columnas con espacios.
- Ejemplo:
  "Playing Time_MP"

- Si una columna tiene espacios o símbolos, usa comillas dobles.

- IDIOMA DE ALIAS: Cuando el usuario solicite métricas agregadas o calculadas (usando SUM, AVG, COUNT, etc.), debes crear SIEMPRE el alias de la columna (usando 'AS') en ESPAÑOL utilizando snake_case. 
- Está terminantemente prohibido usar palabras en inglés para los alias creados (por ejemplo, usa 'total_penaltis_intentados' en lugar de 'total_penalties_attempted').

- Devuelve SOLO SQL válido PostgreSQL.
"""

FORBIDDEN = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE"
]

def clean_sql(sql: str):

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql


def validate_sql(sql: str):

    sql_upper = sql.upper().strip()

    if not sql_upper.startswith("SELECT"):
        return False

    for word in FORBIDDEN:
        if word in sql_upper:
            return False

    return True

def generate_sql(question: str):
    prompt = f"{SYSTEM_PROMPT}\n\nPregunta:\n{question}"
    
    # Lista de modelos a probar por si el principal está saturado
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            print(f"-> SQL generado exitosamente con: {model_name}")
            return clean_sql(response.text)
        except Exception as e:
            print(f"El modelo {model_name} falló o está saturado: {str(e)}")
            continue # Si falla, salta al siguiente modelo de la lista
            
    # Si todos fallan (cosa rarísima)
    raise Exception("Todos los modelos de IA de Google están saturados en este momento.")

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

        SUM(ps."Playing Time_MP") AS "Playing Time_MP",
        SUM(ps."Playing Time_Min") AS "Playing Time_Min",

        SUM(ps."Performance_G+A") AS "Performance_G+A",
        SUM(ps."Performance_CrdY") AS "Performance_CrdY",
        SUM(ps."Performance_CrdR") AS "Performance_CrdR"

    FROM player_stats ps

    LEFT JOIN teams t
        ON ps.team_name = t.name

    WHERE ps.name = :name

    GROUP BY ps.name, ps.season

    ORDER BY ps.season DESC
    """)

    df = pd.read_sql(query, engine, params={"name": name})

    return df.fillna("").to_dict(orient="records")

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

    df = pd.read_sql(query, engine, params={
        "name": name
    })

    return df.fillna("").to_dict(orient="records")

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
        conn.execute(query, {
            "question": question,
            "sql": sql
        })

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
            return {
                "error": "SQL inválido"
            }

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