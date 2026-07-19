FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY .env .

EXPOSE 8080

ENV PORT=8080

CMD ["python", "app.py"]
