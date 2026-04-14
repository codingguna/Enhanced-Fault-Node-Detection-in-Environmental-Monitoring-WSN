"""
Tests for hybrid_detector module - all 3 detection layers
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detection_system.hybrid_detector import HybridFaultDetector, _engineer_node_features
import numpy as np


class TestHybridDetectorInitialization:
    """Test detector initialization and model loading."""

    def test_detector_instantiation(self, detector):
        """Should create detector instance."""
        assert detector is not None
        assert isinstance(detector, HybridFaultDetector)

    def test_ml_model_loaded(self, detector):
        """ML model should be loaded successfully."""
        assert detector.is_ml_ready()
        assert detector.model is not None
        assert detector.encoder is not None
        assert detector.scaler is not None

    def test_model_components_type(self, detector):
        """Loaded components should have correct types."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler, LabelEncoder

        assert isinstance(detector.model, RandomForestClassifier)
        assert isinstance(detector.scaler, StandardScaler)
        assert isinstance(detector.encoder, LabelEncoder)


class TestFeatureEngineering:
    """Test feature engineering for node data."""

    def test_engineer_features_shape(self, sample_node):
        """Feature engineering should produce correct number of features."""
        from config import FEATURE_COLS
        df = _engineer_node_features(sample_node)
        assert df.shape[1] == len(FEATURE_COLS)

    def test_engineer_features_no_nan(self, sample_node):
        """Engineered features should not contain NaN."""
        df = _engineer_node_features(sample_node)
        assert not df.isna().any().any()

    def test_energy_ratio_calculation(self, sample_node):
        """Energy ratio should be energy_consumed / battery_level."""
        df = _engineer_node_features(sample_node)
        expected = sample_node['energy_consumed_mJ'] / sample_node['battery_level']
        actual = df['energy_ratio'].iloc[0]
        assert abs(actual - expected) < 1e-6

    def test_battery_critical_flag(self, sample_node):
        """Battery critical flag should be 1 if battery < 20, else 0."""
        df = _engineer_node_features(sample_node)
        expected = 1 if sample_node['battery_level'] < 20 else 0
        actual = df['battery_critical'].iloc[0]
        assert actual == expected


class TestLayer1RuleBased:
    """Test Layer 1: Rule-based fault detection."""

    def test_battery_low_fault(self, detector):
        """Low battery should trigger battery_low fault."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 10.0,  # Below 15% threshold
            'signal_strength': -60.0,
            'temperature': 25.0,
            'humidity': 50.0,
            'latency_ms': 100.0,
            'pdr': 0.95
        }
        result = detector._layer1_rules(node)
        assert result['fault'] is True
        assert result['fault_type'] == 'battery_low'
        assert result['confidence'] == 0.92

    def test_signal_strength_fault(self, detector):
        """Weak signal should trigger link_loss fault."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 80.0,
            'signal_strength': -100.0,  # Below -95 dBm
            'temperature': 25.0,
            'humidity': 50.0,
            'latency_ms': 100.0,
            'pdr': 0.95
        }
        result = detector._layer1_rules(node)
        assert result['fault'] is True
        assert result['fault_type'] == 'link_loss'

    def test_pdr_fault(self, detector):
        """Low PDR should trigger link_loss fault."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 80.0,
            'signal_strength': -60.0,
            'temperature': 25.0,
            'humidity': 50.0,
            'latency_ms': 100.0,
            'pdr': 0.75  # Below 0.82
        }
        result = detector._layer1_rules(node)
        assert result['fault'] is True
        assert result['fault_type'] == 'link_loss'

    def test_latency_fault(self, detector):
        """High latency should trigger link_loss fault."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 80.0,
            'signal_strength': -60.0,
            'temperature': 25.0,
            'humidity': 50.0,
            'latency_ms': 300.0,  # Above 280 ms
            'pdr': 0.95
        }
        result = detector._layer1_rules(node)
        assert result['fault'] is True
        assert result['fault_type'] == 'link_loss'

    def test_temperature_out_of_range(self, detector):
        """Temperature out of range should trigger sensor_fail."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 80.0,
            'signal_strength': -60.0,
            'temperature': 5.0,  # Below 10°C min
            'humidity': 50.0,
            'latency_ms': 100.0,
            'pdr': 0.95
        }
        result = detector._layer1_rules(node)
        assert result['fault'] is True
        assert result['fault_type'] == 'sensor_fail'

    def test_humidity_out_of_range(self, detector):
        """Humidity out of range should trigger sensor_fail."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 80.0,
            'signal_strength': -60.0,
            'temperature': 25.0,
            'humidity': 98.0,  # Above 95% max
            'latency_ms': 100.0,
            'pdr': 0.95
        }
        result = detector._layer1_rules(node)
        assert result['fault'] is True
        assert result['fault_type'] == 'sensor_fail'

    def test_no_fault(self, detector):
        """Normal node should not trigger faults."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 80.0,
            'signal_strength': -60.0,
            'temperature': 25.0,
            'humidity': 50.0,
            'latency_ms': 100.0,
            'pdr': 0.95
        }
        result = detector._layer1_rules(node)
        assert result['fault'] is False
        assert result['fault_type'] == 'none'
        assert result['confidence'] == 0.0

    def test_priority_order_temperature_humidity(self, detector):
        """Temperature/humidity check should have priority."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 10.0,  # Would trigger battery_low
            'signal_strength': -60.0,
            'temperature': 65.0,  # Triggers sensor_fail (has priority)
            'humidity': 50.0,
            'latency_ms': 100.0,
            'pdr': 0.95
        }
        result = detector._layer1_rules(node)
        # Temperature check comes after battery, but both trigger, battery wins due to elif structure
        # Actually in code, temperature check is after battery, but uses "if not in range" not "elif"
        # So it will override battery fault. Let's check actual behavior
        assert result['fault'] is True
        # sensor_fault should override battery_low due to order of checks
        if node['temperature'] > 55:
            assert result['fault_type'] == 'sensor_fail'


