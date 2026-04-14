# API Documentation

**Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks - REST API Reference**

**Version**: 2.0  
**Base URL**: `http://127.0.0.1:5000`  
**Content-Type**: `application/json`  
**Authentication**: None (development only)

---

## **Overview**

This API provides endpoints for:
- Submitting sensor data for fault detection
- Querying detection history and network status
- Retrieving ML model metrics
- Administrative operations (reset database)

All endpoints are **stateless** and return JSON. CORS is enabled for browser-based clients.

---

## **Base URL Patterns**

| Environment | Host | Port |
|-------------|------|------|
| Development | 127.0.0.1 | 5000 |
| Production | configurable | 80/443 |

Change host/port in `config.py` → `SERVER`.

---

## **Endpoint Reference**

### **1. Dashboard**

**`GET /`**

Serves the interactive HTML dashboard.

**Response**: HTML document (text/html)

**Example**:
```bash
curl http://127.0.0.1:5000/ -o dashboard.html
```

---

### **2. Server Status**

**`GET /status`**

Get server health, statistics, and model status.

**Response** (application/json):
```json
{
  "server": "WSN Hybrid Fault Detection Server",
  "version": "2.0",
  "timestamp": "2024-12-15T14:35:00.123456",
  "ml_model_loaded": true,
  "active_clusters": 3,
  "total_detections": 1452,
  "total_faults": 207,
  "total_readings": 1452,
  "fault_rate": 0.1426,
  "last_reading": "2024-12-15T14:34:59.987654"
}
```

**Fields**:
- `ml_model_loaded`: Whether Random Forest model is loaded (required for Layer 3)
- `active_clusters`: Number of clusters with recent activity
- `total_detections`, `total_faults`, `total_readings`: Cumulative counts
- `fault_rate`: `total_faults / total_detections` (0-1)
- `last_reading`: ISO 8601 timestamp of most recent reading

---

### **3. Submit Sensor Reading**  *(Primary Endpoint)*

**`POST /sensor_data`**

Submit sensor node data for fault detection. Returns detection result immediately.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body** (all fields required unless noted):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `node_id` | int | yes | Unique node identifier (1-50) |
| `cluster_id` | int | yes | Cluster number (1-5) |
| `battery_level` | float | yes | Battery % (0-100) |
| `signal_strength` | float | yes | RSSI dBm (-30 to -100 typical) |
| `temperature` | float | yes | °C (typically -40 to 85) |
| `humidity` | float | yes | Relative humidity % (0-100) |
| `data_redundancy_flag` | int | yes | 0 or 1 |
| `data_packet_size` | int | yes | Bytes (64-512 typical) |
| `latency_ms` | float | yes | Latency in milliseconds |
| `energy_consumed_mJ` | float | yes | Energy usage in mJ |
| `optimized_path_flag` | int | yes | 0 or 1 |
| `load_on_node` | float | yes | Load factor (0.0-1.0) |
| `recovery_time_ms` | float | yes | Recovery time (usually 0) |
| `pdr` | float | yes | Packet delivery ratio (0.0-1.0) |
| `transmission_success` | int | yes | 0 (failure) or 1 (success) |

**Example Request**:
```bash
curl -X POST http://127.0.0.1:5000/sensor_data \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": 12,
    "cluster_id": 3,
    "battery_level": 8.5,
    "signal_strength": -62.0,
    "temperature": 28.4,
    "humidity": 55.2,
    "data_redundancy_flag": 0,
    "data_packet_size": 214,
    "latency_ms": 88.5,
    "energy_consumed_mJ": 0.342,
    "optimized_path_flag": 1,
    "load_on_node": 0.61,
    "recovery_time_ms": 0.0,
    "pdr": 0.934,
    "transmission_success": 1
  }'
```

