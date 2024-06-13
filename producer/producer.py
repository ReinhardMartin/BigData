from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def generate_sensor_data():
    return {
        "sensor_id": random.randint(1, 100),
        "temperature": random.uniform(20.0, 30.0),
        "humidity": random.uniform(30.0, 60.0),
        "timestamp": int(time.time() * 1000)
    }

while True:
    data = generate_sensor_data()
    producer.send('sensor_data', data)
    print(f"Sent data: {data}")
    time.sleep(1)
    
    if input("Type something to stop: "):
        break
