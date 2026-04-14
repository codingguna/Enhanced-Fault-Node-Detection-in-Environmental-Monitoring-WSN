# Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks

**Final Year Project Report**  
**B.E. Information Technology**  
**Academic Year 2025-2026**

---

## **Abstract**

Wireless Sensor Networks (WSNs) are critical for environmental monitoring applications, but sensor node faults can compromise data integrity and system reliability. Traditional rule-based fault detection methods achieve only 72.44% accuracy, missing 27.56% of fault instances. This project presents a **Smart Hybrid Fault Detection System** that combines three detection layers—rule-based thresholds, statistical cluster analysis, and machine learning—to improve accuracy to **90.30%**, representing a **+17.86% improvement** over baseline methods.

The system implements a real-time RESTful API using Flask, receiving sensor data from 50 simulated nodes across 5 clusters, performing multi-layer detection with weighted voting (35% rule-based + 25% cluster + 40% ML), storing results in SQLite, and providing an interactive dashboard for monitoring. The Random Forest classifier is trained on a dataset of 1,854 sensor readings with 19 features including 6 engineered features.

Performance evaluation shows the hybrid approach achieves superior fault detection while maintaining 89.62% ± 0.71% cross-validation accuracy. The Decision Tree model achieves the highest test accuracy at 91.11%, though Random Forest is selected for production due to better stability. The system is production-ready, handling concurrent requests via threading, supporting CORS for web integration, and providing comprehensive REST endpoints for data ingestion, querying, and network monitoring.

**Keywords:** Wireless Sensor Network, Fault Detection, Machine Learning, Random Forest, Hybrid System, Flask API, Real-time Monitoring

---

## **Table of Contents**

1. **Introduction** ................................................. 1
   1.1 Background ................................................... 1
   1.2 Problem Statement ........................................... 2
   1.3 Objectives ................................................... 3
   1.4 Scope & Limitations .......................................... 4
   1.5 Methodology Overview ........................................ 5
   1.6 Report Organization .......................................... 6

2. **Literature Review** ........................................... 7
   2.1 Wireless Sensor Networks: Architecture and Applications .... 7
   2.2 Fault Types in Environmental Monitoring WSNs ............... 9
   2.3 Traditional Rule-Based Detection Methods ................... 11
   2.4 Statistical Anomaly Detection Approaches ................... 13
   2.5 Machine Learning for Fault Detection ....................... 15
   2.6 Hybrid Approaches in Literature ............................ 17
   2.7 Research Gap and Contribution .............................. 18

3. **System Analysis & Design** ................................... 20
   3.1 System Requirements ......................................... 20
      3.1.1 Functional Requirements ............................... 20
      3.1.2 Non-Functional Requirements ........................... 22
      3.1.3 Hardware & Software Specifications .................... 23
   3.2 System Architecture ......................................... 24
      3.2.1 Three-Layer Hybrid Detection Architecture ............ 25
      3.2.2 Component Interaction Diagram ........................ 27
      3.2.3 Data Flow Architecture ................................. 28
   3.3 Detection Algorithm Design .................................. 30
      3.3.1 Layer 1: Rule-Based Thresholds ........................ 31
      3.3.2 Layer 2: Cluster Z-Score Anomaly Detection ............ 33
      3.3.3 Layer 3: Random Forest ML Classifier .................. 35
      3.3.4 Weighted Voting Mechanism .............................. 37
   3.4 Database Design ............................................. 39
      3.4.1 ER Diagram ............................................. 39
      3.4.2 Schema Design .......................................... 40
      3.4.3 Indexing Strategy ....................................... 41
   3.5 API Design .................................................. 42
      3.5.1 RESTful Endpoints ...................................... 42
      3.5.2 Request/Response Formats .............................. 44
      3.5.3 Error Handling ......................................... 46
   3.6 User Interface Design ....................................... 47
      3.6.1 Dashboard Layout ....................................... 47
      3.6.2 Real-time Monitoring Features ......................... 48
      3.6.3 Data Visualization Choices ............................. 49

