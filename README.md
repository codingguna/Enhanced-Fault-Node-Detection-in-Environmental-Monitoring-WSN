# Real-Time Hybrid Fault Detection System for Environmental Monitoring WSN

## 📌 Abstract (Five Key Points)

1. This project implements a real-time hybrid fault detection system for Environmental Monitoring Wireless Sensor Networks (WSNs).
2. It simulates multiple sensor node faults including hard, soft, intermittent, energy, and communication faults.
3. A continuously running Python backend server receives live sensor data and performs hybrid fault detection.
4. Detected faults are classified by type and stored persistently for monitoring and analysis.
5. A Streamlit dashboard provides real-time visualization of sensor readings and detected faults.

---

## 📖 Introduction

Wireless Sensor Networks (WSNs) are widely used in environmental monitoring applications such as temperature tracking, forest fire detection, and air quality monitoring. Sensor nodes deployed in remote areas are prone to various faults including hardware failure, energy depletion, abnormal readings, and communication issues.

This project presents a real-time hybrid fault detection system that simulates environmental sensor nodes, injects multiple fault types, detects faults using node-level and cluster-level logic, and visualizes detected faults using a live dashboard.

The system closely models real-world WSN gateway architecture with backend processing and frontend monitoring.

---

## 🧠 Proposed Methodology

The system operates in four major stages:

1. **Sensor Simulation (Testing Environment)**
   - Deploys virtual sensor nodes
   - Injects faults randomly
   - Generates environmental data continuously

2. **Real-Time Backend Server**
   - Receives sensor data via HTTP
   - Runs hybrid detection logic
   - Classifies fault types
   - Stores detected faults

3. **Hybrid Fault Detection**
   - Node-level detection (hard & energy faults)
   - Cluster-level detection (soft & intermittent faults)
   - Communication fault detection (timeout-based)
   - Centralized confirmation mechanism

4. **Streamlit Dashboard**
   - Displays live sensor data
   - Shows detected faulty nodes and their types
   - Provides monitoring interface

---

## 🛠️ Tech Stack

- **Programming Language:** Python 3.8+
- **Backend Server:** Flask
- **Frontend Dashboard:** Streamlit
- **Data Handling:** CSV (pandas)
- **Communication:** HTTP (REST API)
- **Libraries Used:**
  - Flask
  - Streamlit
  - Requests
  - Pandas

---

## ⚙️ How to Install and Run the Project

### Step 1: Clone or Download Project

`
git clone <your-repo-url>
`
`
cd WSN_RealTime_Hybrid_Project
`

Or download and extract manually.

---

### Step 2: Create Virtual Environment (Recommended)

`
python -m venv venv
`

Activate it:

**Windows:**
`
venv\Scripts\activate
`

**Linux / Mac:**
`
source venv/bin/activate
`

---

### Step 3: Install Dependencies

`
pip install -r requirements.txt
`

---

### Step 4: Run Backend Server

Open Terminal 1:

`
python server.py

Server will start at:

http://127.0.0.1:5000
`

---

### Step 5: Run Sensor Client (Simulation)

Open Terminal 2:

`
python sensor_client.py
`

This starts sending live sensor data to server.

---

### Step 6: Run Streamlit Dashboard

Open Terminal 3:

`
streamlit run dashboard.py
`

Open browser and go to:

`
http://localhost:8501
`

You will see:

- Live sensor readings
- Detected faulty nodes
- Fault types
- Energy levels

---

## 📊 Fault Types Implemented

The system detects the following WSN faults:

- Hard Fault (Node failure)
- Soft/Data Fault (Abnormal readings)
- Intermittent Fault (Random abnormal spikes)
- Energy Fault (Low battery)
- Communication Fault (Node not responding)

---

## 📁 Project Structure

`
WSN_RealTime_Hybrid_Project/
├── server.py
├── sensor_client.py
├── dashboard.py
├── config.py
├── testing_environment/
├── detection_system/
├── evaluation/
└── data/
`

---

## 🚀 Future Enhancements

- Add malicious fault detection
- Add topology visualization
- Add performance analytics
- Integrate database instead of CSV
- Deploy to cloud server

---

## 👨‍💻 Author

Final Year Project – Environmental Monitoring WSN  
Real-Time Hybrid Fault Detection System







