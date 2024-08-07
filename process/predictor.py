import paho.mqtt.client as mqtt
from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.feature import VectorAssembler
import json

# Create Spark session
spark = SparkSession.builder \
    .appName("MQTT Spark Predictor") \
    .getOrCreate()

# Load the trained model
model_path = "/opt/bitnami/spark/model_data/predictive_model"  # Path where the model is saved in the container
model = RandomForestClassificationModel.load(model_path)

# Define the callback for when a message is received
def on_message(client, userdata, msg):
    # Convert message payload to a DataFrame
    data = json.loads(msg.payload.decode('utf-8'))
    df = spark.read.json(spark.sparkContext.parallelize([data]))

    features = ["sensor1", "sensor2", "sensor3"]

    assembler = VectorAssembler(inputCols=features, outputCol='features')

    df_transformed = assembler.transform(df)
    
    # Apply the model to the DataFrame
    predictions = model.transform(df_transformed)
    
    # Show the predictions
    predictions.show()

# Set up the MQTT client
client = mqtt.Client()

# Define the broker address and topic
broker = "mosquitto"  # Replace with your MQTT broker address
port = 1883                     # Default MQTT port
topic = "machines/#"            # Replace with the topic you want to subscribe to

# Set the callback function
client.on_message = on_message

# Connect to the broker
client.connect(broker, port, 60)

# Subscribe to the topic
client.subscribe(topic)

# Start the loop to process messages
client.loop_forever()
