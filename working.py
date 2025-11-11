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
app = FastAPI(title="Factory MQTT + Influx + Mongo Gateway")

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
print("✅ Connected to MongoDB successfully.")

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
            print("✅ Connected to InfluxDB successfully.")
            return client
        except Exception as e:
            print(f"InfluxDB not ready, retrying ({i+1}/10): {e}")
            time.sleep(5)
    print("❌ Could not connect to InfluxDB after retries.")
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
        "payload": data,
        "error": error_msg,
        "source": line
    }
    invalid_col.insert_one(doc)
    mqtt_client.publish("iot/factory/errors", json.dumps(doc))
    print(f"❌ Stored invalid payload: {doc}")

# Include webhook routes
app.include_router(webhook_router, prefix="/logs")

# ------------------------
# Expected ranges
# ------------------------
RANGES = {
    "state": (0, 10),
    "total": (0, 10000),
    "ok": (0, 10000),
    "ng": (0, 10000),
    "alarmcode": (0, 100),
    "measurement": (0, 10000),
    "store": (0, 5000),
    "quality": (0, 100),
    "performance": (0, 100),
    "availability": (0, 100)
}

# ------------------------
# MQTT Handlers
# ------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe("iot/factory/production2")
    else:
        print(f"❌ Failed to connect MQTT, return code {rc}")

def on_message(client, userdata, msg):
    """Process incoming MQTT messages, validate, normalize, and store"""
    try:
        payload = json.loads(msg.payload.decode())
        data = payload.get("Data", payload)

        # Determine production line
        line = "production2" if any(k.endswith("2") for k in data.keys()) else "production1"

        # Normalize data
        normalized = {
            "total": data.get("Total1", data.get("Total2", 0)),
            "ok": data.get("OK1", data.get("OK2", 0)),
            "ng": data.get("NG1", 0) + data.get("NG2", 0) + data.get("Bad", 0),
            "state": data.get("State1", data.get("State2", 0)),
            "alarmcode": data.get("AlarmCode1", data.get("AlarmCode2", 0)),
            "measurement": data.get("Measurement1", data.get("Measurement2", 0)),
            "store": data.get("Store1", data.get("Store2", 0)),
            "quality": data.get("Quality", data.get("Q", 0)),
            "performance": data.get("Performance", data.get("P", 0)),
            "availability": data.get("Availability", data.get("A", 0))
        }

        # Validate numeric fields and ranges
        for field, (min_val, max_val) in RANGES.items():
            value = normalized.get(field, 0)
            try:
                value = float(value)
                if not (min_val <= value <= max_val):
                    raise ValueError(f"{field} value {value} out of range ({min_val}-{max_val})")
                normalized[field] = value
            except Exception as e:
                store_invalid(line, data, str(e))
                return

        # Write to MongoDB
        latest_col.update_one({}, {"$set": {line: normalized}}, upsert=True)

        # Write to InfluxDB
        if influx_client:
            influx_client.write_points([{
                "measurement": line,
                "tags": {"source": "factory"},
                "fields": {k: normalized[k] for k in ["state","total","ok","ng","alarmcode","measurement","store"]}
            }])
            for metric in ["quality", "performance", "availability"]:
                influx_client.write_points([{
                    "measurement": metric,
                    "tags": {"source": "factory", "line": line},
                    "fields": {"value": normalized[metric]}
                }])

        print(f"✅ Stored valid data for {line}: {normalized}")

    except Exception as e:
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