4. **Implementation** ............................................... 51
   4.1 Technology Stack ............................................ 51
      4.1.1 Backend: Python & Flask ............................... 51
      4.1.2 Machine Learning: scikit-learn ........................ 52
      4.1.3 Database: SQLite with WAL Mode ........................ 53
      4.1.4 Frontend: HTML5, Chart.js ............................. 54
      4.1.5 Configuration Management ............................... 55
   4.2 Core Modules ................................................ 56
      4.2.1 Hybrid Detector (`hybrid_detector.py`) ................ 56
      4.2.2 ML Trainer (`ml_trainer.py`) .......................... 58
      4.2.3 Database Manager (`db_manager.py`) .................... 60
      4.2.4 Flask Server (`server.py`) ............................. 62
      4.2.5 Sensor Simulator (`sensor_client.py`) ................. 63
   4.3 Feature Engineering ......................................... 65
      4.3.1 Derived Features ....................................... 66
      4.3.2 Feature Importance Analysis ............................ 67
   4.4 Algorithm Implementation Details ............................ 69
      4.4.1 Rule-Based Detection Logic ............................. 69
      4.4.2 Z-Score Calculation .................................... 70
      4.4.3 Random Forest Configuration ............................ 71
      4.4.4 Weighted Vote Calculation .............................. 72
   4.5 Thread Safety & Concurrency ................................ 73
      4.5.1 Database Connection Locking ............................ 73
      4.5.2 Cluster Cache Management ............................... 74
      4.5.3 Multi-threaded Simulator ............................... 75
   4.6 REST API Implementation ..................................... 76
      4.6.1 Request Validation ..................................... 76
      4.6.2 JSON Serialization ..................................... 77
      4.6.3 CORS Configuration ..................................... 78
      4.6.4 Error Response Handling ............................... 79
   4.7 Dashboard Implementation .................................... 80
      4.7.1 Real-time Data Fetching ................................ 80
      4.7.2 Charts and Visualizations .............................. 81
      4.7.3 Network Topology Display .............................. 82

5. **Testing & Results** ........................................... 84
   5.1 Testing Strategy ............................................ 84
      5.1.1 Unit Testing Approach .................................. 84
      5.1.2 Integration Testing .................................... 85
      5.1.3 Performance Testing .................................... 86
   5.2 Test Cases .................................................. 87
      5.2.1 Configuration Tests .................................... 87
      5.2.2 Detection Layer Tests .................................. 88
      5.2.3 Database Operation Tests ............................... 89
      5.2.4 API Endpoint Tests ..................................... 90
      5.2.5 Simulator Tests ........................................ 91
   5.3 Experimental Setup .......................................... 92
      5.3.1 Dataset Description .................................... 92
      5.3.2 Train-Test Split ....................................... 93
      5.3.3 Evaluation Metrics ..................................... 94
   5.4 Results Analysis ............................................ 95
      5.4.1 Hybrid vs. Rule-Based Comparison ....................... 95
      5.4.2 Layer-wise Performance ................................. 96
      5.4.3 Confusion Matrix Analysis .............................. 97
      5.4.4 Per-Class Precision/Recall ............................. 98
   5.5 Multi-Model Benchmark ....................................... 100
      5.5.1 Models Compared ........................................ 100
      5.5.2 Benchmark Results ...................................... 101
      5.5.3 Model Selection Justification ........................... 103
   5.6 System Performance .......................................... 104
      5.6.1 Response Times ......................................... 104
      5.6.2 Concurrent Request Handling ............................ 105
      5.6.3 Database Query Performance ............................. 106

6. **Conclusion & Future Work** ................................... 108
   6.1 Project Summary ............................................ 108
   6.2 Achievements ............................................... 109
   6.3 Limitations ................................................ 110
   6.4 Future Enhancements ........................................ 111
      6.4.1 Deep Learning Approaches ............................... 111
      6.4.2 Ensemble Meta-Learning ................................. 112
      6.4.3 Distributed Deployment ................................. 113
      6.4.4 Edge Computing Integration ............................. 114
   6.5 Conclusion .................................................. 115

**References** ...................................................... 116

**Appendices** ...................................................... 120
   Appendix A: Complete Source Code Listing ....................... 120
   Appendix B: Dataset Schema & Sample Data ...................... 121
   Appendix C: API Documentation (OpenAPI Spec) .................. 122
   Appendix D: Installation & Deployment Guide .................... 123
   Appendix E: User Manual ......................................... 124
   Appendix F: Test Suite Output ................................... 125
   Appendix G: Raw Benchmark Data ................................. 126

---

## **Chapter 1: Introduction**

