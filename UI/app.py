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
is_subscribing = False
client = mqtt.Client()
predictions = {}

def generate_sensor_data(machine_id):
    timestamp = datetime.utcnow().isoformat()
    temperature = random.uniform(20.0, 100.0)
    pressure = random.uniform(30.0, 150.0)
    vibration = random.uniform(10.0, 50.0)
    data = {
        "timestamp": timestamp,
        "machine_id": machine_id,
        "temperature": temperature,
        "pressure": pressure,
        "vibration": vibration
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
        time.sleep(3)

def stop_publishing():
    global is_publishing
    is_publishing = False
    client.disconnect()

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        topic_parts = msg.topic.split('/')
        machine_id = topic_parts[-1]
        probability = payload.get('probability', 0)
        predictions[machine_id] = probability
        print(f"Received and updated prediction for {machine_id}: {probability}")
    except Exception as e:
        print(f"Error processing message: {e}")

def start_subscribing():
    global is_subscribing
    is_subscribing = True
    client.connect(BROKER, PORT, 60)
    client.subscribe("predictions/#")
    client.on_message = on_message
    client.loop_start()

def stop_subscribing():
    global is_subscribing
    is_subscribing = False
    client.unsubscribe("predictions/#")
    client.loop_stop()
    client.disconnect()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    threading.Thread(target=start_publishing).start()
    if not is_subscribing:
        threading.Thread(target=start_subscribing).start()
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop():
    stop_publishing()
    stop_subscribing()
    return jsonify({"status": "stopped"})

@app.route('/status', methods=['GET'])
def get_status():
    status = {}
    for machine_id, prob in predictions.items():
        if prob > 0.85:
            status[machine_id] = "green"
        elif prob >= 0.35:
            status[machine_id] = "yellow"
        else:
            status[machine_id] = "red"
    return jsonify(status)

@app.route('/schedule', methods=['GET'])
def get_schedule():
    # Sort machines by probability (ascending) for maintenance scheduling
    sorted_machines = sorted(predictions.items(), key=lambda item: item[1])
    schedule = [{"machine_id": machine_id, "probability": prob} for machine_id, prob in sorted_machines]
    return jsonify(schedule)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
