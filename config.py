#config.py
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
DIRS = {
    'database':   os.path.join(ROOT, 'database'),
    'models':     os.path.join(ROOT, 'models'),
    'evaluation': os.path.join(ROOT, 'evaluation'),
    'static':     os.path.join(ROOT, 'static'),
}
PATHS = {
    'dataset':    os.path.join(ROOT, 'database', 'wsn_aft_dataset.csv'),
    'db':         os.path.join(ROOT, 'database', 'wsn_detections.db'),
    'model':      os.path.join(ROOT, 'models',   'fault_classifier.pkl'),
    'encoder':    os.path.join(ROOT, 'models',   'label_encoder.pkl'),
    'scaler':     os.path.join(ROOT, 'models',   'scaler.pkl'),
    'metrics':    os.path.join(ROOT, 'evaluation', 'ml_metrics.json'),
    'eval_chart': os.path.join(ROOT, 'evaluation', 'evaluation_report.png'),
    'dashboard':  os.path.join(ROOT, 'static',   'dashboard.html'),
}
SERVER = {
    'host':  '0.0.0.0',
    'port':  5000,
    'debug': False,
}

SIMULATION = {
    'num_nodes':         50,
    'num_clusters':       5,
    'fault_rate':         0.15,   # 15% of nodes get a fault per round
    'intermittent_rate':  0.08,   # extra 8% get intermittent spike
    'round_interval':     2.0,    # seconds between rounds
    'thread_workers':    10,
    'server_url':        'http://127.0.0.1:5000/sensor_data',
}

THRESHOLDS = {
    # Layer 1 — Rule-Based
    'battery_critical':    15.0,   # % below → battery_low
    'signal_critical':    -95.0,   # dBm below → link_loss
    'latency_critical':   280.0,   # ms above → link_loss
    'pdr_critical':         0.82,  # ratio below → link_loss
    'temp_min':            10.0,   # °C
    'temp_max':            55.0,   # °C
    'humidity_min':        10.0,   # %
    'humidity_max':        95.0,   # %
    # Layer 2 — Cluster Statistical
    'z_score_threshold':    2.5,   # z-score → cluster anomaly
    # Layer 3 — ML
    'ml_confidence_min':    0.55,  # min ML probability to trust
    # Combined decision
    'combined_threshold':   0.30,  # weighted vote threshold
}

DETECTION_WEIGHTS = {
    'layer1': 0.35,
    'layer2': 0.25,
    'layer3': 0.40,
}

ML = {
    'n_estimators':   200,
    'max_depth':       15,
    'min_samples_split': 4,
    'min_samples_leaf':  2,
    'test_size':        0.20,
    'cv_folds':          5,
    'random_state':     42,
}

FEATURE_COLS = [
    'battery_level', 'signal_strength', 'temperature', 'humidity',
    'data_redundancy_flag', 'data_packet_size', 'latency_ms',
    'energy_consumed_mJ', 'optimized_path_flag', 'load_on_node',
    'recovery_time_ms', 'pdr', 'transmission_success',

    'energy_ratio', 'latency_pdr_ratio', 'signal_load_score',
    'battery_critical', 'high_latency', 'weak_signal',
]

FAULT_TYPES = ['none', 'battery_low', 'link_loss', 'sensor_fail']
TARGET_COL  = 'fault_type'


def ensure_dirs():
    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)

ensure_dirs()
