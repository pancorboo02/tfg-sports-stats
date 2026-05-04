import soccerdata as sd
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://tfg:1234@localhost:5432/tfg_db")

fbref = sd.FBref(
    leagues=['ENG-Premier League'],
    seasons=[20]
)

print("Leyendo schedule...")

df = fbref.read_schedule()
df = df.reset_index()

print("Datos cargados:", len(df))

# limpiar
df = df.rename(columns={
    "league": "competition"
})

# 🔥 arreglar encoding raro
df["score"] = df["score"].str.replace("â€“", "–")
df["season"] = df["season"].astype(int)

# 🔥 separar goles
df[["GF_home", "GA_home"]] = df["score"].str.split("–", expand=True)

df["GF_home"] = pd.to_numeric(df["GF_home"], errors="coerce")
df["GA_home"] = pd.to_numeric(df["GA_home"], errors="coerce")

# eliminar partidos no jugados
df = df[df["GF_home"].notna()]

# 🔥 home
home = df.copy()
home["team_name"] = home["home_team"]
home["GF"] = home["GF_home"]
home["GA"] = home["GA_home"]

# 🔥 away
away = df.copy()
away["team_name"] = away["away_team"]
away["GF"] = away["GA_home"]
away["GA"] = away["GF_home"]

df_teams = pd.concat([home, away])

# resultado (vectorizado)
df_teams["result"] = "D"
df_teams.loc[df_teams["GF"] > df_teams["GA"], "result"] = "W"
df_teams.loc[df_teams["GF"] < df_teams["GA"], "result"] = "L"

# agrupar
standings = []

for (team, season, competition), group in df_teams.groupby(["team_name", "season", "competition"]):
    
    matches = len(group)
    wins = (group["result"] == "W").sum()
    draws = (group["result"] == "D").sum()
    losses = (group["result"] == "L").sum()
    
    goals_for = group["GF"].sum()
    goals_against = group["GA"].sum()
    
    goal_diff = goals_for - goals_against
    points = wins * 3 + draws

    standings.append({
        "team_name": team,
        "season": season,
        "competition": competition,
        "matches": matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_diff": goal_diff,
        "points": points
    })

standings_df = pd.DataFrame(standings)

# ordenar
standings_df = standings_df.sort_values(
    ["competition", "season", "points"],
    ascending=[True, True, False]
)

standings_df["id"] = range(1, len(standings_df) + 1)

# guardar
standings_df.to_sql("standings", engine, if_exists="replace", index=False)

print("Standings generados correctamente")
print(len(standings_df))