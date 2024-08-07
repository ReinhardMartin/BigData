from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import threading
import random
import time
import json
from datetime import datetime

app = Flask(__name__)

BROKER = 'mosquitto'
PORT = 1883
NUM_MACHINES = 25
is_publishing = False
client = mqtt.Client()

def generate_sensor_data(machine_id):
    timestamp = datetime.utcnow().isoformat()
    sensor1 = random.uniform(20.0, 100.0)
    sensor2 = random.uniform(30.0, 150.0)
    sensor3 = random.uniform(10.0, 50.0)
    data = {
        "timestamp": timestamp,
        "machine_id": machine_id,
        "sensor1": sensor1,
        "sensor2": sensor2,
        "sensor3": sensor3
    }
    return data

def start_publishing():
    global is_publishing
    is_publishing = True
    client.connect(BROKER, PORT, 60)
    while is_publishing:
        for machine_id in range(1, NUM_MACHINES + 1):
            data = generate_sensor_data(machine_id)
            topic = f"machines/machine_{machine_id}"
            payload = json.dumps(data)
            client.publish(topic, payload)
            print(f"Published to {topic}: {payload}")
        time.sleep(1)

def stop_publishing():
    global is_publishing
    is_publishing = False
    client.disconnect()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    threading.Thread(target=start_publishing).start()
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop():
    stop_publishing()
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
