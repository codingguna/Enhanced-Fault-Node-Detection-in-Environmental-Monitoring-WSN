"""
server.py — WSN Fault Detection REST API Server

Endpoints
─────────
POST  /sensor_data           Receive a sensor reading; run detection; store result
GET   /status                Server health, statistics, ML model status
GET   /detections            Paginated detection log  (?limit=&offset=&fault_only=)
GET   /detections/<node_id>  Per-node detection history
GET   /cluster/<cluster_id>  Cluster-level summary
GET   /metrics               ML model performance (from evaluation/ml_metrics.json)
GET   /network_summary       Full network state snapshot
POST  /reset                 Clear all stored detections

Run:  python server.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import threading
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory

from config import PATHS, SERVER, SIMULATION
from detection_system.hybrid_detector import get_detector
from database.db_manager import (
    insert_detection, query_detections, query_node_history,
    query_cluster_summary, query_status, query_network_summary, reset_db
)

app   = Flask(__name__, static_folder='static')
_lock = threading.Lock()

# ── Cluster peer cache (used by Layer 2) ───────────────────────────────────
_cluster_cache: dict[int, list] = {}
_MAX_PEERS = 20

def _update_cluster_cache(node: dict):
    cid = int(node.get('cluster_id', 0))
    if cid not in _cluster_cache:
        _cluster_cache[cid] = []
    _cluster_cache[cid].append(node)
    if len(_cluster_cache[cid]) > _MAX_PEERS:
        _cluster_cache[cid].pop(0)

def _get_peers(node: dict) -> list:
    cid = int(node.get('cluster_id', 0))
    nid = node.get('node_id')
    return [n for n in _cluster_cache.get(cid, []) if n.get('node_id') != nid]


# ══ Routes ══════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve the dashboard."""
    return send_from_directory('static', 'dashboard.html')


@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    node = request.get_json(force=True, silent=True)
    print('\n Data Recieved:', node)
    if not node:
        return jsonify(error='Request body must be JSON'), 400

    required = ['node_id', 'cluster_id', 'battery_level', 'signal_strength',
                 'temperature', 'humidity', 'latency_ms', 'pdr']
    missing  = [k for k in required if k not in node]
    if missing:
        return jsonify(error=f'Missing required fields: {missing}'), 422

    with _lock:
        _update_cluster_cache(node)
        peers    = _get_peers(node)
        detector = get_detector()
        result   = detector.detect(node, peers)
        insert_detection(result, node)

    return jsonify(status='ok', detection=result), 200


@app.route('/status', methods=['GET'])
def status():
    stats = query_status()
    return jsonify(
        server          = 'WSN Hybrid Fault Detection Server',
        version         = '2.0',
        timestamp       = datetime.now().isoformat(),
        ml_model_loaded = get_detector().is_ml_ready(),
        active_clusters = len(_cluster_cache),
        **stats
    )


@app.route('/detections', methods=['GET'])
def detections():
    limit      = max(1, min(500, int(request.args.get('limit',  100))))
    offset     = max(0,          int(request.args.get('offset',   0)))
    fault_only = request.args.get('fault_only', 'false').lower() == 'true'
    rows, total = query_detections(limit, offset, fault_only)
    return jsonify(total=total, limit=limit, offset=offset, data=rows)


@app.route('/detections/<int:node_id>', methods=['GET'])
def node_detections(node_id):
    limit = max(1, min(200, int(request.args.get('limit', 50))))
    return jsonify(node_id=node_id, history=query_node_history(node_id, limit))


@app.route('/cluster/<int:cluster_id>', methods=['GET'])
def cluster(cluster_id):
    return jsonify(cluster_id=cluster_id, nodes=query_cluster_summary(cluster_id))


@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        with open(PATHS['metrics']) as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify(error='Metrics not found. Run: python -m detection_system.ml_trainer'), 404


@app.route('/network_summary', methods=['GET'])
def network_summary():
    return jsonify(query_network_summary())


@app.route('/reset', methods=['POST'])
def reset():
    reset_db()
    _cluster_cache.clear()
    return jsonify(status='reset complete', timestamp=datetime.now().isoformat())


# ── CORS headers (allow dashboard to call the API) ─────────────────────────
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


if __name__ == '__main__':
    print("=" * 54)
    print("  WSN Enhanced Fault Detection Server  v2.0")
    print(f"  http://127.0.0.1:5000")
    print(f"  Dashboard → http://127.0.0.1:5000/")
    print("=" * 54)
    app.run(host=SERVER['host'], port=SERVER['port'], debug=SERVER['debug'])