**Response** (200 OK):
```json
{
  "status": "ok",
  "detection": {
    "node_id": 12,
    "cluster_id": 3,
    "timestamp": "2024-12-15T14:32:07.123456",
    "fault_detected": true,
    "fault_type": "battery_low",
    "confidence": 0.7246,
    "layers": {
      "rule_based": {
        "fault": true,
        "fault_type": "battery_low",
        "confidence": 0.92,
        "reason": "Battery 8.5% < 15.0%"
      },
      "cluster": {
        "fault": false,
        "fault_type": "none",
        "confidence": 0.0,
        "reason": ""
      },
      "ml_model": {
        "fault": true,
        "fault_type": "battery_low",
        "confidence": 0.81,
        "reason": "RF: battery_low @ 81.0%",
        "probabilities": {
          "battery_low": 0.81,
          "link_loss": 0.04,
          "none": 0.09,
          "sensor_fail": 0.06
        }
      }
    },
    "node_metrics": {
      "battery_level": 8.5,
      "signal_strength": -62.0,
      "temperature": 28.4,
      "humidity": 55.2,
      "latency_ms": 88.5,
      "pdr": 0.934,
      "energy_consumed_mJ": 0.342
    }
  }
}
```

**Detection Result Fields**:
- `fault_detected`: Boolean - was any fault found?
- `fault_type`: One of `"none"`, `"battery_low"`, `"link_loss"`, `"sensor_fail"`
- `confidence`: Weighted vote score (0.0-1.0)
- `layers`: Results from each detection layer
- `node_metrics`: Echo of submitted values (for verification)

**Error Responses**:
- `400 Bad Request`:
  ```json
  {"error": "Request body must be JSON"}
  ```
- `422 Unprocessable Entity`:
  ```json
  {"error": "Missing required fields: ['battery_level', 'pdr']"}
  ```

---

### **4. List Detections**

**`GET /detections`**

Paginated list of all detection records.

**Query Parameters**:

| Parameter | Type | Default | Range/Notes |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | 1 to 500 (max) |
| `offset` | integer | 0 | Must be >= 0 |
| `fault_only` | boolean | false | `true` or `false` (string) |

**Examples**:
```bash
# First 100 records
curl "http://127.0.0.1:5000/detections"

# Records 20-39 (20 records)
curl "http://127.0.0.1:5000/detections?limit=20&offset=20"

# Only faults
curl "http://127.0.0.1:5000/detections?fault_only=true"
```

**Response** (200 OK):
```json
{
  "total": 1452,
  "limit": 100,
  "offset": 0,
  "data": [
    {
      "id": 1452,
      "node_id": 12,
      "cluster_id": 3,
      "timestamp": "2024-12-15T14:32:07.123456",
      "fault_detected": 1,
      "fault_type": "battery_low",
      "confidence": 0.7246,
      "layer1_fault": 1,
      "layer1_type": "battery_low",
      "layer1_reason": "Battery 8.5% < 15.0%",
      "layer2_fault": 0,
      "layer2_type": null,
      "layer2_reason": "",
      "layer3_fault": 1,
      "layer3_type": "battery_low",
      "layer3_reason": "RF: battery_low @ 81.0%",
      "battery_level": 8.5,
      "signal_strength": -62.0,
      "temperature": 28.4,
      "humidity": 55.2,
      "latency_ms": 88.5,
      "pdr": 0.934,
      "energy_mj": 0.342,
      "raw_json": "{...}"  // Full detection result JSON
    }
  ]
}
```

**Implementation Notes**:
- Records ordered by `id DESC` (most recent first)
- `layer_*_type` and `layer_*_reason` may be `NULL` if layer did not flag fault
- `raw_json` contains complete detection result (can be large)

---

### **5. Node Detection History**

**`GET /detections/<node_id>`**

Get all detections for a specific node.

**Path Parameter**:
- `node_id` (integer): Node identifier

**Query Parameters**:
- `limit` (integer, default 50): Maximum records to return

**Example**:
```bash
curl "http://127.0.0.1:5000/detections/12?limit=20"
```

**Response** (200 OK):
```json
{
  "node_id": 12,
  "history": [
    {
      "id": 1452,
      "cluster_id": 3,
      "timestamp": "2024-12-15T14:32:07.123456",
      "fault_detected": 1,
      "fault_type": "battery_low",
      "confidence": 0.7246,
      ...
    }
  ]
}
```

---

### **6. Cluster Summary**

**`GET /cluster/<cluster_id>`**

Get aggregated statistics for all nodes in a cluster.

