from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import threading
import random
import time
import json
from datetime import datetime
import numpy as np

app = Flask(__name__)

BROKER = 'mosquitto'
PORT = 1883
NUM_MACHINES = 25
is_publishing = False
is_subscribing = False
client = mqtt.Client()
predictions = {}

# Initialize the state for each machine
machines = {
    machine_id: {
        'temp': np.random.normal(loc=85, scale=5),
        'pressure': np.random.normal(loc=135, scale=5),
        'vibration': np.random.normal(loc=55, scale=5),
        'degradation_rate_temp': np.random.uniform(-0.5, 0.5),
        'degradation_rate_pressure': np.random.uniform(-0.3, 0.3),
        'degradation_rate_vibration': np.random.uniform(-0.2, 0.2),
        'failed': False
    }
    for machine_id in range(1, NUM_MACHINES + 1)
}

def generate_sensor_data(machine_id):
    machine = machines[machine_id]
    if machine['failed']:
        return None  # Skip data generation for failed machines

    timestamp = datetime.utcnow().isoformat()

    # Dynamic thresholds
    lower_threshold_temp = random.uniform(59, 65)
    upper_threshold_temp = random.uniform(101, 105)
    lower_threshold_pressure = random.uniform(99, 105)
    upper_threshold_pressure = random.uniform(167, 171)
    lower_threshold_vibration = random.uniform(44, 46)
    upper_threshold_vibration = random.uniform(65, 68)

    # Update sensor metrics
    machine['temp'] += machine['degradation_rate_temp']
    machine['pressure'] += machine['degradation_rate_pressure']
    machine['vibration'] += machine['degradation_rate_vibration']

    # Determine status based on thresholds
    if (machine['temp'] < lower_threshold_temp) or (machine['temp'] > upper_threshold_temp) or \
       (machine['pressure'] < lower_threshold_pressure) or (machine['pressure'] > upper_threshold_pressure) or \
       (machine['vibration'] < lower_threshold_vibration) or (machine['vibration'] > upper_threshold_vibration):
        machine['failed'] = True  # Mark this machine as failed
        return None  # No data will be sent for failed machines

    data = {
        "timestamp": timestamp,
        "machine_id": machine_id,
        "temperature": machine['temp'],
        "pressure": machine['pressure'],
        "vibration": machine['vibration'],
        "status": "ok"
    }
    return data

def start_publishing():
    global is_publishing
    is_publishing = True
    client.connect(BROKER, PORT, 60)
    while is_publishing:
        for machine_id in range(1, NUM_MACHINES + 1):
            data = generate_sensor_data(machine_id)
            if data:  # Only publish if data is available (i.e., machine has not failed)
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

@app.route('/data', methods=['GET'])
def get_data():
    data = {}
    for machine_id, machine in machines.items():
        data[machine_id] = {
            "temperature": machine['temp'],
            "pressure": machine['pressure'],
            "vibration": machine['vibration'],
            "status": "failed" if machine['failed'] else "ok"
        }
    return jsonify(data)

@app.route('/restart_machine', methods=['POST'])
def restart_machine():
    machine_id = int(request.json['machine_id'])
    if machine_id in machines:
        machines[machine_id]['temp'] = np.random.normal(loc=85, scale=5)
        machines[machine_id]['pressure'] = np.random.normal(loc=135, scale=5)
        machines[machine_id]['vibration'] = np.random.normal(loc=55, scale=5)
        machines[machine_id]['degradation_rate_temp'] = np.random.uniform(-0.5, 0.5)
        machines[machine_id]['degradation_rate_pressure'] = np.random.uniform(-0.3, 0.3)
        machines[machine_id]['degradation_rate_vibration'] = np.random.uniform(-0.2, 0.2)
        machines[machine_id]['failed'] = False  # Reset the failure status
        return jsonify({"status": f"machine_{machine_id} restarted"})
    else:
        return jsonify({"error": "Invalid machine_id"}), 400

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
