from fastapi import FastAPI
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from datetime import datetime
import json
import threading
import os


MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = "iot/factory/production2"
MQTT_USER = os.getenv("MQTT_USER", "pi")
MQTT_PASS = os.getenv("MQTT_PASS", "raspberry")

INFLUX_HOST = os.getenv("INFLUX_HOST", "127.0.0.1")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", "8086"))
INFLUX_DB = os.getenv("INFLUX_DB", "mqtt_data")

MONGO_DB = os.getenv("MONGO_DB", "mongodb://127.0.0.1:27017/server")

influx_client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
influx_client.create_database(INFLUX_DB)
influx_client.switch_database(INFLUX_DB)


def write_to_influx(topic: str, payload: dict):
    try:
        data_point = [
            {
                "measurement": "mqtt_measurement",
                "tags": {"topic": topic},
                "time": datetime.utcnow().isoformat(),
                "fields": payload,
            }
        ]
        influx_client.write_points(data_point)
        print(f"✅ Data written to InfluxDB: {payload}")
    except Exception as e:
        print(f"⚠️ Failed to write to InfluxDB: {e}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"🚀 Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"❌ MQTT Connection failed with code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📥 Received message on {msg.topic}: {payload}")
        write_to_influx(msg.topic, payload)
    except Exception as e:
        print(f"⚠️ Error processing MQTT message: {e}")


def start_mqtt():
    client = mqtt.Client()
    # Add username/password for authentication
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()


app = FastAPI(title="MQTT → InfluxDB v1 (Auth)")


@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_mqtt, daemon=True).start()


@app.get("/")
def home():
    return {
        "status": "running",
        "mqtt_broker": MQTT_BROKER,
        "mqtt_topic": MQTT_TOPIC,
        "influx_db": INFLUX_DB,
    }


@app.get("/latest")
def latest_data():
    try:
        query = "SELECT * FROM mqtt_measurement ORDER BY time DESC LIMIT 5"
        result = influx_client.query(query)
        return list(result.get_points())
    except Exception as e:
        return {"error": str(e)}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