### 1.1 Background

Wireless Sensor Networks (WSNs) consist of spatially distributed autonomous sensor nodes that monitor physical or environmental conditions, such as temperature, humidity, pressure, light, and sound. These networks have become indispensable in applications ranging from environmental monitoring and precision agriculture to industrial automation and smart cities [1].

In environmental monitoring scenarios, sensor nodes are often deployed in remote or harsh locations where manual maintenance is difficult or impossible. Nodes typically operate on limited battery power and communicate wirelessly, making them susceptible to various fault types [2]:

- **Battery-related faults**: Power depletion or charging circuit failures
- **Communication faults**: Signal attenuation, interference, or hardware failure
- **Sensor faults**: Calibration drift, physical damage, or environmental extremes
- **Processing faults**: Memory corruption or software errors

Detecting these faults in real-time is crucial for maintaining data quality, enabling timely maintenance, and ensuring network longevity. However, the distributed nature and resource constraints of WSNs make fault detection challenging [3].

### 1.2 Problem Statement

Traditional rule-based fault detection approaches rely on hard-coded thresholds (e.g., battery < 15% = fault). While simple and computationally efficient, these methods suffer from significant limitations:

1. **Low Accuracy**: Literature reports rule-based methods achieving only 65-75% accuracy due to rigid thresholds that cannot adapt to varying environmental conditions or node-specific characteristics.

2. **High False Positives**: Normal variations in environmental readings may trigger false alarms, while subtle faults may go undetected.

3. **No Context Awareness**: Individual node readings are evaluated in isolation, ignoring spatial correlations with neighboring nodes that could indicate localized issues.

4. **Manual Threshold Tuning**: Thresholds require domain expertise and frequent recalibration as deployment environments change.

This project addresses these limitations by developing a **hybrid fault detection system** that combines multiple detection techniques to achieve higher accuracy while maintaining computational efficiency suitable for resource-constrained WSN nodes.

### 1.3 Objectives

The primary objectives of this project are:

1. **Design and implement a three-layer hybrid fault detection architecture**:
   - Layer 1: Fast rule-based threshold checks for obvious faults
   - Layer 2: Cluster-based statistical anomaly detection using Z-score
   - Layer 3: Machine learning classifier for complex pattern recognition

2. **Achieve >85% detection accuracy** on the WSN fault dataset while maintaining <200ms detection latency per node.

3. **Develop a complete end-to-end system** including:
   - Real-time RESTful API for sensor data ingestion
   - Persistent storage for detections and raw readings
   - Interactive web dashboard for monitoring
   - High-fidelity sensor node simulator with fault injection

4. **Evaluate and compare multiple ML algorithms** (Random Forest, SVM, Decision Tree, etc.) to select the optimal model for deployment.

5. **Ensure production-quality code** with proper error handling, thread safety, and cross-platform compatibility (Windows, Linux, macOS).

### 1.4 Scope & Limitations

**In Scope:**
- Fault detection for 4 fault types: battery_low, link_loss, sensor_fail, none
- Single-hop cluster analysis with up to 50 nodes in 5 clusters
- Historical data retention and querying via REST API
- Real-time dashboard with live charts and network topology view
- Comprehensive test suite with >80% code coverage
- Multi-model benchmark and performance analysis

**Out of Scope:**
- Multi-hop network fault propagation
- Energy-efficient detection algorithms (focused on accuracy, not energy optimization)
- Real hardware deployment (simulated nodes only)
- Distributed consensus-based fault detection
- Dynamic cluster reconfiguration

**Limitations:**
- Dataset contains only 1,854 samples with class imbalance (85% normal, 15% faults)
- Single dataset used for evaluation; cross-dataset validation recommended
- No online/streaming learning (batch-trained model)
- Flask development server not suitable for high-scale production deployment

### 1.5 Methodology Overview

The project follows an **Agile-inspired iterative development approach** with these phases:

1. **Requirements Analysis** (Week 1-2): Study WSN fault detection literature, define system specifications, select ML algorithms.

2. **Design** (Week 3-4): Create architecture diagrams, design database schema, define API contracts, plan feature engineering.

3. **Implementation** (Week 5-10):
   - Build hybrid detector with 3 detection layers
   - Train and tune ML models
   - Develop Flask REST API with threading support
   - Create interactive dashboard with Chart.js
   - Build multi-threaded simulator with fault injection

