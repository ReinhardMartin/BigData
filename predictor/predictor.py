import paho.mqtt.client as mqtt
from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.feature import VectorAssembler
import json
import os
import time
from filelock import FileLock, Timeout
from concurrent.futures import ThreadPoolExecutor

# Define paths
model_path = "/opt/bitnami/spark/model_data/predictive_model"
lock_path = model_path + ".lock"

def wait_for_model(model_path, lock_path, timeout=600, check_interval=10):
    """ Wait for the model file to become available and ensure it's not being updated """
    lock = FileLock(lock_path)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with lock.acquire(timeout=check_interval):
                if os.path.exists(model_path):
                    return True
        except Timeout:
            pass
        print(f"Waiting for model file at {model_path}...")
        time.sleep(check_interval)
    
    print(f"Model file not found at {model_path} after {timeout} seconds.")
    return False

# Create Spark session
spark = SparkSession.builder \
    .appName("MQTT Spark Predictor") \
    .getOrCreate()

# Wait for the model file to be available
if wait_for_model(model_path, lock_path):
    # Load the trained model
    model = RandomForestClassificationModel.load(model_path)
    print(f"Model loaded from {model_path}.")
else:
    print("Failed to load model. Exiting...")
    exit(1)

# Set up the MQTT client for publishing predictions
publish_client = mqtt.Client()

# Create a thread pool executor for parallel processing
executor = ThreadPoolExecutor(max_workers=25)  # Adjust the number of workers based on your needs

def process_message(topic, payload):
    try:
        # Convert message payload to a DataFrame
        data = json.loads(payload.decode('utf-8'))
        df = spark.read.json(spark.sparkContext.parallelize([data]))

        features = ["temperature", "pressure", "vibration"]

        assembler = VectorAssembler(inputCols=features, outputCol='features')

        df_transformed = assembler.transform(df)
        
        # Apply the model to the DataFrame
        predictions = model.transform(df_transformed)
        
        # Extract probabilities and publish them
        for row in predictions.select("machine_id", "probability").collect():
            machine_id = row["machine_id"]
            probability = row["probability"].toArray()[1]  # Assuming class index 1 is of interest
            # Publish probability to the corresponding topic
            publish_topic = f"predictions/{machine_id}"
            publish_client.publish(publish_topic, json.dumps({"probability": probability}))

        print(f"Probabilities for topic '{topic}' published successfully.")

    except Exception as e:
        print(f"Error processing message from topic '{topic}': {e}")

def on_message(client, userdata, msg):
    # Process messages in parallel using the thread pool
    executor.submit(process_message, msg.topic, msg.payload)

# Set up the MQTT client for subscribing to messages
subscribe_client = mqtt.Client()

# Define the broker address and topics
broker = "mosquitto"  # Replace with your MQTT broker address
port = 1883           # Default MQTT port
subscribe_topic = "machines/#"  # MQTT topic to subscribe to

# Set the callback function for the subscribe client
subscribe_client.on_message = on_message

# Connect to the broker and subscribe to the topic
subscribe_client.connect(broker, port, 60)
subscribe_client.subscribe(subscribe_topic)

# Connect the publish client to the broker
publish_client.connect(broker, port, 60)

# Start the loop to process messages
subscribe_client.loop_start()

# Keep the script running
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
finally:
    subscribe_client.loop_stop()
    publish_client.disconnect()
    subscribe_client.disconnect()
    executor.shutdown()  # Shutdown the thread pool executor
