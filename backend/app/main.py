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
- matches_played (partidos jugados)
- starts (titularidades)
- minutes 
- matches_90s (partidos completos equivalentes)
- goal_contributions (contribuciones de gol, G+A)
- non_penalty_goal_contributions (contribuciones de gol sin penalti, G+A-Pk)
- non_penalty_goals (goles sin penalti, G-Pk)
- penalties_scored (penaltis marcados)
- penalties_attempted (penaltis intentados)
- yellow_cards
- red_cards
- per90_goals
- per90_assists
- per90_goal_contributions (contribuciones de gol por 90 mins)
- per90_non_penalty_goals (goles por 90 mins sin penaltis)
- per90_non_penalty_goal_contributions (contribuciones de gol sin penaltis por 90 mins)


team_stats (estadísticas colectivas de equipos por temporada):

- team_name (nombre equipo)
- competition (liga)
- season (temporada)
- 90s (partidos jugados)

- players_used (jugadores utilizados)
- goals (goles marcados)
- shots (tiros totales)
- shots_on_target (tiros a puerta)

- shot_accuracy (precisión de tiro)
- shots_per90 (tiros por partido)
- shots_on_target_per90 (tiros a puerta por partido)

- goals_per_shot (goles por tiro realizado)
- goals_per_shot_on_target (goles por tiro a puerta realizado)

- penalties_scored (penaltis marcados)
- penalties_attempted (penaltis intentados)

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

REGLAS DE UTILIDAD DE RESULTADOS:

Devuelve resultados útiles y completos para el usuario.

Cuando el usuario pregunte por una métrica
(goles, asistencias, contribuciones de gol, penaltis, tarjetas, tiros, puntos, etc.):

incluye SIEMPRE esa métrica en el SELECT aunque el usuario no pida explícitamente mostrarla.

Ejemplos:

- "jugadores con más goles"
→ incluye goals

- "equipos con más tiros"
→ incluye shots

- "porteros con alguna contribución de gol"
→ incluye goal_contributions

- "jugadores con penaltis marcados"
→ incluye penalties_scored

No devuelvas solo nombre/temporada/competición si existe una métrica principal relacionada con la pregunta.

La columna principal debe aparecer en el SELECT.

Cuando el usuario diga:

- "alguna contribución de gol"
- "con goles"
- "con asistencias"
- "con penaltis"

además del filtro correspondiente (> 0),
incluye esa columna en SELECT.

Ejemplo:

WHERE goal_contributions > 0

y también:

SELECT name, season, competition, goal_contributions

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

Ejemplo correcto:
competition IN ('La Liga', 'Premier League')

Las temporadas son BIGINT.
NO uses comillas para temporadas.

Ejemplo correcto:
season IN (2122, 2223)

Cuando el usuario diga:

- "en todas las temporadas"
- "cada temporada"
- "temporadas disponibles"

debe interpretarse SOLO por season.

NO combinar season con competition
salvo que el usuario lo pida explícitamente.

REGLAS SOBRE POSICIONES:

La columna "pos" puede contener múltiples posiciones.

Ejemplos:
- FW
- FW,MF
- MF,FW
- DF,MF

Por tanto:

- delanteros -> pos LIKE '%FW%'
- mediocampistas -> pos LIKE '%MF%'
- defensas -> pos LIKE '%DF%'
- porteros -> pos LIKE '%GK%'

NO uses:
pos = 'FW'

excepto si el usuario pide exclusivamente delanteros puros.

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

        -- Stats principales
        SUM(ps.goals) AS goals,
        SUM(ps.assists) AS assists,
        SUM(ps.goal_contributions) AS goal_contributions,
        SUM(ps.non_penalty_goals) AS non_penalty_goals,
        SUM(ps.non_penalty_goal_contributions) AS non_penalty_goal_contributions,

        -- Penaltis
        SUM(ps.penalties_scored) AS penalties_scored,
        SUM(ps.penalties_attempted) AS penalties_attempted,

        -- Disciplina
        SUM(ps.yellow_cards) AS yellow_cards,
        SUM(ps.red_cards) AS red_cards,

        -- Tiempo de juego
        SUM(ps.matches_played) AS matches_played,
        SUM(ps.starts) AS starts,
        SUM(ps.minutes) AS minutes,
        SUM(ps.matches_90s) AS matches_90s,

        -- Stats por 90
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

    df = pd.read_sql(query, engine, params={
        "name": name
    })

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

# @app.get("/table/{table_name}")
# def get_table(table_name: str, limit: int = 100, offset: int = 0):
#     allowed_tables = ["players", "player_stats"]

#     if table_name not in allowed_tables:
#         return {"error": "Tabla no permitida"}

#     limit = min(limit, 200)  # evitar locuras

#     query = f"""
#     SELECT * FROM {table_name}
#     ORDER BY id
#     LIMIT {limit} OFFSET {offset}
#     """
    
#     df = pd.read_sql(query, engine)
#     return df.to_dict(orient="records")

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