4. **Testing & Benchmarking** (Week 11-12):
   - Write unit tests for all modules (pytest)
   - Perform integration testing
   - Run multi-model benchmarks (Random Forest, SVM, Decision Tree, KNN, Naive Bayes, MLP, Logistic Regression)
   - Analyze results and compare with baseline

5. **Documentation & Deployment** (Week 13-14):
   - Write project report
   - Create installation guides and user manual
   - Package code with proper structure
   - Prepare demonstration

6. **Polishing** (Week 15):
   - Code cleanup and optimization
   - Ensure cross-platform compatibility
   - Generate final deliverables

### 1.6 Report Organization

The remainder of this report is organized as follows:

- **Chapter 2**: Reviews existing literature on WSN fault detection, ML approaches, and hybrid systems.
- **Chapter 3**: Details system requirements, architecture design, algorithm specification, and database/API design.
- **Chapter 4**: Describes implementation choices, code structure, feature engineering, and concurrency handling.
- **Chapter 5**: Presents testing methodology, experiment results, multi-model benchmark, and performance analysis.
- **Chapter 6**: Concludes with project achievements, limitations, and suggestions for future work.

---

## **Chapter 2: Literature Review** *(Full content to be expanded with 15+ academic references)*

### 2.1 Wireless Sensor Networks: Architecture and Applications

*(To be completed with citations from IEEE/ACM papers)*

### 2.2 Fault Types in Environmental Monitoring WSNs

*(To be completed with classification of fault types)*

### 2.3 Traditional Rule-Based Detection Methods

*(To be completed - discuss threshold-based methods, their simplicity and limitations)*

### 2.4 Statistical Anomaly Detection Approaches

*(To be completed - Z-score, Grubbs test, cluster-based methods)*

### 2.5 Machine Learning for Fault Detection

*(To be completed - supervised vs unsupervised, ensemble methods)*

### 2.6 Hybrid Approaches in Literature

*(To be completed - why combining methods is better)*

### 2.7 Research Gap and Contribution

**This project's novel contributions:**

1. **Weighted voting hybrid architecture**: Unlike simple ensemble methods, we apply weighted voting based on confidence scores from each layer (35% L1 + 25% L2 + 40% L3), optimized through empirical testing.

2. **Real-time cluster context**: Layer 2 maintains a per-cluster cache of peer node states, enabling spatial anomaly detection without expensive distributed consensus.

3. **Feature engineering for WSN**: Introduced derived features (energy_ratio, latency_pdr_ratio, signal_load_score) that capture cross-sensor relationships.

4. **Production-ready implementation**: Complete with threading-safe database operations, CORS-supporting Flask API, and interactive dashboard—extending beyond academic prototypes to deployable system.

---

## **Chapter 3: System Analysis & Design** *(To be expanded with diagrams)*

### 3.1 System Requirements

#### 3.1.1 Functional Requirements

**FR1: Sensor Data Ingestion**
- The system shall accept JSON sensor readings via HTTP POST to `/sensor_data`
- Required fields: node_id, cluster_id, battery_level, signal_strength, temperature, humidity, latency_ms, pdr, plus optional metadata fields

**FR2: Hybrid Fault Detection**
- The system shall perform 3-layer fault detection within 200ms per reading
- Layer 1 (Rule-based): Check 7 hard-coded thresholds
- Layer 2 (Cluster Z-score): Compare with median of 3+ peer nodes in same cluster
- Layer 3 (ML): Use Random Forest classifier for probabilistic fault detection

**FR3: Result Storage**
- All detections shall be stored in SQLite database with complete metadata
- Each detection record shall include individual layer outputs for auditability
- Raw sensor readings shall be stored separately for historical analysis

**FR4: Query Interface**
- GET `/detections`: Paginated list of all detections with optional `fault_only` filter
- GET `/detections/<node_id>`: Historical detections for specific node
- GET `/cluster/<cluster_id>`: Summary statistics by node within cluster
- GET `/network_summary`: Full network state snapshot

**FR5: Real-time Dashboard**
- Web dashboard at `/` shall display live detection results
- Network topology map showing node status (healthy/faulty)
- Real-time charts: fault distribution, detection timeline, ML metrics
- Refreshable at 2-second intervals

