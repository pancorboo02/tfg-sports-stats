import requests
import pandas as pd
from sqlalchemy import create_engine, text
import os

import soccerdata as sd
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
API_KEY = "1c17684803df420a8276c2de73e427fd"

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / "backend" / ".env"

load_dotenv(ENV_PATH)

DATABASE_URL = (
    f"postgresql://{os.getenv('DATABASE_USER')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOST')}:"
    f"{os.getenv('DATABASE_PORT')}/"
    f"{os.getenv('DATABASE_NAME')}"
)

engine = create_engine(DATABASE_URL)

headers = {
    "X-Auth-Token": API_KEY
}

competitions = {
    "PL": "Premier League",
    "PD": "La Liga",
    "SA": "Serie A",
    "BL1": "Bundesliga",
    "FL1": "Ligue 1"
}

team_name_map = {
    #Premier League
    "Man City": "Manchester City",
    "Man United": "Manchester Utd",
    "Brighton Hove": "Brighton",
    "Newcastle": "Newcastle United",
    "Tottenham": "Tottenham Hotspur",
    "Nottingham": "Nottingham Forest",
    "West Ham": "West Ham United",
    "Wolverhampton": "Wolves",
    #La Liga
    "Barça": "Barcelona",
    "Atleti": "Atlético Madrid",
    "Celta": "Celta Vigo",
    "Athletic": "Athletic Club",
    "Sevilla FC": "Sevilla",
    "Real Oviedo": "Oviedo",
    #Ligue One
    "RC Lens": "Lens",
    "Olympique Lyon": "Lyon",
    "Stade Rennais": "Rennes",
    "Angers SCO": "Angers",
    "FC Metz": "Metz",
    "PSG": "Paris Saint-Germain",
    #Bundesliga
    "Bayern": "Bayern Munich",
    "Frankfurt": "Eintracht Frankfurt",
    "Mainz": "Mainz 05",
    "M'gladbach": "Gladbach",
    "HSV": "Hamburger SV",
    "1. FC Köln": "Köln", #ojo con este en terminal sale 1. FC Köln
    "Bremen": "Werder Bremen",
    "St. Pauli": "St Pauli",
    #Serie A
    "Inter Milan": "Inter",
    "AC Milan": "Milan",
    "Como 1907": "Como",
    "Verona": "Hellas Verona",
    "AC Pisa": "Pisa"
}

for code in competitions.keys():

    print(f"Cargando {code}...")

    url = f"https://api.football-data.org/v4/competitions/{code}/teams"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error en {code}")
        print(response.status_code)
        print(response.text)
        continue

    data = response.json()

    for team in data["teams"]:

        api_name = team["shortName"]

        db_name = team_name_map.get(api_name, api_name)

        logo_url = team["crest"]

        update_query = text("""
        UPDATE teams
        SET logo_url = :logo_url
        WHERE name = :team_name
        """)

        with engine.begin() as conn:
            conn.execute(
                update_query,
                {
                    "logo_url": logo_url,
                    "team_name": db_name
                }
            )

        print(f"✔ {db_name}")

print("Logos cargados")