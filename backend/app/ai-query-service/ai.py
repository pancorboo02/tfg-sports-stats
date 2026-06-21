from google import genai

import os

from dotenv import load_dotenv

from prompts import (
    SYSTEM_PROMPT,
    FORBIDDEN
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

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
            
    # Si todos fallan (no debería ocurrir pero quien sabe)
    raise Exception("Todos los modelos de IA de Google están saturados en este momento.")
