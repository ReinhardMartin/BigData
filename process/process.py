from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.sql.functions import when, col

spark = SparkSession.builder \
    .appName("Mongo-Spark") \
    .config("spark.mongodb.read.connection.uri", "mongodb://mongodb:27017/maintenance.machine_data") \
    .getOrCreate()

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

# Save the model
model_path = "/opt/bitnami/spark/model_data/predictive_model"
model.write().overwrite().save(model_path)

print(f"Model saved to {model_path}")

# Stop the Spark session
spark.stop()