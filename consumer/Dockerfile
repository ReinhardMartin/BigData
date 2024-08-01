FROM python:3.9-slim

WORKDIR /app

RUN pip install paho-mqtt pymongo

COPY . .

CMD ["python", "consumer.py"]
