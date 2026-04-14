# Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks

Hybrid, real-time fault detection for environmental Wireless Sensor Networks (WSN), built as a final-year project with production-style API design, persistent storage, testing, and a live dashboard.

## Highlights

- 3-layer hybrid detection pipeline:
  - **Layer 1 (Rule-based)**: threshold checks
  - **Layer 2 (Cluster-based)**: z-score anomaly checks against peers
  - **Layer 3 (ML)**: Random Forest classification
- Fault types supported: `battery_low`, `link_loss`, `sensor_fail` (+ `none` for normal)
- Real-time Flask API + SQLite (WAL mode) persistence
- Dashboard with live status, fault analytics, and test console
- Full automated test suite

## System Flow

1. Sensor payload reaches `POST /sensor_data`
2. Server validates input and runs hybrid detection
3. Raw reading + detection result are stored in SQLite
4. Dashboard fetches live API data (`/status`, `/detections`, `/network_summary`)

## Repository Structure

```text
.
├── server.py                      # Flask API server
├── run.py                         # Convenience launcher
├── sensor_client.py               # Multi-node simulator client
├── config.py                      # Central configuration
├── detection_system/
│   ├── hybrid_detector.py         # 3-layer detection logic
│   └── ml_trainer.py              # Model training pipeline
├── database/
│   ├── db_manager.py              # Schema + data access
│   ├── wsn_aft_dataset.csv        # Training dataset
│   └── wsn_detections.db          # Runtime database (generated)
├── static/
│   └── dashboard.html             # Web dashboard
├── evaluation/
│   ├── generate_report.py
│   ├── ml_metrics.json
│   └── benchmark_*.{csv,json,md}
└── tests/
    ├── test_config.py
    ├── test_db_manager.py
    ├── test_hybrid_detector.py
    ├── test_server.py
    └── test_simulator.py
```

## Quick Start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Train model (first run)

```bash
python run.py train
```

### 3) Start server

```bash
python run.py server
```

Open dashboard at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

### 4) Send traffic from simulator (optional)

```bash
python run.py simulate
# or custom:
python sensor_client.py --rounds 20 --nodes 50 --rate 0.20
```

### 5) Generate evaluation report (optional)

```bash
python run.py report
```

## API Overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serve dashboard |
| `POST` | `/sensor_data` | Ingest sensor reading + return detection |
| `GET` | `/status` | Server and DB status counters |
| `GET` | `/detections` | Paginated detections |
| `GET` | `/detections/<node_id>` | Node history |
| `GET` | `/cluster/<cluster_id>` | Cluster summary |
| `GET` | `/metrics` | ML metrics JSON |
| `GET` | `/network_summary` | Aggregated network snapshot |
| `POST` | `/reset` | Clear detections/readings tables |

See full API details in `API_DOCS.md`.

## Detection Logic

### Layer 1: Rule-Based

Fast deterministic checks on:

- battery
- signal strength
- latency
- packet delivery ratio
- temperature
- humidity

### Layer 2: Cluster Statistical

Compares node metrics against peers in the same cluster using z-score.

### Layer 3: ML Classifier

Random Forest model predicts fault class probabilities from engineered features.

### Final Fusion

- Weighted confidence voting across layers
- Additional safety/consensus logic to reduce false negatives in critical cases

## Dashboard

Current tabs:

- **Overview**
- **Fault Log**
- **Analysis**
- **Test Lab**

The dashboard now uses **real API data only** (no dummy/demo data fallback). If server is offline, it shows offline/empty state.

## Test Lab (Dashboard)

Built-in validation utility lets you:

- send custom readings
- auto-fill normal/fault patterns by type
- view server response summary (`HTTP`, detected, fault type, confidence)
- inspect full JSON response payload

## Model Performance Snapshot

From benchmark artifacts in `evaluation/`:

| Rank | Model | Test Accuracy | CV Mean ± Std |
| --- | --- | ---: | ---: |
| 1 | DecisionTree | 91.11% | 90.56% ± 0.83% |
| 2 | RandomForest | 90.30% | 89.62% ± 0.71% |
| 3 | GaussianNB | 90.03% | 89.55% ± 0.62% |

Random Forest is used in runtime hybrid detection for stability and calibrated multi-class behavior.

## Testing

Run full test suite:

```bash
python -m pytest -q
```

Run specific modules:

```bash
pytest tests/test_server.py -v
pytest tests/test_hybrid_detector.py -v
pytest tests/test_db_manager.py -v
```

## Known Operational Notes

- `POST /reset` is intentionally open in current dev setup; protect it before internet exposure.
- If dashboard behavior looks stale, ensure only one server process is bound to port 5000.
- API and tests depend on model files in `models/`; run training first on a clean machine.

## Troubleshooting

- **Port in use**
  - `netstat -ano | findstr :5000`
  - `taskkill /PID <pid> /F`
- **Model not loaded**
  - `python run.py train`
- **No new dashboard data**
  - verify API counters via `python run.py status`
  - run simulator to generate traffic

## Documentation Map

- `INSTALLATION.md` - setup and environment guide
- `USER_MANUAL.md` - usage guide
- `API_DOCS.md` - endpoint-level API reference
- `PROJECT_REPORT.md` - report outline and project write-up material
- `tests/README.md` - testing strategy and conventions

## Project Context

This repository is the implementation artifact for a final-year engineering project focused on reliable and explainable WSN fault detection in environmental monitoring.
