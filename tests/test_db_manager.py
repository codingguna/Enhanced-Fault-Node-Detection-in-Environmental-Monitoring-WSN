"""
Tests for database module - db_manager operations
"""
import sys
import os
import json
import pytest
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_manager


class TestDatabaseInitialization:
    """Test database schema and initialization."""

    def test_init_db_creates_tables(self, initialized_db):
        """init_db should create detections and sensor_readings tables."""
        cursor = initialized_db.cursor()

        # Check detections table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detections'")
        assert cursor.fetchone() is not None

        # Check sensor_readings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_readings'")
        assert cursor.fetchone() is not None

    def test_detections_schema(self, initialized_db):
        """Detections table should have correct columns."""
        cursor = initialized_db.cursor()
        cursor.execute("PRAGMA table_info(detections)")
        columns = [row[1] for row in cursor.fetchall()]

        expected_columns = [
            'id', 'node_id', 'cluster_id', 'timestamp', 'fault_detected',
            'fault_type', 'confidence',
            'layer1_fault', 'layer1_type', 'layer1_reason',
            'layer2_fault', 'layer2_type', 'layer2_reason',
            'layer3_fault', 'layer3_type', 'layer3_reason',
            'battery_level', 'signal_strength', 'temperature', 'humidity',
            'latency_ms', 'pdr', 'energy_mj', 'raw_json'
        ]
        for col in expected_columns:
            assert col in columns, f"Missing column: {col}"

    def test_sensor_readings_schema(self, initialized_db):
        """Sensor_readings table should have correct columns."""
        cursor = initialized_db.cursor()
        cursor.execute("PRAGMA table_info(sensor_readings)")
        columns = [row[1] for row in cursor.fetchall()]

        expected = [
            'id', 'node_id', 'cluster_id', 'timestamp',
            'temperature', 'humidity', 'battery_level',
            'signal_strength', 'latency_ms', 'pdr', 'energy_mj'
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_indexes_created(self, initialized_db):
        """Performance indexes should be created."""
        cursor = initialized_db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        expected_indexes = [
            'idx_det_node', 'idx_det_cluster',
            'idx_det_ts', 'idx_det_fault', 'idx_sr_node'
        ]
        for idx in expected_indexes:
            assert any(idx in name for name in indexes), f"Missing index: {idx}"


class TestInsertDetection:
    """Test inserting detection results."""

    def test_insert_detection_basic(self, initialized_db):
        """Should insert a detection record."""
        detection = {
            'node_id': 1,
            'cluster_id': 1,
            'timestamp': '2024-01-01T12:00:00',
            'fault_detected': True,
            'fault_type': 'battery_low',
            'confidence': 0.85,
            'layers': {
                'rule_based': {'fault': True, 'fault_type': 'battery_low',
                               'confidence': 0.92, 'reason': 'Battery 10.0%'},
                'cluster': {'fault': False, 'fault_type': 'none',
                            'confidence': 0.0, 'reason': ''},
                'ml_model': {'fault': True, 'fault_type': 'battery_low',
                             'confidence': 0.75, 'reason': 'RF: battery_low @ 75%',
                             'all_proba': {'battery_low': 0.75, 'none': 0.25}}
            },
            'node_metrics': {
                'battery_level': 10.0,
                'signal_strength': -65.0,
                'temperature': 25.0,
                'humidity': 50.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
        }

        node = {
            'node_id': 1,
            'cluster_id': 1,
            'temperature': 25.0,
            'humidity': 50.0,
            'battery_level': 10.0,
            'signal_strength': -65.0,
            'latency_ms': 100.0,
            'pdr': 0.95,
            'energy_consumed_mJ': 0.5
        }

        db_manager.insert_detection(detection, node)

        # Verify insertion
        cursor = initialized_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM detections")
        count = cursor.fetchone()[0]
        assert count == 1

        cursor.execute("SELECT * FROM detections WHERE node_id=1")
        row = dict(cursor.fetchone())
        assert row['fault_detected'] == 1
        assert row['fault_type'] == 'battery_low'
        assert row['confidence'] == 0.85

    def test_insert_multiple_detections(self, initialized_db):
        """Should insert multiple detections correctly."""
        for i in range(5):
            detection = {
                'node_id': i,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': False,
                'fault_type': 'none',
                'confidence': 0.0,
                'layers': {
                    'rule_based': {'fault': False, 'fault_type': 'none',
                                   'confidence': 0.0, 'reason': ''},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.95, 'reason': '',
                                 'all_proba': {'none': 0.95, 'battery_low': 0.02,
                                               'link_loss': 0.02, 'sensor_fail': 0.01}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': i,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        cursor = initialized_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM detections")
        assert cursor.fetchone()[0] == 5


class TestQueryDetections:
    """Test querying detections."""

    def test_query_all_detections(self, initialized_db):
        """Should retrieve all detections with pagination."""
        # Insert 10 test records
        for i in range(10):
            detection = {
                'node_id': i % 5,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': i % 2 == 0,
                'fault_type': 'battery_low' if i % 2 == 0 else 'none',
                'confidence': 0.5 if i % 2 == 0 else 0.0,
                'layers': {
                    'rule_based': {'fault': False, 'fault_type': 'none',
                                   'confidence': 0.0, 'reason': ''},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.5, 'reason': '',
                                 'all_proba': {'none': 0.9, 'battery_low': 0.025,
                                               'link_loss': 0.025, 'sensor_fail': 0.025}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': i % 5,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        rows, total = db_manager.query_detections(limit=100, offset=0, fault_only=False)
        assert len(rows) == 10
        assert total == 10

    def test_query_with_limit_offset(self, initialized_db):
        """Pagination should work correctly."""
        # Insert 20 records
        for i in range(20):
            detection = {
                'node_id': 1,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': False,
                'fault_type': 'none',
                'confidence': 0.0,
                'layers': {
                    'rule_based': {'fault': False, 'fault_type': 'none',
                                   'confidence': 0.0, 'reason': ''},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.0, 'reason': '',
                                 'all_proba': {'none': 1.0, 'battery_low': 0.0,
                                               'link_loss': 0.0, 'sensor_fail': 0.0}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': 1,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        # Test pagination
        rows_page1, total = db_manager.query_detections(limit=10, offset=0, fault_only=False)
        assert len(rows_page1) == 10

        rows_page2, _ = db_manager.query_detections(limit=10, offset=10, fault_only=False)
        assert len(rows_page2) == 10

        # Pages should not overlap
        page1_ids = {r['id'] for r in rows_page1}
        page2_ids = {r['id'] for r in rows_page2}
        assert len(page1_ids & page2_ids) == 0

    def test_query_fault_only(self, initialized_db):
        """fault_only=True should filter to only fault detections."""
        # Insert mix of fault/no-fault
        for i in range(1, 11):  # 1-10 (inclusive)
            is_fault = i % 3 == 1  # 1,4,7,10 -> faults (4 faults)
            detection = {
                'node_id': 1,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': is_fault,
                'fault_type': 'battery_low' if is_fault else 'none',
                'confidence': 0.8 if is_fault else 0.0,
                'layers': {
                    'rule_based': {'fault': is_fault, 'fault_type': 'battery_low' if is_fault else 'none',
                                   'confidence': 0.8 if is_fault else 0.0, 'reason': 'Test'},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.0, 'reason': '',
                                 'all_proba': {'none': 1.0, 'battery_low': 0.0,
                                               'link_loss': 0.0, 'sensor_fail': 0.0}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': 1,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        rows_faults, total_faults = db_manager.query_detections(limit=100, offset=0, fault_only=True)
        assert len(rows_faults) == 4  # 1,4,7,10 out of 1-10
        for row in rows_faults:
            assert row['fault_detected'] == 1

        rows_all, total_all = db_manager.query_detections(limit=100, offset=0, fault_only=False)
        assert len(rows_all) == 10


class TestQueryNodeHistory:
    """Test node-specific querying."""

    def test_query_node_history(self, initialized_db):
        """Should retrieve history for specific node."""
        node_id = 42
        for i in range(5):
            detection = {
                'node_id': node_id,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': i % 2 == 0,
                'fault_type': 'battery_low' if i % 2 == 0 else 'none',
                'confidence': 0.5,
                'layers': {
                    'rule_based': {'fault': False, 'fault_type': 'none',
                                   'confidence': 0.0, 'reason': ''},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.5, 'reason': '',
                                 'all_proba': {'none': 0.9, 'battery_low': 0.025,
                                               'link_loss': 0.025, 'sensor_fail': 0.025}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': node_id,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        history = db_manager.query_node_history(node_id, limit=10)
        assert len(history) == 5
        for entry in history:
            assert entry['node_id'] == node_id

    def test_query_node_history_limit(self, initialized_db):
        """Should respect limit parameter."""
        node_id = 99
        for i in range(20):
            detection = {
                'node_id': node_id,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': False,
                'fault_type': 'none',
                'confidence': 0.0,
                'layers': {
                    'rule_based': {'fault': False, 'fault_type': 'none',
                                   'confidence': 0.0, 'reason': ''},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.0, 'reason': '',
                                 'all_proba': {'none': 1.0, 'battery_low': 0.0,
                                               'link_loss': 0.0, 'sensor_fail': 0.0}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': node_id,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        history = db_manager.query_node_history(node_id, limit=5)
        assert len(history) == 5


class TestQueryClusterSummary:
    """Test cluster-level aggregation queries."""

    def test_cluster_summary_structure(self, initialized_db):
        """Should return aggregated node statistics per cluster."""
        cluster_id = 2
        node_ids = [10, 11, 12]

        for nid in node_ids:
            for i in range(3):
                detection = {
                    'node_id': nid,
                    'cluster_id': cluster_id,
                    'timestamp': f'2024-01-01T12:{i:02d}:00',
                    'fault_detected': i == 0,
                    'fault_type': 'battery_low' if i == 0 else 'none',
                    'confidence': 0.5,
                    'layers': {
                        'rule_based': {'fault': False, 'fault_type': 'none',
                                       'confidence': 0.0, 'reason': ''},
                        'cluster': {'fault': False, 'fault_type': 'none',
                                    'confidence': 0.0, 'reason': ''},
                        'ml_model': {'fault': False, 'fault_type': 'none',
                                     'confidence': 0.5, 'reason': '',
                                     'all_proba': {'none': 0.9, 'battery_low': 0.025,
                                                   'link_loss': 0.025, 'sensor_fail': 0.025}}
                    },
                    'node_metrics': {
                        'battery_level': 50.0 + i,  # Varied battery
                        'signal_strength': -60.0,
                        'temperature': 25.0,
                        'humidity': 50.0,
                        'latency_ms': 100.0,
                        'pdr': 0.95,
                        'energy_consumed_mJ': 0.5
                    }
                }
                node = {
                    'node_id': nid,
                    'cluster_id': cluster_id,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'battery_level': 50.0 + i,
                    'signal_strength': -60.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
                db_manager.insert_detection(detection, node)

        summary = db_manager.query_cluster_summary(cluster_id)
        assert len(summary) == 3
        node_summary = [s for s in summary if s['node_id'] == 10][0]
        assert 'readings' in node_summary
        assert 'faults' in node_summary
        assert 'avg_battery' in node_summary
        assert 'avg_latency' in node_summary
        assert 'avg_pdr' in node_summary
        assert 'last_seen' in node_summary


class TestQueryStatus:
    """Test server status statistics."""

    def test_status_counts(self, initialized_db):
        """Should compute correct totals."""
        # Insert 15 records, 5 with faults
        for i in range(15):
            is_fault = i < 5
            detection = {
                'node_id': 1,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': is_fault,
                'fault_type': 'battery_low' if is_fault else 'none',
                'confidence': 0.5,
                'layers': {
                    'rule_based': {'fault': False, 'fault_type': 'none',
                                   'confidence': 0.0, 'reason': ''},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.5, 'reason': '',
                                 'all_proba': {'none': 0.9, 'battery_low': 0.025,
                                               'link_loss': 0.025, 'sensor_fail': 0.025}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': 1,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        status = db_manager.query_status()
        assert status['total_detections'] == 15
        assert status['total_faults'] == 5
        assert status['total_readings'] == 15
        assert status['fault_rate'] == pytest.approx(5/15, 0.001)


class TestQueryNetworkSummary:
    """Test network-wide summary queries."""

    def test_network_summary_structure(self, initialized_db):
        """Should return comprehensive network statistics."""
        # Insert data across 2 clusters, 3 nodes each
        for cluster in [1, 2]:
            for node in range(1, 4):
                for i in range(3):
                    detection = {
                        'node_id': node + (cluster * 10),
                        'cluster_id': cluster,
                        'timestamp': f'2024-01-01T12:{i:02d}:00',
                        'fault_detected': i == 0 and node == 1,
                        'fault_type': 'link_loss' if i == 0 and node == 1 else 'none',
                        'confidence': 0.6,
                        'layers': {
                            'rule_based': {'fault': False, 'fault_type': 'none',
                                           'confidence': 0.0, 'reason': ''},
                            'cluster': {'fault': False, 'fault_type': 'none',
                                        'confidence': 0.0, 'reason': ''},
                            'ml_model': {'fault': False, 'fault_type': 'none',
                                         'confidence': 0.6, 'reason': '',
                                         'all_proba': {'none': 0.9, 'battery_low': 0.025,
                                                       'link_loss': 0.025, 'sensor_fail': 0.025}}
                        },
                        'node_metrics': {
                            'battery_level': 80.0,
                            'signal_strength': -60.0,
                            'temperature': 25.0,
                            'humidity': 50.0,
                            'latency_ms': 100.0,
                            'pdr': 0.95,
                            'energy_consumed_mJ': 0.5
                        }
                    }
                    node_data = {
                        'node_id': node + (cluster * 10),
                        'cluster_id': cluster,
                        'temperature': 25.0,
                        'humidity': 50.0,
                        'battery_level': 80.0,
                        'signal_strength': -60.0,
                        'latency_ms': 100.0,
                        'pdr': 0.95,
                        'energy_consumed_mJ': 0.5
                    }
                    db_manager.insert_detection(detection, node_data)

        summary = db_manager.query_network_summary()
        assert 'fault_distribution' in summary
        assert 'node_states' in summary
        assert 'hourly_stats' in summary
        assert len(summary['node_states']) == 6

    def test_network_summary_uses_latest_fault_type(self, initialized_db):
        """last_fault_type should come from the latest inserted detection row."""
        node_id = 77
        cluster_id = 2
        rows = [
            ('2024-01-01T12:00:00', True, 'battery_low'),
            ('2024-01-01T12:01:00', False, 'none'),
            ('2024-01-01T12:02:00', True, 'link_loss'),
        ]
        for ts, is_fault, fault_type in rows:
            detection = {
                'node_id': node_id,
                'cluster_id': cluster_id,
                'timestamp': ts,
                'fault_detected': is_fault,
                'fault_type': fault_type,
                'confidence': 0.7,
                'layers': {
                    'rule_based': {'fault': is_fault, 'fault_type': fault_type, 'confidence': 0.7, 'reason': 'test'},
                    'cluster': {'fault': False, 'fault_type': 'none', 'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': is_fault, 'fault_type': fault_type, 'confidence': 0.7, 'reason': 'test', 'all_proba': {'none': 0.3, 'link_loss': 0.7}}
                },
                'node_metrics': {
                    'battery_level': 70.0,
                    'signal_strength': -63.0,
                    'temperature': 24.0,
                    'humidity': 48.0,
                    'latency_ms': 110.0,
                    'pdr': 0.92,
                    'energy_consumed_mJ': 0.4
                }
            }
            node_data = {
                'node_id': node_id,
                'cluster_id': cluster_id,
                'temperature': 24.0,
                'humidity': 48.0,
                'battery_level': 70.0,
                'signal_strength': -63.0,
                'latency_ms': 110.0,
                'pdr': 0.92,
                'energy_consumed_mJ': 0.4
            }
            db_manager.insert_detection(detection, node_data)

        summary = db_manager.query_network_summary()
        node_state = next(s for s in summary['node_states'] if s['node_id'] == node_id)
        assert node_state['last_fault_type'] == 'link_loss'


class TestResetDB:
    """Test database reset functionality."""

    def test_reset_clears_detections(self, initialized_db):
        """Reset should clear all detections."""
        # Insert some data
        for i in range(5):
            detection = {
                'node_id': 1,
                'cluster_id': 1,
                'timestamp': f'2024-01-01T12:{i:02d}:00',
                'fault_detected': False,
                'fault_type': 'none',
                'confidence': 0.0,
                'layers': {
                    'rule_based': {'fault': False, 'fault_type': 'none',
                                   'confidence': 0.0, 'reason': ''},
                    'cluster': {'fault': False, 'fault_type': 'none',
                                'confidence': 0.0, 'reason': ''},
                    'ml_model': {'fault': False, 'fault_type': 'none',
                                 'confidence': 0.0, 'reason': '',
                                 'all_proba': {'none': 1.0, 'battery_low': 0.0,
                                               'link_loss': 0.0, 'sensor_fail': 0.0}}
                },
                'node_metrics': {
                    'battery_level': 80.0,
                    'signal_strength': -60.0,
                    'temperature': 25.0,
                    'humidity': 50.0,
                    'latency_ms': 100.0,
                    'pdr': 0.95,
                    'energy_consumed_mJ': 0.5
                }
            }
            node = {
                'node_id': 1,
                'cluster_id': 1,
                'temperature': 25.0,
                'humidity': 50.0,
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
            db_manager.insert_detection(detection, node)

        cursor = initialized_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM detections")
        assert cursor.fetchone()[0] == 5

        db_manager.reset_db()

        cursor.execute("SELECT COUNT(*) FROM detections")
        assert cursor.fetchone()[0] == 0

    def test_reset_clears_sensor_readings(self, initialized_db):
        """Reset should also clear sensor readings."""
        # Insert detection will also insert sensor reading
        detection = {
            'node_id': 1,
            'cluster_id': 1,
            'timestamp': '2024-01-01T12:00:00',
            'fault_detected': False,
            'fault_type': 'none',
            'confidence': 0.0,
            'layers': {
                'rule_based': {'fault': False, 'fault_type': 'none',
                               'confidence': 0.0, 'reason': ''},
                'cluster': {'fault': False, 'fault_type': 'none',
                            'confidence': 0.0, 'reason': ''},
                'ml_model': {'fault': False, 'fault_type': 'none',
                             'confidence': 0.0, 'reason': '',
                             'all_proba': {'none': 1.0, 'battery_low': 0.0,
                                           'link_loss': 0.0, 'sensor_fail': 0.0}}
            },
            'node_metrics': {
                'battery_level': 80.0,
                'signal_strength': -60.0,
                'temperature': 25.0,
                'humidity': 50.0,
                'latency_ms': 100.0,
                'pdr': 0.95,
                'energy_consumed_mJ': 0.5
            }
        }
        node = {
            'node_id': 1,
            'cluster_id': 1,
            'temperature': 25.0,
            'humidity': 50.0,
            'battery_level': 80.0,
            'signal_strength': -60.0,
            'latency_ms': 100.0,
            'pdr': 0.95,
            'energy_consumed_mJ': 0.5
        }
        db_manager.insert_detection(detection, node)

        cursor = initialized_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor_readings")
        assert cursor.fetchone()[0] > 0

        db_manager.reset_db()

        cursor.execute("SELECT COUNT(*) FROM sensor_readings")
        assert cursor.fetchone()[0] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
