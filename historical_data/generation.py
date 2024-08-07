import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient

# Constants
NUM_MACHINES = 25
NUM_RECORDS = 150  # Number of records to generate

# Generate timestamps
start_time = datetime(2024, 1, 1)
time_interval = timedelta(minutes=5)
timestamps = [start_time + i * time_interval for i in range(NUM_RECORDS)]

# Initialize list to hold records
records = []

# Generate data for each machine
for machine_id in range(1, NUM_MACHINES + 1):
    for timestamp in timestamps:
        # Generate sensor metrics
        temp = np.random.normal(loc=85, scale=15)  # Normal distribution for temperature
        pressure = np.random.normal(loc=135, scale=20)  # Normal distribution for pressure
        vibration = np.random.normal(loc=55, scale=10)  # Normal distribution for vibration

        # Dynamic thresholds
        lower_threshold_temp = np.random.uniform(59, 65)
        upper_threshold_temp = np.random.uniform(101, 105)

        lower_threshold_pressure = np.random.uniform(99, 105)
        upper_threshold_pressure = np.random.uniform(167, 171)

        lower_threshold_vibration = np.random.uniform(44, 46)
        upper_threshold_vibration = np.random.uniform(65, 68)

        # Determine status based on thresholds
        if (temp < lower_threshold_temp) or (temp > upper_threshold_temp) or \
           (pressure < lower_threshold_pressure) or (pressure > upper_threshold_pressure) or \
           (vibration < lower_threshold_vibration) or (vibration > upper_threshold_vibration):
            status = 'failure'
        else:
            status = 'ok'
        
        # Append record
        records.append({
            'timestamp': timestamp,
            'machine_id': machine_id,
            'temperature': temp,
            'pressure': pressure,
            'vibration': vibration,
            'status': status
        })

# Connect to MongoDB
client = MongoClient('mongodb', 27017)
db = client['maintenance']
collection = db['machine_data']

# Insert data into MongoDB
collection.insert_many(records)

# Confirm data insertion
print(f"Inserted {collection.count_documents({})} records into the 'machine_data' collection.")
client.close()