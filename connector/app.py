from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import os, json, time
from threading import Thread
from datetime import datetime

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
INFLUX_USER = os.getenv("INFLUX_USER", "admin")
INFLUX_PASS = os.getenv("INFLUX_PASS", "secret123")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret123@mongo:27017/?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "mqtt_data")

# ========================
# Allowed Topics & Lines
# ========================
ALLOWED_TOPICS = {
    "iot/factory/piyawat/production_all": "factory_piyawat",
    "iot/factory/gw1/production_all": "factory_gw1",
    "iot/factory/gw2/production_all": "factory_gw2",
}
ALLOWED_LINES = {"production1", "production2"}

OPTIONAL_FIELDS = ["total", "ok", "ng", "state", "alarmcode", "measurement", "store"]
REQUIRED_METRICS = ["quality", "performance", "availability", "oee"]

QPA_MAP = {
    "Q": "quality", "%Q": "quality", "Quality": "quality",
    "P": "performance", "%P": "performance", "Performance": "performance",
    "A": "availability", "%A": "availability", "Availability": "availability",
    "OEE": "oee", "%OEE": "oee", "oee": "oee"
}

OK_MAP = {"good": "ok", "ok": "ok", "ok1": "ok", "pass": "ok", "passed": "ok", "accepted": "ok", "success": "ok"}
NG_MAP = {"ng": "ng", "ng1": "ng", "bad": "ng", "fail": "ng", "failed": "ng"}

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
def connect_influx(retries=10, delay=5):
    for i in range(retries):
        try:
            client = InfluxDBClient(
                host=INFLUX_HOST,
                port=INFLUX_PORT,
                username=INFLUX_USER,
                password=INFLUX_PASS,
                timeout=5,
                retries=3
            )
            client.get_list_database()
            print("Connected to InfluxDB successfully.")
            return client
        except Exception as e:
            print(f"InfluxDB not ready, retrying ({i+1}/{retries}): {e}")
            time.sleep(delay)
    print("Could not connect to InfluxDB.")
    return None

influx_client = connect_influx()

# ========================
# MQTT Setup
# ========================
mqtt_client = mqtt.Client()

def store_invalid(source, data, error_msg):
    doc = {
        "time": datetime.utcnow().isoformat() + "Z",
        "payload": json.dumps(data) if not isinstance(data, str) else data,
        "error": error_msg,
        "source": source
    }
    invalid_col.insert_one(doc)
    try:
        mqtt_client.publish("iot/factory/errors", json.dumps(doc))
    except Exception:
        pass
    print("Stored invalid payload:", doc)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe("iot/factory/+/production_all")
    else:
        print(f"Failed to connect to MQTT, return code {rc}")

def on_message(client, userdata, msg):
    raw_payload = msg.payload.decode(errors="ignore")
    topic = msg.topic
    try:
        payload = json.loads(raw_payload)
    except Exception:
        store_invalid(topic, raw_payload, "Payload is not valid JSON")
        return

    if topic not in ALLOWED_TOPICS:
        store_invalid(topic, payload, "Topic not allowed")
        return

    data_all = payload.get("Data", payload)
    if not isinstance(data_all, dict) or not data_all:
        store_invalid(topic, payload, "Missing or invalid 'Data' object")
        return

    influx_db_name = ALLOWED_TOPICS[topic]
    influx = influx_client
    if influx:
        try:
            influx.create_database(influx_db_name)
            influx.switch_database(influx_db_name)
        except Exception as e:
            print(f"Warning: failed to prepare InfluxDB '{influx_db_name}': {e}")

    any_stored = False
    for line, data in data_all.items():
        if line not in ALLOWED_LINES:
            store_invalid(line, data, f"Line '{line}' not allowed")
            continue
        if not isinstance(data, dict) or not data:
            store_invalid(line, data, "Empty or invalid line payload")
            continue

        normalized = {}
        for k, v in data.items():
            key_lower = k.lower()
            norm_key = QPA_MAP.get(k, k.lower())
            if key_lower in OK_MAP:
                norm_key = "ok"
            elif key_lower in NG_MAP:
                norm_key = "ng"
            normalized[norm_key] = v

        # Optional fields
        for f in OPTIONAL_FIELDS:
            normalized.setdefault(f, None)

        # Metrics - accept partial, don't reject if missing
        normalized["topic"] = topic
        normalized["received_at"] = datetime.utcnow().isoformat() + "Z"

        # MongoDB
        try:
            latest_col.update_one({}, {"$set": {line: normalized}}, upsert=True)
        except Exception as e:
            store_invalid(line, data, f"MongoDB write error: {e}")
            continue

        # InfluxDB
        if influx:
            try:
                prod_fields = {k: normalized[k] for k in OPTIONAL_FIELDS if normalized[k] is not None}
                if prod_fields:
                    influx.write_points([{
                        "measurement": line,
                        "tags": {"topic": topic, "source": "factory"},
                        "fields": prod_fields
                    }])
                for metric in REQUIRED_METRICS:
                    val = normalized.get(metric)
                    if val is not None:
                        influx.write_points([{
                            "measurement": metric,
                            "tags": {"topic": topic, "line": line},
                            "fields": {"value": val}
                        }])
            except Exception as e:
                store_invalid(line, data, f"InfluxDB write error: {e}")

        print(f"Stored valid data for {line} from topic {topic}")
        any_stored = True

    if not any_stored:
        store_invalid(topic, payload, "No valid lines stored from payload")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def mqtt_loop():
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
    doc = latest_col.find_one({}, {"_id": 0})
    if not doc:
        return {"production1": {}, "production2": {}}
    return doc

@app.get("/invalid_payloads")
def get_invalid_payloads(limit: int = 10):
    docs = list(invalid_col.find({}, {"_id": 0}).sort("time", -1).limit(limit))
    return docs

@app.get("/influx/{topic_name}")
def get_influx_data(topic_name: str, limit: int = 10):
    topic_map = {
        "gw1": "iot/factory/gw1/production_all",
        "gw2": "iot/factory/gw2/production_all",
        "piyawat": "iot/factory/piyawat/production_all"
    }
    if topic_name not in topic_map:
        return JSONResponse({"error": "Invalid topic name"}, status_code=400)
    topic = topic_map[topic_name]
    db_name = ALLOWED_TOPICS[topic]
    if influx_client is None:
        return JSONResponse({"error": "InfluxDB client not available"}, status_code=500)
    try:
        influx_client.switch_database(db_name)
        measurements = influx_client.get_list_measurements()
        result = {}
        for m in measurements:
            measurement_name = m['name']
            query = f'SELECT * FROM "{measurement_name}" ORDER BY time DESC LIMIT {limit}'
            points = list(influx_client.query(query).get_points())
            result[measurement_name] = points
        return result
    except Exception as e:
        return JSONResponse({"error": f"InfluxDB query failed: {e}"}, status_code=500)

