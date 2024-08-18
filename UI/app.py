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
NUM_MACHINES = 5
is_publishing = False
is_subscribing = False
client = mqtt.Client()
predictions = {}

def generate_sensor_data(machine_id):
    # Generate timestamp
    timestamp = datetime.utcnow().isoformat()

    # Generate sensor metrics using normal distribution
    temperature = random.uniform(20.0, 100.0)
    pressure = random.uniform(30.0, 150.0)
    vibration = random.uniform(10.0, 50.0)
    
    # Dynamic thresholds
    lower_threshold_temp = np.random.uniform(59, 65)
    upper_threshold_temp = np.random.uniform(101, 105)

    lower_threshold_pressure = np.random.uniform(99, 105)
    upper_threshold_pressure = np.random.uniform(167, 171)

    lower_threshold_vibration = np.random.uniform(44, 46)
    upper_threshold_vibration = np.random.uniform(65, 68)

    # Determine status based on thresholds
    if (temperature < lower_threshold_temp) or (temperature > upper_threshold_temp) or \
       (pressure < lower_threshold_pressure) or (pressure > upper_threshold_pressure) or \
       (vibration < lower_threshold_vibration) or (vibration > upper_threshold_vibration):
        status = 'failure'
    else:
        status = 'ok'

    # Prepare data
    data = {
        "timestamp": timestamp,
        "machine_id": machine_id,
        "temperature": temperature,
        "pressure": pressure,
        "vibration": vibration,
        "status": status
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
    status = []
    for machine_id, prob in predictions.items():
        failure_probability = 1 - prob
        if failure_probability > 0.85:
            color = "red"
        if failure_probability >= 0.35:
            color = "yellow"
        else:
            color = "green"
        status.append({
            "machine_id": machine_id,
            "color": color,
            "failure_probability": failure_probability
        })
    # Sort the status list by failure probability in descending order
    status = sorted(status, key=lambda x: x['failure_probability'], reverse=True)
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

