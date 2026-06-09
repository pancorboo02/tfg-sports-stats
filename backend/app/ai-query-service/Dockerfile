FROM python:3.12-slim

WORKDIR /app

COPY app/ai-query-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ai-query-service/main.py .
COPY app/ai-query-service/ai.py .
COPY app/ai-query-service/prompts.py .
COPY app/ai-query-service/repository.py .

COPY app/shared ./shared

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]