# User Manual

**Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [System Overview](#system-overview)
3. [Running the System](#running-the-system)
4. [Using the Dashboard](#using-the-dashboard)
5. [API Reference](#api-reference)
6. [Sensor Simulator](#sensor-simulator)
7. [Monitoring & Analysis](#monitoring--analysis)
8. [Administration](#administration)
9. [FAQ](#faq)
10. [Glossary](#glossary)

---

## **1. Getting Started**

### What is This System?

The **Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks** system monitors wireless sensor networks for node failures and anomalies. It combines:

- **Rule-based checks** (hard thresholds like battery < 15%)
- **Statistical cluster analysis** (Z-score comparison with neighboring nodes)
- **Machine Learning** (Random Forest classifier)

And produces **90.3% accuracy**—a 17.86% improvement over rules alone.

### Who Uses This?

- **Network Operators**: Monitor real-time health of WSN deployments
- **Researchers**: Study fault patterns and detection algorithms
- **Developers**: Integrate fault detection into larger systems via API
- **Students**: Learn about ML, WSNs, and real-time systems

### Minimum Requirements

- Python 3.10+
- 1GB RAM minimum (4GB recommended)
- 100MB disk space
- Internet connection for initial package installation

---

## **2. System Overview**

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                           │
│  • Web Dashboard (http://127.0.0.1:5000/)                   │
│  • REST API (JSON over HTTP)                                │
│  • CLI Tools (run.py)                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    WSN HUB (Flask Server)                   │
│                                                             │
│   ┌─────────────────┐  ┌─────────────────┐                │
│   │  Sensor Input   │→ │  3-Layer        │ → Database     │
│   │  (POST JSON)    │  │  Detector       │                │
│   └─────────────────┘  └─────────────────┘                │
│                                                             │
│   ┌─────────────────┐  ┌─────────────────┐                │
│   │  Query API      │← │  SQLite DB      │                │
│   │  (GET /status)  │  │  (wsn_detections│                │
│   └─────────────────┘  │     .db)         │                │
│                         └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                           │
                  ┌────────┴────────┐
                  │  Simulator       │
                  │  (50 nodes,      │
                  │   fault inject) │
                  └──────────────────┘
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Real-time Detection** | <200ms latency per sensor reading |
| **3 Detection Layers** | Rules + Statistics + ML for robust detection |
| **Web Dashboard** | Interactive charts, network topology, alerts |
| **Historical Queries** | Retrieve past detections by node/cluster/time |
| **Multi-threaded** | Handles concurrent sensor submissions |
| **Extensible** | Add new algorithms via plugin architecture |

---

## **3. Running the System**

### 3.1 One-Command Startup

The easiest way to launch everything:

```bash
python run.py all
```

This will:
1. Ask if you want to train the ML model (Yes on first run)
2. Open **2 terminal windows**:
   - Window 1: Flask server
   - Window 2: Sensor simulator (50 nodes, 15% fault rate)
3. Open web browser to dashboard automatically

Press `Ctrl+C` in each terminal to stop.

### 3.2 Manual Startup (More Control)

**Terminal 1 - Start the server:**
```bash
python run.py server
```

Output:
```
======================================================
  Smart Hybrid Fault Node Detection Server  v2.0
  http://127.0.0.1:5000
  Dashboard -> http://127.0.0.1:5000/
======================================================
 * Serving Flask app 'server'
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**Terminal 2 - Start the simulator:**
```bash
python run.py simulate
```

Or customize:
```bash
python sensor_client.py --rounds 10 --nodes 30 --rate 0.20 --interval 3.0
```

Parameters:
- `--rounds`: Number of simulation rounds (0 = infinite, default)
- `--nodes`: Number of sensor nodes (default: 50)
- `--rate`: Fault injection rate 0.0-1.0 (default: 0.15 = 15%)
- `--interval`: Seconds between rounds (default: 2.0)
- `--url`: Server URL (default: http://127.0.0.1:5000/sensor_data)

Example simulation output:
```
========================================================
  WSN Sensor Node Simulator
  Nodes: 50   Clusters: 5
  Fault rate: 15%   Interval: 2.0s
  Server: http://127.0.0.1:5000/sensor_data
========================================================
[Round    1] 14:30:22 - dispatching 50 readings  [OK] (faults this round: 8)
[Round    2] 14:30:24 - dispatching 50 readings  [OK] (faults this round: 7)
...
```

**Terminal 3 - Monitor (optional):**
```bash
python run.py status
```

### 3.3 Command Reference

| Command | Description |
|---------|-------------|
| `python run.py train` | Train the ML model (required first time) |
| `python run.py server` | Start Flask server only |
| `python run.py simulate` | Start sensor simulator |
| `python run.py report` | Generate evaluation charts |
| `python run.py status` | Check if server is running |
| `python run.py all` | Train + server + simulator (interactive) |
| `pytest tests/` | Run test suite |

---

## **4. Using the Dashboard**

### 4.1 Accessing the Dashboard

Open browser to: **http://127.0.0.1:5000/**

The dashboard auto-refreshes every 2 seconds with live data.

### 4.2 Dashboard Sections

#### **A. Top Stats Bar**
Shows current system status:
- Total Detections (total readings processed)
- Active Clusters (1-5)
- Fault Rate (percentage of faulty detections)
- ML Status (Loaded/Not Loaded)
- Last Update time

#### **B. Tabs**

**1. Dashboard (Home)**
- **Network Map**: Visual representation of 50 nodes across 5 clusters
  - Green nodes = Healthy
  - Red nodes = Fault detected
  - Yellow = Suspected (overlapping detections)
  - Gray = No data yet
- Hover over nodes to see detailed metrics

**2. Fault Log**
Table of recent detections:
- Timestamp, Node ID, Cluster ID
- Fault Type (battery_low, link_loss, sensor_fail, none)
- Confidence (0.0-1.0)
- Layer breakdown (rule, cluster, ML)
- Action buttons to view full details

**3. Metrics**
- Accuracy vs Rule-Based baseline
- Confusion matrix heatmap
- Per-class precision/recall/F1
- ROC curves (if multiclass supported)

**4. Analysis**
- Fault distribution by cluster
- Fault type breakdown (pie chart)
- Detection timeline (line chart)
- Battery/Signal/PDR trends

### 4.3 Interacting with the Dashboard

**View Node Details**:
- Click on a node in the network map
- Modal popup shows:
  - Current readings (battery, signal, temp, humidity...)
  - Recent history (last 10 detections)
  - Detection reason from each layer

**Filter Fault Log**:
- Use search box to filter by node_id or fault_type
- Toggle "Show only faults" checkbox
- Change page size (10, 25, 50, 100)

**Export Data**:
- Click "Download CSV" to export visible table rows
- Data saved to Downloads folder

---

## **5. API Reference**

### Base URL
```
http://127.0.0.1:5000/
```

### Authentication
Currently **no authentication** (development mode only). For production, add API keys or OAuth.

---

### **GET /** - Dashboard

**Description**: Serves the main HTML dashboard page

**Response**: HTML document

**Example**:
```bash
curl http://127.0.0.1:5000/
# Opens dashboard in browser or returns HTML source
```

---

### **POST /sensor_data** - Submit Sensor Reading

**Description**: Submit a sensor node reading for fault detection. Core functionality.

**Required Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `node_id` | integer | Unique node identifier (1-50) |
| `cluster_id` | integer | Cluster number (1-5) |
| `battery_level` | float | Battery percentage (0.0-100.0) |
| `signal_strength` | float | RSSI in dBm (typical -30 to -100) |
| `temperature` | float | Temperature in Celsius (expected: 10-55) |
| `humidity` | float | Humidity percentage (0-100) |
| `latency_ms` | float | Communication latency in milliseconds |
| `pdr` | float | Packet Delivery Ratio (0.0-1.0) |
| `data_redundancy_flag` | integer (0/1) | Data redundancy enabled |
| `data_packet_size` | integer | Packet size in bytes |
| `energy_consumed_mJ` | float | Energy consumed in millijoules |
| `optimized_path_flag` | integer (0/1) | Using optimized routing |
| `load_on_node` | float | Current load (0.0-1.0) |
| `recovery_time_ms` | float | Recovery time (usually 0) |
| `transmission_success` | integer (0/1) | Transmission success flag |

**Request Example**:
```json
{
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
}
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

**Error Responses**:
- `400 Bad Request`: Invalid JSON body
- `422 Unprocessable Entity`: Missing required fields (list in `error` field)

---

### **GET /status** - Server Health

**Description**: Get server statistics and health status

**Response** (200 OK):
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

---

### **GET /detections** - Query Detections

**Description**: Paginated list of all detection records

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Max records (1-500) |
| `offset` | integer | 0 | Number of records to skip |
| `fault_only` | boolean | false | If true, return only fault detections |

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
      "raw_json": "{...}"
    }
  ]
}
```

---

### **GET /detections/<node_id>** - Node History

**Description**: Get all detections for a specific node

**Path Parameter**:
- `node_id` (integer): Node identifier

**Query Parameters**:
- `limit` (integer, default 50): Max records to return

**Response** (200 OK):
```json
{
  "node_id": 12,
  "history": [ /* array of detection records */ ]
}
```

---

### **GET /cluster/<cluster_id>** - Cluster Summary

**Description**: Get summary statistics for all nodes in a cluster

**Path Parameter**:
- `cluster_id` (integer): Cluster number (1-5)

**Response** (200 OK):
```json
{
  "cluster_id": 3,
  "nodes": [
    {
      "node_id": 11,
      "readings": 1452,
      "faults": 23,
      "avg_battery": 78.45,
      "avg_latency": 110.2,
      "avg_pdr": 0.934,
      "last_seen": "2024-12-15T14:34:59.123"
    }
  ]
}
```

---

### **GET /metrics** - ML Performance Metrics

**Description**: Load model performance metrics from evaluation report

**Response**:
- `200 OK`: JSON metrics if file exists
- `404 Not Found`: If model not trained yet

**Example Response**:
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
    }
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

### **GET /network_summary** - Full Network Snapshot

**Description**: Comprehensive network-wide statistics

**Response** (200 OK):
```json
{
  "fault_distribution": [
    {"fault_type": "battery_low", "count": 87},
    {"fault_type": "link_loss", "count": 65},
    {"fault_type": "sensor_fail", "count": 23}
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
    {
      "hour": "14",
      "total": 452,
      "faults": 64
    }
  ]
}
```

---

### **POST /reset** - Clear Database

**Description**: Delete all detections and sensor readings (does not drop tables)

**Response** (200 OK):
```json
{
  "status": "reset complete",
  "timestamp": "2024-12-15T14:40:00.123456"
}
```

**Use cases**:
- Start fresh test run
- Clear old data before demo
- Reset statistics

---

## **6. Sensor Simulator**

### How the Simulator Works

The `sensor_client.py` simulates 50 wireless sensor nodes distributed across 5 clusters:

1. **Baseline behavior**: Each node has baseline temperature, humidity, and battery
2. **Natural variation**: Gaussian noise added to readings
3. **Battery drain**: Drain per round (0.05-0.30%)
4. **Fault injection**: Based on `fault_rate` probability:
   - `battery_low`: Force battery drop to 2-14%
   - `link_loss`: Degrade signal, PDR, latency, transmission
   - `sensor_fail`: Extreme temperature/humidity values

### Simulator Configuration

Edit `config.py` → `SIMULATION`:

```python
SIMULATION = {
    'num_nodes': 50,           # Total simulated nodes
    'num_clusters': 5,         # Clusters 1-5
    'fault_rate': 0.15,        # 15% faults per round
    'round_interval': 2.0,     # Seconds between batches
    'thread_workers': 10,      # Concurrent HTTP requests
    'server_url': 'http://127.0.0.1:5000/sensor_data',
}
```

### Using the Simulator

**Quick start**:
```bash
python run.py simulate
```

**Custom simulation**:
```bash
python sensor_client.py \
  --rounds 100 \
  --nodes 30 \
  --rate 0.25 \
  --interval 1.5 \
  --url http://127.0.0.1:5000/sensor_data
```

**Simulator output explained**:
```
[Round   1] 14:30:22 - dispatching 50 readings  [OK] (faults this round: 8)
│         │            │                       │
│         │            │                       └─ Number of faults injected
│         │            └─ HTTP requests sent to server
│         └─ Round number and timestamp
└─ Indicates successful submission (✗ if failed)
```

Every 5 rounds, statistics are printed:
```
  === Stats after 5 rounds ===
    Readings sent   : 250
    Faults injected : 41
    Faults detected : 38
```

---

## **7. Monitoring & Analysis**

### Checking System Health

**Server Status**:
```bash
python run.py status
```

**Dashboard**:
Visit http://127.0.0.1:5000/ → Dashboard tab → Top stats bar

**Live Logs**:
- Server logs to console (stdout/stderr) and Flask default logger
- Each POST to `/sensor_data` prints: `Data Received: {...}`

### Querying Data

**All detections (with filtering)**:
```bash
curl "http://127.0.0.1:5000/detections?limit=50&fault_only=true"
```

**Specific node**:
```bash
curl "http://127.0.0.1:5000/detections/42?limit=20"
```

**Cluster summary**:
```bash
curl "http://127.0.0.1:5000/cluster/3"
```

**Export to file**:
```bash
curl "http://127.0.0.1:5000/detections?limit=1000" > detections.json
python -m json.tool detections.json > detections_pretty.json
```

### Performance Monitoring

**Check response times**:
```bash
time curl -X POST http://127.0.0.1:5000/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"node_id": 1, ...}' > /dev/null
```

Should be <200ms.

**Database size**:
```bash
ls -lh database/wsn_detections.db
# Grows ~1KB per 100 detections
```

**Memory usage** (server):
- Monitor via Task Manager (Windows) or `htop` (Linux)
- Typically <150MB for normal operation

---

## **8. Administration**

### Resetting the System

**Clear all data** (keep schema):
```bash
# Method 1: API
curl -X POST http://127.0.0.1:5000/reset

# Method 2: Python
python -c "from database.db_manager import reset_db; reset_db()"
```

**Delete database file**:
```bash
rm database/wsn_detections.db
# Server will recreate automatically on next insert
```

### Backing Up Data

**Export all detections**:
```bash
python -c "
import sqlite3, json
conn = sqlite3.connect('database/wsn_detections.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT * FROM detections').fetchall()
data = [dict(row) for row in rows]
with open('backup_detections.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f'Exported {len(data)} records')
"
```

**Copy database file**:
```bash
# Simple copy (must stop server first)
cp database/wsn_detections.db backup_20250403.db
```

### Retraining the Model

If you want to retrain with different parameters:

```bash
# Edit config.py - ML settings
# Then:
python -m detection_system.ml_trainer
```

New model will automatically be used by server on next request.

---

## **9. FAQ**

### General Questions

**Q: What's the difference between `run.py` and `server.py`?**  
A: `run.py` is a convenience launcher with multiple commands. `server.py` runs only the Flask server. Use `run.py` for ease.

**Q: Can I use real sensor data instead of simulator?**  
A: Yes! POST real sensor JSON to `/sensor_data`. Ensure required fields match. See API docs.

**Q: How many nodes can this handle?**  
A: Current implementation: ~50 nodes, 5 clusters. Can scale to 200+ with proper hardware. Beyond that, consider database sharding and load balancing.

**Q: Is this production-ready?**  
A: For prototype/development: YES. For high-scale production: Requires WSGI server (Gunicorn), reverse proxy (nginx), proper logging, monitoring, and security hardening.

**Q: Why is my detection accuracy different from report?**  
A: Accuracy depends on data distribution, fault injection patterns, and random variation. The 90.3% is from held-out test set. Runtime may vary.

---

### Troubleshooting FAQ

**Q: Server won't start - "Address already in use"**  
A: Port 5000 is occupied. Change `SERVER['port']` in `config.py` or kill existing process.

**Q: ML model fails to load**  
A: Run `python run.py train` first. Check `models/` directory for `.pkl` files.

**Q: Dashboard not updating**  
A: Check browser console (F12). CORS errors mean server not running or wrong URL. Refresh page.

**Q: High CPU usage**  
A: Simulator default is 50 nodes × 2s intervals = 25 req/sec. Reduce nodes or increase interval.

**Q: Tests failing**  
A: Ensure database is clean. Run `pytest tests/ -v --tb=short` for details.

---

## **10. Glossary**

| Term | Definition |
|------|------------|
| **WSN** | Wireless Sensor Network - distributed sensors communicating wirelessly |
| **Fault Detection** | Process of identifying malfunctioning nodes or sensors |
| **Hybrid Detection** | Combining multiple detection techniques (rules, stats, ML) |
| **Cluster** | Group of geographically nearby nodes (5 clusters × 10 nodes each) |
| **Z-Score** | Statistical measure of how many standard deviations from mean |
| **Random Forest** | Ensemble ML method using multiple decision trees |
| **REST API** | HTTP API following Representational State Transfer principles |
| **Flask** | Python web framework |
| **SQLite** | Lightweight file-based database |
| **Cross-validation** | Technique to evaluate model generalizability |
| **Precision/Recall** | Evaluation metrics for classification |
| **Feature Engineering** | Creating new features from raw data to improve ML |

---

## **Getting Help**

- **Documentation**: See `README.md`, `PROJECT_REPORT.md`, `INSTALLATION.md`
- **API Details**: See `API_DOCS.md`
- **Code Examples**: See `tests/` directory
- **Issues**: https://github.com/yourusername/Enhanced-Fault-Node-Detection-in-Environmental-Monitoring-WSN/issues

---

**Version**: 2.0  
**Last Updated**: April 2025  
**For**: BE-IT Final Year Project