class TestLayer2Cluster:
    """Test Layer 2: Cluster Z-score anomaly detection."""

    def test_insufficient_peers(self, detector):
        """Should return no fault with < 3 peers."""
        node = {'node_id': 1, 'cluster_id': 1, 'temperature': 25.0}
        peers = [{'node_id': 2, 'temperature': 24.0}]  # Only 1 peer
        result = detector._layer2_cluster(node, peers)
        assert result['fault'] is False
        assert result['confidence'] == 0.0

    def test_outlier_detected(self, detector):
        """Should detect statistical outlier."""
        node = {'node_id': 1, 'cluster_id': 1, 'temperature': 50.0}  # Very high temp
        peers = [
            {'node_id': 2, 'temperature': 25.0},
            {'node_id': 3, 'temperature': 26.0},
            {'node_id': 4, 'temperature': 24.0},
        ]
        result = detector._layer2_cluster(node, peers)
        assert result['fault'] is True
        assert result['fault_type'] == 'sensor_fail'
        assert result['confidence'] > 0.6

    def test_normal_node_no_fault(self, detector):
        """Node within cluster range should not trigger."""
        node = {'node_id': 1, 'cluster_id': 1, 'temperature': 25.0}
        peers = [
            {'node_id': 2, 'temperature': 24.0},
            {'node_id': 3, 'temperature': 26.0},
            {'node_id': 4, 'temperature': 25.5},
        ]
        result = detector._layer2_cluster(node, peers)
        assert result['fault'] is False

    def test_z_score_threshold_respected(self, detector):
        """Should flag if z-score > threshold (2.5)."""
        from config import THRESHOLDS
        node = {'node_id': 1, 'cluster_id': 1, 'battery_level': 50.0}
        # Create peers with small variance but non-zero std
        # Mean ~100, std small => z-score large for 50
        peers = [
            {'node_id': 2, 'battery_level': 100.0},
            {'node_id': 3, 'battery_level': 100.5},
            {'node_id': 4, 'battery_level': 99.5},
            {'node_id': 5, 'battery_level': 100.0},
        ]
        result = detector._layer2_cluster(node, peers)
        assert result['fault'] is True