**FR6: Simulator**
- Generate synthetic sensor data for 50 nodes across 5 clusters
- Inject faults at configurable rate (default 15%)
- Multi-threaded HTTP client for realistic load testing

### 3.1.2 Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| **Response Time** | < 200ms for detection, < 50ms for queries |
| **Availability** | 99% uptime during operation |
| **Concurrency** | Support 50 concurrent sensor submissions |
| **Data Retention** | Store minimum 10,000 detection records |
| **Cross-platform** | Run on Windows, Linux, macOS |
| **Code Quality** | Pylint score > 8.0, test coverage > 80% |

### 3.1.3 Hardware & Software Specifications

**Development Environment:**
- Python 3.12+
- 8GB RAM minimum
- 500MB disk space

**Runtime Dependencies:**
```
Flask==2.3.3
pandas==2.3.3
numpy==1.26.4
scikit-learn==1.8.0
joblib==1.5.3
matplotlib==3.10.8
seaborn==0.13.2
requests==2.32.3
```

### 3.2 System Architecture

#### 3.2.1 Three-Layer Hybrid Detection Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      WSN HUB / SERVER                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              DETECTION ENGINE                       │   │
│   │    ┌──────────────┐  ┌──────────────┐             │   │
│   │    │  LAYER 1      │  │  LAYER 2      │           │   │
│   │    │  Rule-Based   │  │  Cluster Z-   │           │   │
│   │    │  Thresholds   │  │  Score        │           │   │
│   │    │  (35% weight) │  │  (25% weight) │           │   │
│   │    └──────────────┘  └──────────────┘             │   │
│   │               ┌──────────────────────┐             │   │
│   │               │   LAYER 3            │             │   │
│   │               │   Random Forest ML   │             │   │
│   │               │   (40% weight)       │             │   │
│   │               └──────────────────────┘             │   │
│   │                   ┌─────────────┐                  │   │
│   │                   │ WEIGHTED    │                  │   │
│   │                   │ VOTING      │                  │   │
│   │                   └─────────────┘                  │   │
│   │                     │                                 │   │
│   └─────────────────────┼─────────────────────────────────┘   │
│                         │                                     │
│   ┌─────────────────────┼─────────────────────────────────┐   │
│   │               RESULT PACKAGE                         │   │
│   │  (node_id, cluster_id, timestamp, fault_detected,  │   │
│   │   fault_type, confidence, layer details, metrics)  │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │               DATABASE LAYER                        │   │
│   │  • detections table (all detection records)        │   │
│   │  • sensor_readings table (raw data)                │   │
│   │  • Indexes for fast querying                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Flask REST API                         │   │
│   │  POST /sensor_data  - Submit reading               │   │
│   │  GET  /status       - Server health                │   │
│   │  GET  /detections   - Query results                │   │
│   │  GET  /metrics      - ML performance               │   │
│   │  POST /reset        - Clear database               │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2.2 Database Schema

**Table: detections**
```sql
CREATE TABLE detections (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id          INTEGER  NOT NULL,
    cluster_id       INTEGER  NOT NULL,
    timestamp        TEXT     NOT NULL,
    fault_detected   INTEGER  NOT NULL DEFAULT 0,
    fault_type       TEXT     NOT NULL DEFAULT 'none',
    confidence       REAL     NOT NULL DEFAULT 0.0,
    layer1_fault     INTEGER  NOT NULL DEFAULT 0,
    layer1_type      TEXT,
    layer1_reason    TEXT,
    layer2_fault     INTEGER  NOT NULL DEFAULT 0,
    layer2_type      TEXT,
    layer2_reason    TEXT,
    layer3_fault     INTEGER  NOT NULL DEFAULT 0,
    layer3_type      TEXT,
    layer3_reason    TEXT,
    battery_level    REAL,
    signal_strength  REAL,
    temperature      REAL,
    humidity         REAL,
    latency_ms       REAL,
    pdr              REAL,
    energy_mj        REAL,
    raw_json         TEXT
);
```

**Indexes:**
- `idx_det_node` ON detections(node_id)
- `idx_det_cluster` ON detections(cluster_id)
- `idx_det_ts` ON detections(timestamp)
- `idx_det_fault` ON detections(fault_detected)
- `idx_sr_node` ON sensor_readings(node_id)

### 3.2.3 API Specification

All endpoints support CORS for browser-based clients.

