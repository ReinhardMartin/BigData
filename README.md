# Predictive Maintenance System
This project was developed for the Big Data Technologies 2023-2024 course as part of the master's program in Data Science at the University of Trento. The focus is on implementing a Predictive Maintenance System for industrial machinery using real-time data collection, machine learning, and big data processing to predict maintenance needs, preventing unexpected downtimes, reducing costs, and optimizing efficiency.

The system leverages IoT sensors to monitor critical machine parameters (e.g., temperature, pressure, vibration) and uses these data streams to predict when maintenance is necessary, thereby increasing uptime and reducing unplanned maintenance.

## Technologies Used
- **Apache Spark**: Train the predictive model and processes real-time data streams.
- **MongoDB**: Stores historical and new data.
- **Docker + Docker Compose**: Manages and orchestrates services.
- **Flask**: Provides the web-based User Interface.
- **MQTT (Eclipse Mosquitto)**: Manages messaging between system components.

## System Architecture
The architecture includes:

An MQTT message queue for communication.
Real-time data ingestion and processing with Spark.
MongoDB for data storage.
A Flask-based UI for visualizing predictive maintenance data.
!(images/framework.png)

## Project Structure

```.
├── UI
│   ├── Dockerfile
│   ├── app.py
│   └── templates
│       └── ...
├── consumer
│   ├── Dockerfile
│   └── consumer.py
├── historical_data
│   ├── Dockerfile
│   └── generation.py
├── mosquitto
│   ├── config
│       └── ...
│   ├── data
│       └── ...
│   └── log
│       └── ...
├── predictor
│   ├── Dockerfile
│   └── predictor.py
├── process
│   ├── Dockerfile
│   └── process.py
├── docker-compose.yml
└── README.md 
```
## Setup and Configuration
Installation
Clone the repository:

`git clone https://github.com/ReinhardMartin/BigData.git`
 
Build and run the Docker containers:

`docker-compose up --build -d`

## Usage
Access the Flask application at `http://localhost:5000`.
View real-time sensor data, equipment statuses, and predicted maintenance schedules.
![UI Interface](images/UI_interface.png)

## Components Description
- **User Interface (UI)**: Provides the front-end interface to start the stream of data and for viewing predictive maintenance results (`app.py`).
- **Consumer**: Collects incoming MQTT messages from IoT sensors and stores it in MongoDB (`consumer.py`).
- **Historical Data**: Generates and loads historical data for training (`generation.py`).
- **Mosquitto**: Handles the MQTT broker configuration, data, and logs.
- **Predictor**: Handles data processing tasks on the stream of data (`process.py`).
- **Process**: Implements machine learning models to predict the machine status (`predictor.py`).

## To Be Implemented
Enhanced Real-Time Integration: Improve real-time data procession from sensors.
Improved Machine Learning Models: Develop more advanced algorithms for better predictive accuracy.
Improve synthetic data generation: add more contextual attributes and improve data consistency.

## Dependencies da controllare
Docker v24.0.2
Docker Compose v2.18.1
Python v3.11.0
Flask v2.3.2
Paho-MQTT v1.6.1
MongoDB
Mosquitto
Ensure all dependencies are installed before running the project.

## Authors
This project was developed by Group 10 for the Big Data Technologies course:

- **Damiano Orlandi** - damiano.orlandi@studenti.unitn.it - @Damn18
- **Clelia Porcelluzzi** - clelia.porcelluzzi@studenti.unitn.it - @clelia-p
- **Martin Reinhard** - martin.reinhard@studenti.unitn.it - @ReinhardMartin