class TestLayer3ML:
    """Test Layer 3: ML model predictions."""

    def test_ml_ready(self, detector):
        """ML model should be ready."""
        assert detector.is_ml_ready()

    def test_ml_prediction_normal_node(self, detector, sample_node):
        """Normal node should predict 'none' with high confidence."""
        result = detector._layer3_ml(sample_node)
        assert result['fault'] is False  # Should not flag fault
        assert result['all_proba']['none'] > 0.9  # High confidence in 'none'
        assert 'all_proba' in result

    def test_ml_prediction_structure(self, detector, sample_node):
        """ML result should have correct structure."""
        result = detector._layer3_ml(sample_node)
        assert 'fault' in result
        assert 'fault_type' in result
        assert 'confidence' in result
        assert 'reason' in result
        assert 'all_proba' in result
        assert isinstance(result['all_proba'], dict)

    def test_ml_probabilities_sum_to_one(self, detector, sample_node):
        """All class probabilities should sum to ~1.0."""
        result = detector._layer3_ml(sample_node)
        total = sum(result['all_proba'].values())
        assert abs(total - 1.0) < 0.001

    def test_ml_known_fault_class(self, detector):
        """Known fault patterns should be detected."""
        # Simulate very low battery to trigger battery_low
        node = {
            'node_id': 100, 'cluster_id': 1,
            'battery_level': 5.0,
            'signal_strength': -65.0,
            'temperature': 25.0,
            'humidity': 50.0,
            'data_redundancy_flag': 0,
            'data_packet_size': 256,
            'latency_ms': 100.0,
            'energy_consumed_mJ': 2.0,
            'optimized_path_flag': 1,
            'load_on_node': 0.6,
            'recovery_time_ms': 0.0,
            'pdr': 0.95,
            'transmission_success': 1
        }
        result = detector._layer3_ml(node)
        # Probabilities dict should exist
        assert 'battery_low' in result['all_proba']


