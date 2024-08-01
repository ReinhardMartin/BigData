import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json

# MQTT settings
MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883
MQTT_TOPIC = 'machines/#'

# MongoDB settings
MONGO_HOST = 'mongodb'
MONGO_PORT = 27017
MONGO_DB = 'mqtt_data'
MONGO_COLLECTION = 'messages'

# MongoDB client setup
mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# MQTT client setup
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Received message from topic {msg.topic}")
    message = json.loads(msg.payload.decode('utf-8'))
    collection.insert_one({
        "topic": msg.topic,
        "message": message
    })
    print(f"Stored message in MongoDB: {message}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
