from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Mongo-Spark") \
    .config("spark.mongodb.read.connection.uri", "mongodb://mongodb:27017/maintenance.machine_data") \
    .config("spark.mongodb.write.connection.uri", "mongodb://mongodb:27017/maintenance.machine_data") \
    .getOrCreate()

# Read from MongoDB
mongodf = spark.read.format("mongodb").option("collection", "machine_data") \
    .option("database", "maintenance") \
    .load()

# Show Data
mongodf.show()