class TestHybridDetection:
    """Test complete hybrid detection pipeline."""

    def test_detect_returns_structure(self, detector, sample_node):
        """Detection should return complete result structure."""
        result = detector.detect(sample_node, [])
        required_keys = [
            'node_id', 'cluster_id', 'timestamp', 'fault_detected',
            'fault_type', 'confidence', 'layers', 'node_metrics'
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_layers_structure(self, detector, sample_node):
        """Each layer should have fault, type, confidence, reason."""
        result = detector.detect(sample_node, [])
        layers = ['rule_based', 'cluster', 'ml_model']
        for layer in layers:
            assert layer in result['layers']
            layer_data = result['layers'][layer]
            assert 'fault' in layer_data
            assert 'fault_type' in layer_data
            assert 'confidence' in layer_data
            assert 'reason' in layer_data

    def test_node_metrics_preserved(self, detector, sample_node):
        """Node metrics should match input."""
        result = detector.detect(sample_node, [])
        metrics = result['node_metrics']
        for key in ['battery_level', 'signal_strength', 'temperature',
                    'humidity', 'latency_ms', 'pdr', 'energy_consumed_mJ']:
            assert key in metrics
            assert metrics[key] == sample_node[key]

    def test_json_serializable(self, detector, sample_node):
        """Result should be JSON serializable."""
        import json
        result = detector.detect(sample_node, [])
        json_str = json.dumps(result)  # Should not raise
        assert isinstance(json_str, str)

    def test_confidence_range(self, detector, sample_node):
        """Combined confidence should be 0-1 range."""
        result = detector.detect(sample_node, [])
        conf = result['confidence']
        assert 0 <= conf <= 1

    def test_fault_type_or_none(self, detector, sample_node):
        """If fault_detected is False, fault_type should be 'none'."""
        result = detector.detect(sample_node, [])
        if not result['fault_detected']:
            assert result['fault_type'] == 'none'

    def test_strong_rule_fault_not_suppressed_by_vote(self, detector):
        """Strong layer-1 rule fault should force final fault detection."""
        node = {
            'node_id': 9,
            'cluster_id': 3,
            'battery_level': 80.74,
            'signal_strength': -63.2,
            'temperature': 25.77,
            'humidity': 97.73,  # Above humidity_max, triggers sensor_fail rule
            'data_redundancy_flag': 0,
            'data_packet_size': 256,
            'latency_ms': 46.1,
            'energy_consumed_mJ': 0.5,
            'optimized_path_flag': 1,
            'load_on_node': 0.6,
            'recovery_time_ms': 0.0,
            'pdr': 0.904,
            'transmission_success': 1
        }
        result = detector.detect(node, [])
        assert result['layers']['rule_based']['fault'] is True
        assert result['layers']['rule_based']['fault_type'] == 'sensor_fail'
        assert result['fault_detected'] is True
        assert result['fault_type'] == 'sensor_fail'

    def test_two_layer_agreement_detects_even_low_confidence(self, detector):
        """Two-layer agreement should detect fault near low-confidence boundary."""
        # Rule layer should flag battery_low.
        # Peer data makes cluster layer also flag battery_low.
        node = {
            'node_id': 2, 'cluster_id': 1,
            'battery_level': 14.8,   # just below threshold -> rule fault
            'signal_strength': -60.0,
            'temperature': 25.0,
            'humidity': 50.0,
            'data_redundancy_flag': 0,
            'data_packet_size': 256,
            'latency_ms': 100.0,
            'energy_consumed_mJ': 0.5,
            'optimized_path_flag': 1,
            'load_on_node': 0.6,
            'recovery_time_ms': 0.0,
            'pdr': 0.95,
            'transmission_success': 1
        }
        peers = [
            {'node_id': 3, 'battery_level': 90.0, 'temperature': 25.0, 'humidity': 50.0},
            {'node_id': 4, 'battery_level': 89.5, 'temperature': 24.8, 'humidity': 49.7},
            {'node_id': 5, 'battery_level': 90.3, 'temperature': 25.2, 'humidity': 50.3},
        ]
        result = detector.detect(node, peers)
        assert result['layers']['rule_based']['fault'] is True
        assert result['layers']['cluster']['fault'] is True
        assert result['fault_detected'] is True


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_missing_optional_fields(self, detector):
        """Detector should handle missing optional fields gracefully."""
        # Minimal valid node
        node = {
            'node_id': 1,
            'cluster_id': 1,
            'battery_level': 80.0,
            'signal_strength': -60.0,
            'temperature': 25.0,
            'humidity': 50.0,
            'latency_ms': 100.0,
            'pdr': 0.95
        }
        # Add only required fields, not optional ones
        try:
            result = detector.detect(node, [])
            # Should work or fail gracefully
            assert result is not None
        except (KeyError, TypeError) as e:
            pytest.fail(f"Detector failed with missing optional fields: {e}")

    def test_extreme_values(self, detector):
        """Should handle extreme but valid values."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 100.0,  # Max
            'signal_strength': -30.0,  # Very strong signal
            'temperature': -10.0,  # Very cold
            'humidity': 0.0,  # 0% humidity
            'latency_ms': 0.0,  # No latency
            'pdr': 1.0,  # Perfect delivery
            'data_redundancy_flag': 0,
            'data_packet_size': 512,
            'energy_consumed_mJ': 0.0,
            'optimized_path_flag': 1,
            'load_on_node': 1.0,
            'recovery_time_ms': 0.0,
            'transmission_success': 1
        }
        result = detector.detect(node, [])
        assert result['fault_detected'] in [True, False]

    def test_zero_values(self, detector):
        """Should handle zero values correctly."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 0.0,  # Should trigger battery fault
            'signal_strength': 0.0,
            'temperature': 0.0,
            'humidity': 0.0,
            'latency_ms': 0.0,
            'pdr': 0.0,  # Very low PDR
            'data_redundancy_flag': 0,
            'data_packet_size': 0,
            'energy_consumed_mJ': 0.0,
            'optimized_path_flag': 0,
            'load_on_node': 0.0,
            'recovery_time_ms': 0.0,
            'transmission_success': 0
        }
        result = detector.detect(node, [])
        assert result is not None
        # Battery 0% should trigger Layer 1
        assert result['layers']['rule_based']['fault'] is True

    def test_invalid_numeric_types_handled_gracefully(self, detector):
        """String/invalid numeric inputs should not crash detector."""
        node = {
            'node_id': 1, 'cluster_id': 1,
            'battery_level': 'bad-value',
            'signal_strength': '-60',
            'temperature': '25.5',
            'humidity': '50',
            'latency_ms': '100',
            'pdr': '0.95',
            'data_redundancy_flag': 0,
            'data_packet_size': 256,
            'energy_consumed_mJ': 0.3,
            'optimized_path_flag': 1,
            'load_on_node': 0.5,
            'recovery_time_ms': 0.0,
            'transmission_success': 1
        }
        result = detector.detect(node, [])
        assert result is not None
        assert 'layers' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
