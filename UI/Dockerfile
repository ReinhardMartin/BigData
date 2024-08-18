FROM python:3.9-slim

WORKDIR /app

RUN pip install Flask paho-mqtt numpy

COPY . .

CMD ["python", "app.py"]
