import soccerdata as sd
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://tfg:1234@localhost:5432/tfg_db")

fbref = sd.FBref(
    leagues=[
        'ENG-Premier League',
        'ESP-La Liga',
        'ITA-Serie A',
        'GER-Bundesliga',
        'FRA-Ligue 1'
    ],
    seasons=[20,21,22,23,24,25]
)

df = fbref.read_team_season_stats(stat_type="shooting")

df = df.reset_index()

# Aplanar columnas
df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
df.columns = [col.rstrip('_') for col in df.columns]

# Renombrar
df = df.rename(columns={
    "league": "competition",
    "team": "team_name",
    "Standard_Gls": "goals",
    "Standard_Sh": "shots",
    "Standard_SoT": "shots_on_target"
})


df["competition"] = df["competition"].str.replace("ENG-", "", regex=False)
df["competition"] = df["competition"].str.replace("ESP-", "", regex=False)
df["competition"] = df["competition"].str.replace("ITA-", "", regex=False)
df["competition"] = df["competition"].str.replace("GER-", "", regex=False)
df["competition"] = df["competition"].str.replace("FRA-", "", regex=False)

# id
df["id"] = range(1, len(df) + 1)

df.to_sql("team_stats", engine, if_exists="replace", index=False)

print("Teams cargados")
print(len(df))