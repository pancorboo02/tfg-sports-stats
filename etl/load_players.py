import soccerdata as sd
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://tfg:1234@localhost:5432/tfg_db")

fbref = sd.FBref(
    leagues=['ENG-Premier League'],
    seasons=['2021', '2022','2023','2024','2025']
)

df = fbref.read_player_season_stats(stat_type="standard")

# Reset index
df = df.reset_index()

# Aplanar columnas
df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
df.columns = [col.rstrip('_') for col in df.columns]

# Limpiar nacionalidad
df["nation"] = df["nation"].str.split().str[0]

# Renombrar columnas clave
df = df.rename(columns={
    "player": "name",
    "nation": "nationality",
    "Performance_Gls": "goals",
    "Performance_Ast": "assists"
})

# Crear id único
df["id"] = range(1, len(df) + 1)
df["season_label"] = df["season"].apply(
    lambda x: f"{int(x)-1}-{str(x)[-2:]}"
)

# Guardar TODO
df.to_sql("player_stats", engine, if_exists="replace", index=False)

print("Datos cargados correctamente")
print(len(df))