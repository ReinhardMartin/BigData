from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.sql.functions import when, col
import shutil
import os
import time

def retrain_model():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("Mongo-Spark Retrain") \
        .config("spark.mongodb.read.connection.uri", "mongodb://mongodb:27017/maintenance.machine_data") \
        .getOrCreate()

    try:
        # Read from MongoDB
        df = spark.read.format("mongodb") \
            .option("collection", "machine_data") \
            .option("database", "maintenance") \
            .load()

        # Drop MongoDB _id column
        df = df.drop("_id")

        # Convert 'status' column to numeric: 0 for "ok" and 1 for "failure"
        df = df.withColumn("status", when(col("status") == "failure", 1).otherwise(0))

        # Define feature columns and assemble them into a single 'features' column
        feature_cols = ["temperature", "vibration", "pressure"]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

        # Transform the DataFrame to include the 'features' column
        df = assembler.transform(df)

        # Define the RandomForest model
        rf = RandomForestClassifier(labelCol="status", featuresCol="features")

        # Train the model
        model = rf.fit(df)

        # Paths for saving the model
        temp = "/opt/bitnami/spark/model_data/predictive_model_temp"
        model_path = "/opt/bitnami/spark/model_data/predictive_model"

        # Remove the temporary directory if it exists
        if os.path.exists(temp):
            shutil.rmtree(temp)

        # Save the model to the temporary directory
        model.write().overwrite().save(temp)

        # Move the model to the final directory
        if os.path.exists(model_path):
            shutil.rmtree(model_path)

        shutil.move(temp, model_path)

        print(f"Model saved to {model_path}")

    except Exception as e:
        print(f"Error during model retraining: {e}")

    finally:
        # Stop the Spark session
        spark.stop()

if __name__ == "__main__":
    try:
        while True:
            retrain_model()
            print("Waiting for the next retraining...")
            time.sleep(60)  # Sleep for 1 day (86400 seconds)

    except KeyboardInterrupt:
        print("Manual interrupt received, stopping the retraining process.")
