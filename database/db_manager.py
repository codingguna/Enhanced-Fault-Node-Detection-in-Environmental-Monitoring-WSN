# database/db_manager.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import sqlite3
import threading
from typing import Optional
from config import PATHS, ensure_dirs

ensure_dirs()

_db_lock = threading.Lock()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(PATHS['db'], check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_db():
    
    with _connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS detections (
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

        CREATE TABLE IF NOT EXISTS sensor_readings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id         INTEGER  NOT NULL,
            cluster_id      INTEGER  NOT NULL,
            timestamp       TEXT     NOT NULL,
            temperature     REAL,
            humidity        REAL,
            battery_level   REAL,
            signal_strength REAL,
            latency_ms      REAL,
            pdr             REAL,
            energy_mj       REAL
        );

        CREATE INDEX IF NOT EXISTS idx_det_node      ON detections(node_id);
        CREATE INDEX IF NOT EXISTS idx_det_cluster   ON detections(cluster_id);
        CREATE INDEX IF NOT EXISTS idx_det_ts        ON detections(timestamp);
        CREATE INDEX IF NOT EXISTS idx_det_fault     ON detections(fault_detected);
        CREATE INDEX IF NOT EXISTS idx_sr_node       ON sensor_readings(node_id);
        """)
        conn.commit()


def insert_detection(result: dict, node: dict):
    layers = result.get('layers', {})
    l1 = layers.get('rule_based', {})
    l2 = layers.get('cluster',   {})
    l3 = layers.get('ml_model',  {})
    m  = result.get('node_metrics', {})

    with _db_lock, _connect() as conn:
        conn.execute("""
            INSERT INTO detections (
                node_id, cluster_id, timestamp, fault_detected, fault_type,
                confidence,
                layer1_fault, layer1_type, layer1_reason,
                layer2_fault, layer2_type, layer2_reason,
                layer3_fault, layer3_type, layer3_reason,
                battery_level, signal_strength, temperature, humidity,
                latency_ms, pdr, energy_mj, raw_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            result['node_id'],    result['cluster_id'], result['timestamp'],
            int(result['fault_detected']), result['fault_type'], result['confidence'],
            int(l1.get('fault', False)), l1.get('fault_type'), l1.get('reason'),
            int(l2.get('fault', False)), l2.get('fault_type'), l2.get('reason'),
            int(l3.get('fault', False)), l3.get('fault_type'), l3.get('reason'),
            m.get('battery_level'), m.get('signal_strength'),
            m.get('temperature'),   m.get('humidity'),
            m.get('latency_ms'),    m.get('pdr'),
            m.get('energy_consumed_mJ'),
            json.dumps(result)
        ))
        conn.execute("""
            INSERT INTO sensor_readings (
                node_id, cluster_id, timestamp,
                temperature, humidity, battery_level, signal_strength,
                latency_ms, pdr, energy_mj
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            node['node_id'], node['cluster_id'], result['timestamp'],
            node.get('temperature'),   node.get('humidity'),
            node.get('battery_level'), node.get('signal_strength'),
            node.get('latency_ms'),    node.get('pdr'),
            node.get('energy_consumed_mJ'),
        ))
        conn.commit()


def query_detections(limit: int = 100, offset: int = 0,
                     fault_only: bool = False) -> tuple[list, int]:
    where = "WHERE fault_detected=1" if fault_only else ""
    with _connect() as conn:
        rows  = conn.execute(
            f"SELECT * FROM detections {where} ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM detections {where}"
        ).fetchone()[0]
    return [dict(r) for r in rows], total


def query_node_history(node_id: int, limit: int = 50) -> list:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM detections WHERE node_id=? ORDER BY id DESC LIMIT ?",
            (node_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def query_cluster_summary(cluster_id: int) -> list:
    with _connect() as conn:
        rows = conn.execute("""
            SELECT node_id,
                   COUNT(*)            AS readings,
                   SUM(fault_detected) AS faults,
                   ROUND(AVG(battery_level), 2)   AS avg_battery,
                   ROUND(AVG(latency_ms),    2)   AS avg_latency,
                   ROUND(AVG(pdr),           3)   AS avg_pdr,
                   MAX(timestamp)               AS last_seen
            FROM detections
            WHERE cluster_id=?
            GROUP BY node_id
            ORDER BY node_id
        """, (cluster_id,)).fetchall()
    return [dict(r) for r in rows]


def query_status() -> dict:
    with _connect() as conn:
        total    = conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
        faults   = conn.execute("SELECT COUNT(*) FROM detections WHERE fault_detected=1").fetchone()[0]
        readings = conn.execute("SELECT COUNT(*) FROM sensor_readings").fetchone()[0]
        last_ts  = conn.execute("SELECT MAX(timestamp) FROM detections").fetchone()[0]
    return {
        'total_detections': total,
        'total_faults':     faults,
        'total_readings':   readings,
        'fault_rate':       round(faults / total, 4) if total else 0.0,
        'last_reading':     last_ts,
    }


def query_network_summary() -> dict:
    with _connect() as conn:
        fault_dist = conn.execute("""
            SELECT fault_type, COUNT(*) AS count
            FROM detections WHERE fault_detected=1
            GROUP BY fault_type ORDER BY count DESC
        """).fetchall()

        node_states = conn.execute("""
            SELECT node_id, cluster_id,
                   MAX(timestamp)             AS last_seen,
                   ROUND(AVG(battery_level), 2) AS avg_battery,
                   SUM(fault_detected)        AS total_faults,
                   COUNT(*)                   AS total_readings,
                   fault_type                 AS last_fault_type
            FROM detections
            GROUP BY node_id
            ORDER BY node_id
        """).fetchall()

        hourly = conn.execute("""
            SELECT strftime('%H', timestamp) AS hour,
                   COUNT(*)            AS total,
                   SUM(fault_detected) AS faults
            FROM detections
            GROUP BY hour ORDER BY hour
        """).fetchall()

    return {
        'fault_distribution': [dict(r) for r in fault_dist],
        'node_states':        [dict(r) for r in node_states],
        'hourly_stats':       [dict(r) for r in hourly],
    }


def reset_db():
    with _db_lock, _connect() as conn:
        conn.execute("DELETE FROM detections")
        conn.execute("DELETE FROM sensor_readings")
        conn.commit()



init_db()