**POST /sensor_data**
- **Content-Type**: application/json
- **Request Body**: See schema in Chapter 1
- **Response**:
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
    "layers": { /* ... */ },
    "node_metrics": { /* ... */ }
  }
}
```

**GET /status**
- **Response**: Server health, statistics, ML model status

**GET /detections** (Query params: `limit`, `offset`, `fault_only`)
- **Response**: `{ total, limit, offset, data: [...] }`

**GET /detections/<node_id>**
- **Response**: `{ node_id, history: [...] }`

**GET /cluster/<cluster_id>**
- **Response**: `{ cluster_id, nodes: [...] }`

**GET /metrics**
- **Response**: ML model performance metrics from JSON file

**GET /network_summary**
- **Response**: Full network state with fault distribution, node states, hourly stats

**POST /reset**
- **Response**: `{ status: "reset complete", timestamp }`

---

## **Chapter 4: Implementation** *(To be expanded)*

### 4.1 Technology Stack

### 4.2 Core Modules

### 4.3 Feature Engineering

### 4.4 Algorithm Implementation Details

### 4.5 Thread Safety & Concurrency

### 4.6 REST API Implementation

### 4.7 Dashboard Implementation

---

## **Chapter 5: Testing & Results** *(To be expanded)*

### 5.1 Testing Strategy

### 5.2 Test Cases

### 5.3 Experimental Setup

### 5.4 Results Analysis

### 5.5 Multi-Model Benchmark

### 5.6 System Performance

---

## **Chapter 6: Conclusion & Future Work** *(To be expanded)*

### 6.1 Project Summary

### 6.2 Achievements

### 6.3 Limitations

### 6.4 Future Enhancements

### 6.5 Conclusion

---

## **References** *(To be populated with 15-20 academic references)*

[IEEE/ACM format citation style]

1. I.F. Akyildiz, W. Su, Y. Sankarasubramaniam, E. Cayirci, "Wireless sensor networks: a survey", Computer Networks, vol. 38, no. 4, pp. 393-422, 2002.

2. K. Akkaya, M. Demirbas, M. Ozguner, "Fault-tolerant clustering for wireless sensor networks", In proceedings of the 4th ACM international conference on Embedded networked sensor systems, 2006.

3. L. Arienzo, "Distributed fault detection in wireless sensor networks", International Journal of Distributed Sensor Networks, vol. 8, no. 1, 2012.

4. ... *(continuing with ML and fault detection papers)*

---

## **Appendices**

### Appendix A: Complete Source Code Listing  
*(All Python source files)*

### Appendix B: Dataset Schema & Sample Data  
*(CSV schema, feature descriptions, sample rows)*

### Appendix C: API Documentation (OpenAPI Spec)  
*(Full OpenAPI/Swagger specification)*

### Appendix D: Installation & Deployment Guide  
*(Step-by-step setup instructions)*

### Appendix E: User Manual  
*(How to use the system, screenshots, demo)*

### Appendix F: Test Suite Output  
*(pytest results with coverage report)*

### Appendix G: Raw Benchmark Data  
*(CSV/JSON from benchmark_models.py)*

---

## **Word Count & Page Estimates**

- **Abstract**: 150 words
- **Chapters 1-6**: ~25,000 words (≈ 75 pages @ 350 words/page)
- **References**: ~5 pages
- **Appendices**: ~20 pages
- **Total**: ~100 pages

---

## **Deliverables Checklist**

- [x] Working system with all components
- [x] Comprehensive test suite (pytest)
- [x] ML model training pipeline
- [x] Benchmark suite comparing 7 algorithms
- [x] REST API with documentation
- [x] Interactive dashboard
- [x] Sensor simulator with fault injection
- [x] Code cleanup and organization
- [x] Unicode-free for Windows compatibility
- [ ] Formal written report (this skeleton needs expansion)
- [ ] Installation guide
- [ ] User manual
- [ ] Demo video (3-5 minutes)
- [ ] Source code archive
- [ ] Requirement Verification Document (RVD)

---

**END OF REPORT OUTLINE**

*Note: This document provides the complete structure and placeholder content for the final year project report. Each section marked "To be expanded" needs detailed writing with proper citations, diagrams, screenshots, and analysis. The existing codebase and results provide all the technical content needed to flesh out each chapter.*
