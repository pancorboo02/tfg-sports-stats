import soccerdata as sd
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://tfg:1234@localhost:5432/tfg_db")

# 🔥 5 grandes ligas
leagues = [
    'ENG-Premier League',
    'ESP-La Liga',
    'ITA-Serie A',
    'GER-Bundesliga',
    'FRA-Ligue 1'
]

seasons = [20, 21, 22, 23, 24, 25]

fbref = sd.FBref(
    leagues=leagues,
    seasons=seasons
)

print("Leyendo player stats...")

df = fbref.read_player_season_stats(stat_type="standard")

df = df.reset_index()

print("Datos cargados:", len(df))

# 🔥 aplanar columnas
df.columns = [
    '_'.join(col).strip() if isinstance(col, tuple) else col
    for col in df.columns
]
df.columns = [col.rstrip('_') for col in df.columns]

# 🔥 normalizar competición
df["competition"] = df["league"]

df["competition"] = df["competition"].str.replace("ENG-", "", regex=False)
df["competition"] = df["competition"].str.replace("ESP-", "", regex=False)
df["competition"] = df["competition"].str.replace("ITA-", "", regex=False)
df["competition"] = df["competition"].str.replace("GER-", "", regex=False)
df["competition"] = df["competition"].str.replace("FRA-", "", regex=False)

# 🔥 limpiar nacionalidad
df["nation"] = df["nation"].str.split().str[0]

# 🔥 tipos
df["season"] = df["season"].astype(int)

# 🔥 renombrar columnas clave
df = df.rename(columns={
    "player": "name",
    "nation": "nationality",
    "team": "team_name",
    "Performance_Gls": "goals",
    "Performance_Ast": "assists"
})

# 🔥 eliminar columnas innecesarias si quieres optimizar
# df = df[["name", "team_name", "competition", "season", "goals", "assists", ...]]

# 🔥 id
df["id"] = range(1, len(df) + 1)

# 🔥 limpiar NaN
df = df.fillna(0)

# guardar
df.to_sql("player_stats", engine, if_exists="replace", index=False)

print("Player stats cargados correctamente")
print(len(df))