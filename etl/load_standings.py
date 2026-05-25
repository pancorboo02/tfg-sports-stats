import soccerdata as sd
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://tfg:1234@localhost:5432/tfg_db")

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

print("Leyendo schedule...")

df = fbref.read_schedule()
df = df.reset_index()

print("Datos cargados:", len(df))

# normalizar competición
df["competition"] = df["league"]

df["competition"] = df["competition"].str.replace("ENG-", "", regex=False)
df["competition"] = df["competition"].str.replace("ESP-", "", regex=False)
df["competition"] = df["competition"].str.replace("ITA-", "", regex=False)
df["competition"] = df["competition"].str.replace("GER-", "", regex=False)
df["competition"] = df["competition"].str.replace("FRA-", "", regex=False)

# arreglar encoding
df["score"] = df["score"].str.replace("â€“", "–")

df["season"] = df["season"].astype(int)

# separar goles
df[["GF_home", "GA_home"]] = df["score"].str.split("–", expand=True)

df["GF_home"] = pd.to_numeric(df["GF_home"], errors="coerce")
df["GA_home"] = pd.to_numeric(df["GA_home"], errors="coerce")

df = df[df["GF_home"].notna()]

# home
home = df.copy()
home["team_name"] = home["home_team"]
home["GF"] = home["GF_home"]
home["GA"] = home["GA_home"]

# away
away = df.copy()
away["team_name"] = away["away_team"]
away["GF"] = away["GA_home"]
away["GA"] = away["GF_home"]

df_teams = pd.concat([home, away])

# resultado vectorizado
df_teams["result"] = "D"
df_teams.loc[df_teams["GF"] > df_teams["GA"], "result"] = "W"
df_teams.loc[df_teams["GF"] < df_teams["GA"], "result"] = "L"

# agrupar
standings = []

for (team, season, competition), group in df_teams.groupby(
    ["team_name", "season", "competition"]
):

    wins = (group["result"] == "W").sum()
    draws = (group["result"] == "D").sum()
    losses = (group["result"] == "L").sum()

    goals_for = group["GF"].sum()
    goals_against = group["GA"].sum()

    standings.append({
        "team_name": team,
        "season": season,
        "competition": competition,
        "matches": len(group),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_diff": goals_for - goals_against,
        "points": wins * 3 + draws
    })

standings_df = pd.DataFrame(standings)
standings_df = standings_df[
    standings_df["matches"] >= 10  #así evito que se metan equipos de divisiones inferiores que hayan jugado playoff
]
# ordenar
standings_df = standings_df.sort_values(
    ["competition", "season", "points"],
    ascending=[True, True, False]
)

standings_df["id"] = range(1, len(standings_df) + 1)

# guardar
standings_df.to_sql("standings", engine, if_exists="replace", index=False)

print("Standings cargados correctamente")
print(len(standings_df))