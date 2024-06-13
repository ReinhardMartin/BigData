from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json

consumer = KafkaConsumer('sensor_data', bootstrap_servers='localhost:9092', value_deserializer=lambda m: json.loads(m.decode('utf-8')))

client = InfluxDBClient(url='http://localhost:8086', token='5t_F72Wmvoy1pjsZTzdFArKELX_EJNr2tNW82sQotPJCv86uWTxcWfaq4U-ogRVLKIeKYFr-600U34ixUu_L4Q==', org='myorg')
write_api = client.write_api(write_options=SYNCHRONOUS)

bucket = "mybucket"

for message in consumer:
    data = message.value
    point = Point("sensor_data") \
        .tag("sensor_id", data['sensor_id']) \
        .field("temperature", data['temperature']) \
        .field("humidity", data['humidity']) \
        .time(data['timestamp'], WritePrecision.MS)
    
    write_api.write(bucket=bucket, org="myorg", record=point)
    print(f"Stored data: {data}")
