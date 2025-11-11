from fastapi import FastAPI
from pymongo import MongoClient
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import os, json, time
from threading import Thread
from datetime import datetime

from webhook_routes import router as webhook_router

# ========================
# App Initialization
# ========================
app = FastAPI()

# ========================
# Configuration
# ========================
MQTT_BROKER = os.getenv("MQTT_BROKER", "emqx")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
INFLUX_HOST = os.getenv("INFLUX_HOST", "influxdb")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", 8086))
INFLUX_DB = os.getenv("INFLUX_DB", "mqtt_data")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret123@mongo:27017/?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "mqtt_data")

# ========================
# MongoDB Setup
# ========================
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
latest_col = mongo_db["latest_production"]
invalid_col = mongo_db["invalid_payloads"]
print("Connected to MongoDB successfully.")

# ========================
# InfluxDB Setup
# ========================
def connect_influx():
    for i in range(10):
        try:
            client = InfluxDBClient(
                host=INFLUX_HOST,
                port=INFLUX_PORT,
                username="admin",
                password="secret123",
                database=INFLUX_DB
            )
            client.create_database(INFLUX_DB)
            print("Connected to InfluxDB successfully.")
            return client
        except Exception as e:
            print(f"InfluxDB not ready, retrying ({i+1}/10): {e}")
            time.sleep(5)
    print("Could not connect to InfluxDB after retries.")
    return None

influx_client = connect_influx()

# ========================
# MQTT Setup
# ========================
mqtt_client = mqtt.Client()

def store_invalid(line, data, error_msg):
    """Store invalid payloads in MongoDB and publish to MQTT error topic"""
    doc = {
        "time": datetime.utcnow().isoformat() + "Z",
        "payload": json.dumps(data),
        "error": error_msg,
        "source": line
    }
    invalid_col.insert_one(doc)
    mqtt_client.publish("iot/factory/errors", json.dumps(doc))
    print(f"Stored invalid payload: {doc}")

# --- Include the Webhook Endpoints ---
# This line adds all the routes from webhook_routes.py
# All routes will be prefixed with /logs
app.include_router(webhook_router, prefix="/logs")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe("iot/factory/production2")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """Process incoming MQTT messages, normalize, validate, and store"""
    try:
        payload = json.loads(msg.payload.decode())
        data = payload.get("Data", payload)

        # Determine production line
        if any(k.endswith("1") for k in data.keys()):
            line = "production1"
        elif any(k.endswith("2") for k in data.keys()):
            line = "production2"
        else:
            line = "production2"

        # Key normalization mapping
        key_map = {
            "state": ["state"],
            "ok": ["ok", "good"],
            "ng": ["ng", "not good", "not okay"],
            "total": ["total"],
            "alarmcode": ["alarmcode", "alarm_code"],
            "measurement": ["measurement"],
            "store": ["store"],
            "quality": ["quality", "q"],
            "performance": ["performance", "p"],
            "availability": ["availability", "a"]
        }

        # Normalize keys
        normalized = {}
        for target_key, variants in key_map.items():
            for k in data.keys():
                if k.lower() in [v.lower() for v in variants]:
                    normalized[target_key] = data[k]
                    break
            if target_key not in normalized:
                normalized[target_key] = 0  # default if missing

        # Validate numeric fields
        numeric_fields = ["ok", "ng", "state", "total", "alarmcode",
                          "measurement", "store", "quality", "performance", "availability"]
        for field in numeric_fields:
            value = normalized.get(field)
            if not isinstance(value, (int, float)):
                try:
                    normalized[field] = float(value)
                except Exception:
                    store_invalid(line, data, f"invalid {field} value: {value}")
                    return

        # Write to MongoDB
        latest_col.update_one({}, {"$set": {line: normalized}}, upsert=True)

        # Write to InfluxDB
        if influx_client:
            # Production metrics
            influx_client.write_points([{
                "measurement": line,
                "tags": {"source": "factory"},
                "fields": {k: normalized[k] for k in ["state","total","ok","ng","alarmcode","measurement","store"]}
            }])

            # Quality, Performance, Availability
            for metric in ["quality", "performance", "availability"]:
                influx_client.write_points([{
                    "measurement": metric,
                    "tags": {"source": "factory", "line": line},
                    "fields": {"value": normalized[metric]}
                }])

        print(f"Stored valid data for {line}: {normalized}")

    except Exception as e:
        print(f"Error processing message: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def mqtt_loop():
    """MQTT connection loop with reconnect"""
    while True:
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
            mqtt_client.loop_forever()
        except Exception as e:
            print(f"MQTT connection error: {e}")
            time.sleep(5)

Thread(target=mqtt_loop, daemon=True).start()

# ========================
# FastAPI Routes
# ========================
@app.get("/latest/mongo")
def get_latest_mongo():
    """Return latest data from MongoDB"""
    doc = latest_col.find_one({}, {"_id": 0})
    return doc or {"production1": {}, "production2": {}}

@app.get("/latest/influx")
def get_latest_influx(limit: int = 10):
    """Return latest points from InfluxDB"""
    if not influx_client:
        return {"error": "InfluxDB not connected"}

    result = {"production1": [], "production2": [], "quality": [], "performance": [], "availability": []}
    try:
        # Production metrics
        for line in ["production1", "production2"]:
            q = f'SELECT * FROM "{line}" ORDER BY time DESC LIMIT {limit}'
            res = list(influx_client.query(q).get_points())
            result[line] = res

        # Quality, Performance, Availability
        for metric in ["quality", "performance", "availability"]:
            q = f'SELECT * FROM "{metric}" ORDER BY time DESC LIMIT {limit}'
            res = list(influx_client.query(q).get_points())
            result[metric] = res

    except Exception as e:
        print(f"InfluxDB query error: {e}")

    return result

@app.get("/invalid_payloads")
def get_invalid_payloads(limit: int = 10):
    """Return latest invalid payloads from MongoDB"""
    docs = list(invalid_col.find({}, {"_id": 0}).sort("time", -1).limit(limit))
    return docs
