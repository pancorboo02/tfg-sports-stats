FROM python:3.12-slim

WORKDIR /app

COPY app/team-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/team-service/main.py .

COPY app/shared ./shared

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]