# IIoT Gateway Connection System

A comprehensive Industrial Internet of Things (IIoT) data connector system that enables real-time monitoring and visualization of factory production metrics through MQTT messaging and Grafana dashboards.

## 🎯 Overview

This system provides a complete solution for connecting industrial gateways to a central data collection and visualization platform. It handles data ingestion from multiple production lines, normalizes varying data formats, and provides role-based access to monitoring dashboards.

## ✨ Features

- **MQTT-based Data Ingestion**: Real-time data collection from multiple IIoT gateways
- **Flexible Schema Normalization**: Automatic mapping of various field naming conventions
- **Multi-Gateway Support**: Concurrent connections from multiple production lines
- **Error Handling & Logging**: Robust validation with automatic error reporting
- **Role-Based Visualization**: Grafana dashboards with configurable access permissions
- **Topic-Based Routing**: UUID-based routing ensures data isolation and security

## 🏗️ Architecture

```
IIoT Gateway → MQTT Broker (Port 1883) → Data Connector → MongoDB → Grafana Dashboards
```

### Key Components

- **MQTT Broker**: Message broker for gateway communication
- **Data Connector**: Backend service for data validation and normalization
- **MongoDB**: Database for storing production metrics and invalid payloads
- **Grafana**: Web-based visualization and analytics platform

## 🚀 Getting Started

### Prerequisites

- MQTT broker (Mosquitto recommended)
- MongoDB database
- Grafana instance
- Node.js (if applicable for the data connector)

### Network Configuration

Configure your gateway client with these connection parameters:

| Parameter | Value | Description |
|-----------|-------|-------------|
| MQTT Broker Host | `192.168.1.137` | Local server IP address |
| MQTT Broker Port | `1883` | Standard MQTT TCP port |
| Security Protocol | Username/Password | Credential-based authentication |

## 🔐 Authentication

### Gateway Credentials

| Device Name | Username | Password | MQTT Topic |
|-------------|----------|----------|------------|
| Piyawat Gateway | `piyawat@gmail.com` | `password123` | `691c1f4c2b2333b7705b88f8/iot/factory/piyawat/production_all` |
| Gateway 1 | `gateway1@gmail.com` | `password123` | `691c1f162b2333b7705b88f2/iot/factory/gw1/production_all` |
| Gateway 2 | `gateway2@gmail.com` | `password123` | `691c1f252b2333b7705b88f4/iot/factory/gw2/production_all` |

### Grafana Access

**URL**: `http://192.168.1.137:3000`

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin/Evaluator | `professor` | `234Cy&<G7Mwh0y6J` | Full system access |
| Operator 1 | `gateway1` | `gateway1` | Gateway 1 data only |
| Operator 2 | `gateway2` | `gateway2` | Gateway 2 data only |

## 📊 Data Format

### JSON Payload Structure

The system expects JSON payloads with production line data:

```json
{
  "Data": {
    "production1": {
      "total": 100,
      "ok": 95,
      "ng": 5,
      "quality": 95.0,
      "performance": 92.0,
      "availability": 98.0,
      "oee": 85.0,
      "state": "1"
    },
    "production2": {
      "total": 200,
      "ok": 190,
      "ng": 10,
      "quality": 95.0,
      "performance": 88.0,
      "availability": 97.0
    }
  }
}
```

### Supported Fields

The system automatically normalizes field names from various formats:

| Standard Key | Accepted Aliases | Description |
|--------------|------------------|-------------|
| `ok` | ok, ok1, good, pass, passed, success | Successful products count |
| `ng` | ng, ng1, bad, fail, failed | Non-compliant products count |
| `quality` | quality, Q, %Q | Quality percentage |
| `performance` | performance, P, %P | Performance percentage |
| `availability` | availability, A, %A | Availability percentage |
| `oee` | oee, OEE, %OEE | Overall Equipment Effectiveness |
| `total` | total | Total production count |
| `state` | state | Operational state (RUNNING/IDLE) |
| `alarmcode` | alarmcode | Active alarm codes |

## 🧪 Testing

### Quick Test Commands

Test the system using mosquitto_pub commands:

**Standard Data Ingestion:**
```bash
mosquitto_pub -h 192.168.1.137 -p 1883 \
  -u "gateway2@gmail.com" -P "password123" \
  -t "691c1f252b2333b7705b88f4/iot/factory/gw2/production_all" \
  -m '{"Data": {"production1": {"total": 100, "ok": 95, "ng": 5, "quality": 95}}}'
```

**Partial Update (Quality Only):**
```bash
mosquitto_pub -h 192.168.1.137 -p 1883 \
  -u "piyawat@gmail.com" -P "password123" \
  -t "691c1f4c2b2333b7705b88f8/iot/factory/piyawat/production_all" \
  -m '{"Data": {"production1": {"quality": 96}}}'
```

**Using Field Aliases:**
```bash
mosquitto_pub -h 192.168.1.137 -p 1883 \
  -u "piyawat@gmail.com" -P "password123" \
  -t "691c1f4c2b2333b7705b88f8/iot/factory/piyawat/production_all" \
  -m '{"Data": {"production2": {"Good": 950, "ng": 40, "Q": 95.0, "%P": 97.0}}}'
```

## ⚠️ Error Handling

The system provides comprehensive error handling:

- **Invalid JSON**: Rejected and logged to `invalid_payloads` collection
- **Wrong Topic**: Data not processed, error logged to `iot/factory/errors`
- **Invalid Line Keys**: Payload rejected if production line keys are incorrect
- **Notification**: All errors published to the error topic for monitoring

## 📁 Project Structure

```
├── data-connector/        # Backend data processing service
├── config/               # Configuration files
├── grafana-dashboards/   # Dashboard definitions
├── test-scripts/         # Testing utilities
└── docs/                # Documentation
```

## 🛠️ Configuration

1. Update the MQTT broker IP address in your configuration
2. Set up MongoDB connection string
3. Configure Grafana data source
4. Import dashboard templates
5. Add gateway credentials to authentication system

## 📝 Usage Example

### Publishing from Python

```python
import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.username_pw_set("piyawat@gmail.com", "password123")
client.connect("192.168.1.137", 1883)

payload = {
    "Data": {
        "production1": {
            "total": 300,
            "ok": 290,
            "ng": 10,
            "quality": 95,
            "performance": 92,
            "availability": 97,
            "oee": 94
        }
    }
}

client.publish(
    "691c1f4c2b2333b7705b88f8/iot/factory/piyawat/production_all",
    json.dumps(payload)
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

[Specify your license here]

## 👥 Authors

[Add your name and contact information]

## 🙏 Acknowledgments

- Professor and evaluators for system requirements
- Gateway operators for testing and feedback

## 📧 Support

For questions or issues, please open an issue in the GitHub repository or contact the maintainers.

---

**Note**: Remember to use real passwords and credentials before deploying to production environments.
