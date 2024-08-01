FROM python:3.9-slim

WORKDIR /app

RUN pip install Flask paho-mqtt

COPY . .

CMD ["python", "app.py"]
