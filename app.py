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

PRODUCTION_TOPICS = ["iot/factory/production1", "iot/factory/production2"]

REQUIRED_FIELDS = {
    "production1": ["Total1", "OK1", "NG1", "State1", "AlarmCode1", "Measurement1", "Store1"],
    "production2": ["Total2", "OK2", "NG2", "State2", "AlarmCode2", "Measurement2", "Store2"]
}

ALL_FIELDS = set([
    "Total1","OK1","NG1","State1","AlarmCode1","Measurement1","Store1",
    "Total2","OK2","NG2","State2","AlarmCode2","Measurement2","Store2",
    "Quality","Performance","Availability"
])

# Mapping Q/P/A variants
QPA_MAP = {
    "Q": "Quality", "P": "Performance", "A": "Availability",
    "%Q": "Quality", "%P": "Performance", "%A": "Availability"
}

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

# Include webhook routes
app.include_router(webhook_router, prefix="/logs")

# ------------------------
# MQTT Handlers
# ------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        for topic in PRODUCTION_TOPICS:
            client.subscribe(topic)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    if topic not in PRODUCTION_TOPICS:
        print(f"Ignored message on unknown topic: {topic}")
        return

    try:
        payload = json.loads(msg.payload.decode())
        data = payload.get("Data", payload)
        line = "production1" if "1" in topic else "production2"

	 # ----------------------
        # Empty payload check
        # ----------------------
        if not data or all(v in (None, {}) for v in data.values()):
            store_invalid(line, data, "Empty payload")
            return

        # Normalize Q/P/A variants
        data = { QPA_MAP.get(k, k): v for k,v in data.items() }

        # Detect invalid keys
        invalid_keys = set(data.keys()) - ALL_FIELDS
        if invalid_keys:
            store_invalid(line, data, f"Contains invalid keys: {invalid_keys}")
            return

        # Check for missing required fields
        missing_fields = [f for f in REQUIRED_FIELDS[line] if f not in data]
        if missing_fields and any(f in data for f in REQUIRED_FIELDS[line]):
            store_invalid(line, data, f"Missing required fields: {missing_fields}")
            return

        # Normalize fields
        normalized = {}
        # Numeric production metrics
        for field_map in zip(["Total","OK","NG","State","AlarmCode","Measurement","Store"],
                             REQUIRED_FIELDS[line]):
            norm_field, data_field = field_map
            normalized[norm_field.lower()] = data.get(data_field, 0)
        # Q/P/A metrics
        for metric in ["Quality","Performance","Availability"]:
            normalized[metric.lower()] = data.get(metric, 0)

        # Validate numeric fields
        for key, value in normalized.items():
            if not isinstance(value, (int, float)):
                try:
                    normalized[key] = float(value)
                except Exception:
                    store_invalid(line, data, f"Invalid {key} value: {value}")
                    return

        # Write to MongoDB
        latest_col.update_one({}, {"$set": {line: normalized}}, upsert=True)

        # Write to InfluxDB (if connected)
        if influx_client:
            # Only write production numeric metrics if present
            if any(data.get(f) is not None for f in REQUIRED_FIELDS[line]):
                influx_client.write_points([{
                    "measurement": line,
                    "tags": {"source": "factory"},
                    "fields": {k: normalized[k] for k in ["state","total","ok","ng","alarmcode","measurement","store"]}
                }])
            # Always write Q/P/A metrics
            for metric_name in ["quality", "performance", "availability"]:
                influx_client.write_points([{
                    "measurement": metric_name,
                    "tags": {"source": "factory", "line": line},
                    "fields": {"value": normalized[metric_name]}
                }])

        print(f"Stored valid data for {line}: {normalized}")

    except Exception as e:
        line = line if 'line' in locals() else "unknown"
        store_invalid(line, data, f"Error processing message: {e}")

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

    result = {
        "production1": [], "production2": [],
        "quality": {"production1": [], "production2": []},
        "performance": {"production1": [], "production2": []},
        "availability": {"production1": [], "production2": []}
    }
    try:
        for line in ["production1", "production2"]:
            q = f'SELECT * FROM "{line}" ORDER BY time DESC LIMIT {limit}'
            res = list(influx_client.query(q).get_points())
            result[line] = res
        for metric in ["quality", "performance", "availability"]:
            for line in ["production1", "production2"]:
                q = f'SELECT * FROM "{metric}" WHERE "line"=\'{line}\' ORDER BY time DESC LIMIT {limit}'
                res = list(influx_client.query(q).get_points())
                result[metric][line] = res
    except Exception as e:
        print(f"InfluxDB query error: {e}")

    return result

@app.get("/invalid_payloads")
def get_invalid_payloads(limit: int = 10):
    """Return latest invalid payloads from MongoDB"""
    docs = list(invalid_col.find({}, {"_id": 0}).sort("time", -1).limit(limit))
    return docs
