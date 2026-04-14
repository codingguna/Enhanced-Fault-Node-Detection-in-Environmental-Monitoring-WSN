# Installation Guide

**Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Installation (5 minutes)](#quick-installation)
3. [Detailed Installation Steps](#detailed-installation-steps)
4. [Verifying Installation](#verifying-installation)
5. [Docker Deployment (Optional)](#docker-deployment-optional)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

---

## **Prerequisites**

### Operating Systems
- Windows 10/11 (tested)
- Linux (Ubuntu 20.04+ recommended)
- macOS 11+ (Big Sur or later)

### Software Requirements

1. **Python 3.10 or higher**
   - Download from https://www.python.org/downloads/
   - Verify: `python --version` or `python3 --version`
   - Must include pip (Python package installer)

2. **Git** (for cloning repository)
   - Windows: https://git-scm.com/download/win
   - Linux: `sudo apt-get install git`
   - macOS: `brew install git`
   - Verify: `git --version`

3. **7-Zip** or built-in archive tools (for extracting downloads)

### Optional (for development)
- **VS Code** or **PyCharm** IDE
- **pytest** for running test suite
- **Docker** for containerized deployment

---

## **Quick Installation (5 minutes)**

For experienced users, here's the fastest way to get started:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Enhanced-Fault-Node-Detection-in-Environmental-Monitoring-WSN.git
cd Enhanced-Fault-Node-Detection-in-Environmental-Monitoring-WSN

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train ML model (first time only)
python run.py train

# 4. Start server
python run.py server

# 5. In another terminal, start simulator
python run.py simulate

# 6. Open browser to http://127.0.0.1:5000/
```

That's it! The system should be running.

---

## **Detailed Installation Steps**

### Step 1: Obtain the Source Code

#### Option A: Clone the Repository (Recommended)
```bash
# Navigate to your desired directory
cd ~/Documents  # or D:\Projects on Windows

# Clone the repository
git clone https://github.com/yourusername/Enhanced-Fault-Node-Detection-in-Environmental-Monitoring-WSN.git

# Navigate into project directory
cd Enhanced-Fault-Node-Detection-in-Environmental-Monitoring-WSN
```

#### Option B: Download ZIP Archive
1. Click the green "Code" button on GitHub repository page
2. Select "Download ZIP"
3. Extract to desired location
4. Open terminal/command prompt in the extracted folder

### Step 2: Verify Python Installation

Open terminal (PowerShell, CMD, Bash, or PowerShell) and run:

```bash
python --version
# or on some systems
python3 --version
```

**Expected output**: `Python 3.10.x` or higher

If not installed:
- Download from https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation (Windows)

### Step 3: Install Python Dependencies

```bash
# From project root directory
pip install -r requirements.txt
```

**What gets installed:**
- Flask (web framework)
- pandas (data processing)
- numpy (numerical operations)
- scikit-learn (machine learning)
- joblib (model persistence)
- requests (HTTP client for simulator)
- matplotlib (charting for reports)

**Verify installation:**
```bash
pip list | grep -E "(Flask|pandas|numpy|scikit-learn|joblib|requests|matplotlib)"
```

Should show all packages with versions.

### Step 4: Initialize Database & Train Model

The `run.py` script automates everything:

```bash
# This will:
# 1. Check that ML models exist
# 2. If missing, run training automatically
# 3. Start Flask server
python run.py server
```

**Alternative: Manual training**
```bash
# Train ML model separately (takes 30-60 seconds)
python -m detection_system.ml_trainer

# Expected output:
# ============================================================
#   WSN ML Fault Classifier - Training Pipeline
# ============================================================
# Dataset: 1854 rows x 19 features
# ...
# Test Accuracy: 90.30%
# ...
# [OK] Model saved -> models/fault_classifier.pkl
```

**Output files created:**
- `models/fault_classifier.pkl` - Trained Random Forest
- `models/label_encoder.pkl` - Label encoder
- `models/scaler.pkl` - Feature scaler
- `evaluation/ml_metrics.json` - Performance metrics
- `database/wsn_detections.db` - SQLite database (auto-created)

### Step 5: Test the Installation

Once server is running (from Step 4), open another terminal:

```bash
# Check server status
python run.py status

# Expected output:
#   Server Status
#   ----------------------------------------
#   server          : WSN Hybrid Fault Detection Server
#   version         : 2.0
#   ml_model_loaded : True
#   total_detections: 0
#   ...
```

---

## **Verifying Installation**

### Automated Verification Script

Run the included verification script:

```bash
python verify_fix.py
```

**Expected output:**
```
[HybridDetector] [OK] ML model loaded successfully.
Detection Result: (JSON with fault_detected: false)

Verifying types:
fault_detected type: <class 'bool'>
confidence type: <class 'float'>

[OK] Verification successful: Result is JSON serializable.
```

### Manual Checks

**1. Test API endpoint:**
```bash
# Server must be running
curl http://127.0.0.1:5000/status | python -m json.tool
```

**2. Submit test sensor data:**
```bash
curl -X POST http://127.0.0.1:5000/sensor_data \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": 1,
    "cluster_id": 1,
    "battery_level": 85.5,
    "signal_strength": -65.0,
    "temperature": 25.0,
    "humidity": 50.0,
    "latency_ms": 100.0,
    "pdr": 0.95,
    "data_redundancy_flag": 0,
    "data_packet_size": 256,
    "energy_consumed_mJ": 0.5,
    "optimized_path_flag": 1,
    "load_on_node": 0.6,
    "recovery_time_ms": 0.0,
    "transmission_success": 1
  }' | python -m json.tool
```

**3. Open dashboard:**
- Navigate to http://127.0.0.1:5000/ in web browser
- Should see interactive dashboard with charts

---

## **Docker Deployment (Optional)**

If you prefer containerized deployment:

### Build Docker Image

```dockerfile
# Dockerfile (create this in project root)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 5000

# Command to run
CMD ["python", "server.py"]
```

Build and run:

```bash
# Build image
docker build -t wsn-fault-detection:v1.0 .

# Run container
docker run -p 5000:5000 wsn-fault-detection:v1.0

# Train model first (if needed)
docker run -v $(pwd)/models:/app/models wsn-fault-detection:v1.0 python run.py train
```

**Note**: The first run will take time to train the model. Mount volumes to persist data.

---

## **Troubleshooting**

### Issue: "Python not found" or "pip command not recognized"

**Solution**:
- Python not added to PATH. Reinstall Python and check "Add Python to PATH"
- Or use full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe -m pip install -r requirements.txt`

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution**:
```bash
pip install -r requirements.txt
# or install individually
pip install flask pandas numpy scikit-learn
```

### Issue: "UnicodeEncodeError" on Windows when running server

**Solution**: This has been fixed in the codebase. Ensure you're using the latest version. If still occurring:
```bash
set PYTHONIOENCODING=utf-8
python server.py
```

### Issue: Port 5000 already in use

**Solution**:
```bash
# Change port in config.py
SERVER = {
    'host': '0.0.0.0',
    'port': 5001,  # Change this
    'debug': False,
}

# Or kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
sudo lsof -ti:5000 | xargs kill -9
```

### Issue: "Model files not found" error

**Solution**: Train the model first:
```bash
python run.py train
# or
python -m detection_system.ml_trainer
```

### Issue: Database locked or "database is locked" errors

**Solution**:
- SQLite WAL mode is enabled, but if other processes are accessing DB, they may conflict
- Ensure no other instances of server running
- Delete `database/wsn_detections.db-wal` and `database/wsn_detections.db-shm` if present (temporary WAL files)
- Restart server

### Issue: Slow performance or high CPU usage

**Check**:
- Number of simulator nodes: reduce with `--nodes 20` flag
- Check for infinite loops in simulator
- Enable debug mode: `debug=True` in config.py (slows performance)

### Issue: "Connection refused" when running simulator

**Solution**:
- Ensure server is running first: `python run.py server`
- Check server URL in config: `SIMULATION['server_url']`
- Server must be at http://127.0.0.1:5000 by default

### Issue: Tests failing

**Solution**:
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run only failing test with verbose output
pytest tests/test_hybrid_detector.py::TestLayer1RuleBased::test_battery_low_fault -v

# Clean up __pycache__ and retry
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

### Issue: Import errors after file moves

**Solution**:
```bash
# Ensure Python can find modules
python -c "import sys; sys.path.insert(0, '.'); import detection_system.hybrid_detector"
# Should output nothing or "[HybridDetector] [OK]..."
```

### Platform-Specific Notes

**Windows**:
- Use PowerShell or Git Bash for better Unix-like commands
- Avoid spaces in project path (use `D:\Projects\wsn` not `D:\My Documents\...`)
- Python 3.12 may need Visual C++ Build Tools for some packages (usually automatic)

**Linux**:
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-dev build-essential
```

**macOS**:
```bash
# Install Homebrew if needed, then Python
brew install python3
# Or use system Python
python3 --version
```

---

## **Uninstallation**

To remove the project:

```bash
# Simply delete the project folder
rm -rf Enhanced-Fault-Node-Detection-in-Environmental-Monitoring-WSN

# Or on Windows, delete in Explorer/Files
```

**Note**: This does not remove Python packages installed globally. To remove those:

```bash
# Create a requirements list and uninstall
pip freeze > installed_packages.txt
# Review file, then:
pip uninstall -r installed_packages.txt -y
# Or manually:
pip uninstall flask pandas numpy scikit-learn joblib requests matplotlib -y
```

Virtual environments are recommended to avoid polluting global Python (see next section).

---

## **Recommended: Use Virtual Environment**

To avoid dependency conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

---

## **Next Steps**

After successful installation:

1. **Run the full system**:
   ```bash
   python run.py all
   ```

2. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Generate benchmark**:
   ```bash
   python benchmark_models.py
   ```

4. **Read the User Manual**: [USER_MANUAL.md](USER_MANUAL.md)

5. **Review API docs**: [API_DOCS.md](API_DOCS.md)

6. **Start developing**: Modify code in `detection_system/`, `server.py`, etc.

---

## **Support**

- **Issues**: https://github.com/yourusername/Enhanced-Fault-Node-Detection-in-Environmental-Monitoring-WSN/issues
- **Documentation**: See `README.md`, `PROJECT_REPORT.md`
- **Email**: your.email@example.com

---

**Last Updated**: April 2025  
**Version**: 2.0