**Path Parameter**:
- `cluster_id` (integer): Cluster number (1-5)

**Example**:
```bash
curl "http://127.0.0.1:5000/cluster/3" | python -m json.tool
```

**Response** (200 OK):
```json
{
  "cluster_id": 3,
  "nodes": [
    {
      "node_id": 21,
      "readings": 1452,
      "faults": 23,
      "avg_battery": 87.34,
      "avg_latency": 105.2,
      "avg_pdr": 0.945,
      "last_seen": "2024-12-15T14:34:59.123"
    },
    {
      "node_id": 22,
      "readings": 1452,
      "faults": 5,
      "avg_battery": 92.12,
      "avg_latency": 98.7,
      "avg_pdr": 0.956,
      "last_seen": "2024-12-15T14:34:58.987"
    }
  ]
}
```

**Fields**:
- `readings`: Total detections for this node
- `faults`: Count of fault_detected = 1
- `avg_battery`, `avg_latency`, `avg_pdr`: Averages over all readings
- `last_seen`: Most recent timestamp

---

### **7. ML Metrics**

**`GET /metrics`**

Load model performance metrics from `evaluation/ml_metrics.json` (generated by training).

**Response**:
- `200 OK` with JSON if file exists
- `404 Not Found` if model not yet trained

**Example**:
```bash
curl http://127.0.0.1:5000/metrics | python -m json.tool
```

**Response**:
```json
{
  "accuracy": 0.903,
  "cv_mean": 0.8962,
  "cv_std": 0.0071,
  "rule_based_accuracy": 0.7244,
  "improvement": 0.1786,
  "classes": ["battery_low", "link_loss", "none", "sensor_fail"],
  "per_class": {
    "battery_low": {
      "precision": 0.35,
      "recall": 0.3889,
      "f1": 0.3684,
      "support": 18
    },
    ...
  },
  "confusion_matrix": [[...]],
  "feature_importance": {
    "recovery_time_ms": 0.3429,
    "energy_ratio": 0.0565,
    ...
  }
}
```

---

### **8. Network Summary**

**`GET /network_summary`**

Comprehensive network-wide statistics.

**Response** (200 OK):
```json
{
  "fault_distribution": [
    {"fault_type": "battery_low", "count": 87},
    {"fault_type": "link_loss", "count": 65},
    {"fault_type": "sensor_fail", "count": 23},
    {"fault_type": "none", "count": 1277}
  ],
  "node_states": [
    {
      "node_id": 12,
      "cluster_id": 3,
      "last_seen": "2024-12-15T14:34:59.123",
      "avg_battery": 78.45,
      "total_faults": 23,
      "total_readings": 1452,
      "last_fault_type": "battery_low"
    }
  ],
  "hourly_stats": [
    {"hour": "13", "total": 320, "faults": 42},
    {"hour": "14", "total": 452, "faults": 64},
    ...
  ]
}
```

**Usage**:
- Dashboard loads this for network overview
- Used for trend analysis and reporting

---

### **9. Reset Database**

**`POST /reset`**

Delete all detections and sensor readings. Schema remains.

**Use Cases**:
- Clear old data before new test
- Reset statistics for demo

**Response** (200 OK):
```json
{
  "status": "reset complete",
  "timestamp": "2024-12-15T14:40:00.123456"
}
```

**Warning**: This is irreversible. Ensure data is backed up if needed.

---

## **Common Patterns**

### Python Client Example

```python
import requests
import json

BASE = "http://127.0.0.1:5000"

# Submit reading
payload = {
    "node_id": 1, "cluster_id": 1, "battery_level": 85.5,
    "signal_strength": -65.0, "temperature": 25.0, "humidity": 50.0,
    "latency_ms": 100.0, "pdr": 0.95,
    "data_redundancy_flag": 0, "data_packet_size": 256,
    "energy_consumed_mJ": 0.5, "optimized_path_flag": 1,
    "load_on_node": 0.6, "recovery_time_ms": 0.0,
    "transmission_success": 1
}
r = requests.post(f"{BASE}/sensor_data", json=payload)
result = r.json()
print(f"Fault detected: {result['detection']['fault_detected']}")

# Get status
r = requests.get(f"{BASE}/status")
print(r.json()['fault_rate'])

# Query faults
r = requests.get(f"{BASE}/detections?fault_only=true&limit=50")
faults = r.json()['data']
```

