"""
Tests for configuration module - validates all settings and paths
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class TestConfigPaths:
    """Test that all required paths are defined and directories exist."""

    def test_all_paths_defined(self):
        """Verify all expected path keys are present."""
        required_paths = [
            'dataset', 'db', 'model', 'encoder', 'scaler',
            'metrics', 'eval_chart', 'dashboard'
        ]
        for path_key in required_paths:
            assert path_key in config.PATHS, f"Missing path: {path_key}"

    def test_directories_exist(self):
        """Verify all required directories are created."""
        for dir_name, dir_path in config.DIRS.items():
            assert os.path.isdir(dir_path), f"Directory not found: {dir_name} -> {dir_path}"

    def test_paths_are_absolute(self):
        """All paths should be absolute."""
        for path_key, path_val in config.PATHS.items():
            assert os.path.isabs(path_val), f"Path {path_key} is not absolute: {path_val}"


class TestServerConfig:
    """Test server configuration."""

    def test_server_ports(self):
        """Server port should be a valid integer."""
        assert isinstance(config.SERVER['port'], int)
        assert 1024 <= config.SERVER['port'] <= 65535

    def test_server_host(self):
        """Server host should be a valid IP or hostname."""
        assert isinstance(config.SERVER['host'], str)
        assert len(config.SERVER['host']) > 0

    def test_debug_mode_type(self):
        """Debug should be boolean."""
        assert isinstance(config.SERVER['debug'], bool)


class TestSimulationConfig:
    """Test simulation parameters."""

    def test_num_nodes_positive(self):
        """Number of nodes should be positive."""
        assert config.SIMULATION['num_nodes'] > 0

    def test_num_clusters_positive(self):
        """Number of clusters should be positive."""
        assert config.SIMULATION['num_clusters'] > 0

    def test_fault_rate_range(self):
        """Fault rate should be between 0 and 1."""
        rate = config.SIMULATION['fault_rate']
        assert 0 <= rate <= 1, f"Fault rate {rate} out of range [0,1]"

    def test_round_interval_positive(self):
        """Round interval should be positive."""
        assert config.SIMULATION['round_interval'] > 0

    def test_thread_workers_positive(self):
        """Thread workers should be positive integer."""
        assert config.SIMULATION['thread_workers'] > 0

    def test_server_url_format(self):
        """Server URL should be a valid HTTP URL."""
        url = config.SIMULATION['server_url']
        assert url.startswith('http://') or url.startswith('https://')
        assert '/sensor_data' in url


class TestThresholds:
    """Test detection thresholds."""

    def test_battery_critical_positive(self):
        """Battery critical threshold should be positive percentage."""
        assert 0 < config.THRESHOLDS['battery_critical'] <= 100

    def test_signal_critical_negative(self):
        """Signal critical should be negative dBm value."""
        assert config.THRESHOLDS['signal_critical'] < 0

    def test_latency_critical_positive(self):
        """Latency threshold should be positive."""
        assert config.THRESHOLDS['latency_critical'] > 0

    def test_pdr_critical_range(self):
        """PDR threshold should be between 0 and 1."""
        pdr = config.THRESHOLDS['pdr_critical']
        assert 0 <= pdr <= 1

    def test_z_score_threshold_positive(self):
        """Z-score threshold should be positive."""
        assert config.THRESHOLDS['z_score_threshold'] > 0

    def test_ml_confidence_min_range(self):
        """ML confidence minimum should be between 0 and 1."""
        conf = config.THRESHOLDS['ml_confidence_min']
        assert 0 <= conf <= 1

    def test_combined_threshold_range(self):
        """Combined threshold should be between 0 and 1."""
        thresh = config.THRESHOLDS['combined_threshold']
        assert 0 <= thresh <= 1

    def test_temperature_range_valid(self):
        """Temperature min < max."""
        assert config.THRESHOLDS['temp_min'] < config.THRESHOLDS['temp_max']

    def test_humidity_range_valid(self):
        """Humidity min < max."""
        assert config.THRESHOLDS['humidity_min'] < config.THRESHOLDS['humidity_max']


class TestDetectionWeights:
    """Test detection layer weights sum to 1.0."""

    def test_weights_sum_to_one(self):
        """Layer weights should sum to 1.0 (or close to it)."""
        total = (config.DETECTION_WEIGHTS['layer1'] +
                 config.DETECTION_WEIGHTS['layer2'] +
                 config.DETECTION_WEIGHTS['layer3'])
        assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, expected 1.0"

    def test_all_weights_positive(self):
        """All weights should be positive."""
        for layer, weight in config.DETECTION_WEIGHTS.items():
            assert weight >= 0, f"Weight for {layer} is negative: {weight}"


class TestMLConfig:
    """Test ML training configuration."""

    def test_n_estimators_positive(self):
        """Number of estimators should be positive."""
        assert config.ML['n_estimators'] > 0

    def test_max_depth_valid(self):
        """Max depth should be positive or None."""
        depth = config.ML['max_depth']
        assert depth is None or depth > 0

    def test_min_samples_split_valid(self):
        """Min samples split should be >= 2."""
        assert config.ML['min_samples_split'] >= 2

    def test_min_samples_leaf_valid(self):
        """Min samples leaf should be >= 1."""
        assert config.ML['min_samples_leaf'] >= 1

    def test_test_size_range(self):
        """Test size should be between 0 and 1."""
        size = config.ML['test_size']
        assert 0 < size < 1

    def test_cv_folds_positive(self):
        """CV folds should be at least 2."""
        assert config.ML['cv_folds'] >= 2

    def test_random_state_set(self):
        """Random state should be set for reproducibility."""
        assert isinstance(config.ML['random_state'], int)


class TestFeatureColumns:
    """Test feature column definitions."""

    def test_feature_cols_not_empty(self):
        """Should have defined feature columns."""
        assert len(config.FEATURE_COLS) > 0

    def test_no_duplicate_features(self):
        """Feature columns should be unique."""
        assert len(config.FEATURE_COLS) == len(set(config.FEATURE_COLS))

    def test_base_features_present(self):
        """Base sensor features should be included."""
        base_features = [
            'battery_level', 'signal_strength', 'temperature', 'humidity',
            'latency_ms', 'pdr'
        ]
        for feat in base_features:
            assert feat in config.FEATURE_COLS, f"Missing base feature: {feat}"

    def test_derived_features_present(self):
        """Derived features should be included."""
        derived_features = ['energy_ratio', 'latency_pdr_ratio', 'signal_load_score']
        for feat in derived_features:
            assert feat in config.FEATURE_COLS, f"Missing derived feature: {feat}"


class TestFaultTypes:
    """Test fault type definitions."""

    def test_fault_types_defined(self):
        """Should have fault type definitions."""
        assert len(config.FAULT_TYPES) > 0
        assert 'none' in config.FAULT_TYPES

    def test_known_fault_types(self):
        """Should include expected fault types."""
        expected = ['none', 'battery_low', 'link_loss', 'sensor_fail']
        for ft in expected:
            assert ft in config.FAULT_TYPES, f"Missing fault type: {ft}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