### JavaScript Client Example

```javascript
// Submit reading
async function submitReading(data) {
  const response = await fetch('http://127.0.0.1:5000/sensor_data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await response.json();
}

// Get status (with interval polling)
setInterval(async () => {
  const data = await fetch('http://127.0.0.1:5000/status').then(r => r.json());
  updateDashboard(data);
}, 2000);
```

---

## **Rate Limiting & Throttling**

Currently **no rate limiting**. For production deployment, consider:
- Flask-Limiter extension
- Reverse proxy (nginx) rate limiting
- API gateway

Recommended limits for 50-node WSN:
- Max 100 requests/minute per IP
- Burst up to 200 requests

---

## **Error Handling**

All errors return JSON with `error` key:

**400 Bad Request**:
```json
{"error": "Invalid JSON"}
```

**422 Unprocessable Entity**:
```json
{"error": "Missing required fields: ['battery_level']"}
```

**500 Internal Server Error**:
```json
{"error": "ML model error: ..."}
```

**503 Service Unavailable**:
Returned when ML model not loaded and set to strict mode (not default).

HTTP status codes follow standard conventions.

---

## **CORS Support**

CORS headers are automatically added to all responses:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

This allows browser-based clients from any origin.

---

## **OpenAPI/Swagger Specification**

A full OpenAPI 3.0 spec is available in `docs/openapi.yaml` (to be generated).

Third-party tools like Postman can import this for testing.

---

## **Testing the API**

### Using curl
```bash
# Health check
curl -i http://127.0.0.1:5000/status

# Submit reading
curl -i -X POST http://127.0.0.1:5000/sensor_data \
  -H "Content-Type: application/json" \
  -d @sample_payload.json

# Get faults
curl -s "http://127.0.0.1:5000/detections?fault_only=true" | jq '.data[] | {node, type: .fault_type, conf: .confidence}'
```

### Using Postman/Insomnia
1. Create new request
2. Set URL and method
3. Add headers as needed
4. Set raw JSON body
5. Send and view formatted response

### Using Python pytest
See `tests/test_server.py` for integration test examples.

---

## **Versioning**

API is version 2.0 (see `server.py` docstring). Breaking changes increment major version.

Current stable version: **2.0**

Deprecated endpoints (if any) will return `410 Gone` with deprecation notice in response body.

---

## **Performance Characteristics**

| Endpoint | P50 Latency | P95 Latency | Notes |
|----------|-------------|-------------|-------|
| POST /sensor_data | 120ms | 180ms | Includes detection (ML model predict) |
| GET /status | 15ms | 30ms | Simple DB query |
| GET /detections | 25ms | 50ms | Depends on limit |
| GET /metrics | 5ms | 10ms | File read |
| POST /reset | 50ms | 80ms | Clears both tables |

*Measured on development machine (Intel i5, 8GB RAM, SSD)*

---

## **Production Considerations**

Before deploying to production:

1. **Replace Flask dev server** with Gunicorn or uWSGI:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 server:app
   ```

2. **Add authentication**:
   - API keys
   - JWT tokens
   - OAuth 2.0

3. **Enable HTTPS**:
   - Use nginx as reverse proxy with SSL termination
   - Let's Encrypt for free certificates

4. **Database backup strategy**:
   - Periodic SQLite backups
   - Consider PostgreSQL for larger deployments

5. **Logging**:
   - Configure structured logging
   - Centralize logs (ELK stack, Datadog)

6. **Monitoring**:
   - Prometheus metrics endpoint
   - Alert on fault rate spikes

7. **Load testing**:
   - Use locust or k6 to simulate 100+ nodes
   - Optimize DB indexes if needed

---

## **Changelog**

**Version 2.0** (April 2025)
- Initial release
- 3-layer hybrid detection
- Full REST API with 9 endpoints
- Interactive dashboard
- Multi-threaded server

---

**End of API Documentation**

For questions or issues, see project README or open GitHub issue.
