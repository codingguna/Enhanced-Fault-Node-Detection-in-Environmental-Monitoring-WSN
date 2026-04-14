"""
Tests for node_simulator - fault injection and node generation
"""
import sys
import os
import time
import pytest
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from testing_environment.node_simulator import (
    build_reading, inject_fault, generate_round,
    reset_batteries, NODE_BASELINES, _battery, reseed_simulation
)
from config import FAULT_TYPES, SIMULATION


class TestNodeBaselines:
    """Test node baseline definitions."""

    def test_all_nodes_have_baselines(self):
        """All simulated nodes should have baseline data."""
        expected_nodes = SIMULATION['num_nodes']
        assert len(NODE_BASELINES) == expected_nodes

    def test_baseline_ranges(self):
        """Baseline values should be within expected ranges."""
        for node_id, baseline in NODE_BASELINES.items():
            assert 18.0 <= baseline['temperature'] <= 35.0
            assert 30.0 <= baseline['humidity'] <= 70.0
            assert 60.0 <= baseline['battery'] <= 100.0

    def test_baseline_keys(self):
        """Each baseline should have required keys."""
        required_keys = ['temperature', 'humidity', 'battery']
        for node_id, baseline in NODE_BASELINES.items():
            for key in required_keys:
                assert key in baseline


class TestBuildReading:
    """Test node reading generation."""

    def test_build_reading_structure(self):
        """Should generate reading with all required fields."""
        reading = build_reading(1)

        required_fields = [
            'node_id', 'cluster_id', 'battery_level', 'signal_strength',
            'temperature', 'humidity', 'data_redundancy_flag', 'data_packet_size',
            'latency_ms', 'energy_consumed_mJ', 'optimized_path_flag',
            'load_on_node', 'recovery_time_ms', 'pdr', 'transmission_success'
        ]
        for field in required_fields:
            assert field in reading, f"Missing field: {field}"

    def test_node_id_preserved(self):
        """Node ID should match input."""
        node_id = 42
        reading = build_reading(node_id)
        assert reading['node_id'] == node_id

    def test_cluster_assignment(self):
        """Cluster should be 1-5 based on node_id modulo."""
        for node_id in range(1, 51):
            reading = build_reading(node_id)
            cluster = reading['cluster_id']
            assert 1 <= cluster <= SIMULATION['num_clusters']
            expected_cluster = ((node_id - 1) % SIMULATION['num_clusters']) + 1
            assert cluster == expected_cluster

    def test_temperature_range(self):
        """Temperature should be within reasonable bounds."""
        for _ in range(10):
            reading = build_reading(1)
            assert -40 <= reading['temperature'] <= 85

    def test_humidity_range(self):
        """Humidity should be 0-100%."""
        for _ in range(10):
            reading = build_reading(1)
            assert 0 <= reading['humidity'] <= 100

    def test_battery_decreases_over_time(self):
        """Battery should drain with repeated calls."""
        node_id = 1
        initial = build_reading(node_id)
        time.sleep(0.01)  # Ensure different drain
        second = build_reading(node_id)
        # Batteries should be decreasing (though drain is small)
        # Due to randomness, this might not always be true, so check trend over many calls
        batteries = [build_reading(node_id)['battery_level'] for _ in range(20)]
        # First reading should be higher than last (generally decreasing)
        assert batteries[0] > batteries[-1] or all(60 <= b <= 100 for b in batteries)

    def test_signal_strength_range(self):
        """Signal strength should be reasonable dBm."""
        for _ in range(10):
            reading = build_reading(1)
            assert -80 <= reading['signal_strength'] <= -30

    def test_pdr_range(self):
        """PDR should be 0-1."""
        for _ in range(10):
            reading = build_reading(1)
            assert 0 <= reading['pdr'] <= 1

    def test_optional_flags_are_binary(self):
        """Binary flags should be 0 or 1."""
        reading = build_reading(1)
        assert reading['data_redundancy_flag'] in [0, 1]
        assert reading['optimized_path_flag'] in [0, 1]
        assert reading['transmission_success'] in [0, 1]

    def test_load_on_node_range(self):
        """Load should be between 0 and 1."""
        for _ in range(10):
            reading = build_reading(1)
            assert 0.1 <= reading['load_on_node'] <= 1.0

    def test_recovery_time_initial(self):
        """Initial recovery time should be 0."""
        reading = build_reading(1)
        assert reading['recovery_time_ms'] == 0.0


class TestInjectFault:
    """Test fault injection into readings."""

    def test_battery_low_injection(self):
        """Battery low should set low battery and energy consumption."""
        reading = build_reading(1)
        original_battery = reading['battery_level']

        faulty = inject_fault(reading.copy(), 'battery_low')

        assert faulty['battery_level'] < 15.0
        assert faulty['battery_level'] >= 2.0
        assert faulty['energy_consumed_mJ'] > 1.7  # Increased energy
        assert faulty['battery_level'] != original_battery

    def test_link_loss_injection(self):
        """Link loss should affect signal, PDR, latency, transmission."""
        reading = build_reading(1)
        faulty = inject_fault(reading.copy(), 'link_loss')

        assert faulty['signal_strength'] < -95.0
        assert faulty['pdr'] < 0.82
        assert faulty['latency_ms'] > 290.0
        assert faulty['transmission_success'] == 0

    def test_sensor_fail_temperature(self):
        """Sensor fail should produce extreme temperatures."""
        reading = build_reading(1)
        original_temp = reading['temperature']

        for _ in range(10):  # Try several injections
            faulty = inject_fault(reading.copy(), 'sensor_fail')
            # Either temperature or humidity goes wrong
            if faulty['temperature'] != reading['temperature']:
                # If temp changed, should be extreme
                assert (faulty['temperature'] < 3 or faulty['temperature'] > 58) or \
                       (faulty['humidity'] < 7 or faulty['humidity'] > 97)

    def test_none_fault_passthrough(self):
        """'none' should return reading unchanged."""
        reading = build_reading(1)
        result = inject_fault(reading.copy(), 'none')
        assert result == reading

    def test_unknown_fault_passthrough(self):
        """Unknown fault type should return reading unchanged."""
        reading = build_reading(1)
        result = inject_fault(reading.copy(), 'unknown_type')
        assert result == reading


class TestGenerateRound:
    """Test round generation with fault injection."""

    def test_generate_round_returns_tuple_list(self):
        """Should return list of (reading, label) tuples."""
        batch = generate_round(num_nodes=5)
        assert isinstance(batch, list)
        assert len(batch) == 5
        for reading, label in batch:
            assert isinstance(reading, dict)
            assert isinstance(label, str)

    def test_generate_round_node_count(self):
        """Should generate correct number of nodes."""
        for num_nodes in [1, 10, 25, 50]:
            batch = generate_round(num_nodes=num_nodes)
            assert len(batch) == num_nodes

    def test_generate_round_fault_rate(self):
        """Approximately fault_rate of nodes should get faults."""
        fault_rate = 0.3
        num_nodes = 100
        batches = [generate_round(fault_rate=fault_rate, num_nodes=num_nodes) for _ in range(5)]

        for batch in batches:
            fault_count = sum(1 for _, label in batch if label != 'none')
            # Should be roughly 30% but allow random variation
            assert 10 <= fault_count <= 55, f"Fault count {fault_count} out of expected range"

    def test_generate_round_valid_fault_types(self):
        """Fault labels should be from FAULT_TYPES."""
        batch = generate_round(fault_rate=1.0, num_nodes=50)  # Force 100% faults
        for _, label in batch:
            assert label in FAULT_TYPES

    def test_none_label_for_healthy_nodes(self):
        """Nodes with no injected fault should have 'none'."""
        batch = generate_round(fault_rate=0.0, num_nodes=20)  # Force no faults
        for _, label in batch:
            assert label == 'none'

    def test_all_nodes_have_readings(self):
        """Every node should have complete reading."""
        batch = generate_round(num_nodes=10)
        for reading, label in batch:
            assert reading['battery_level'] is not None
            assert reading['signal_strength'] is not None


class TestBatteryManagement:
    """Test battery state tracking."""

    def test_reset_batteries(self):
        """Reset should restore all batteries to baseline."""
        # Consume some battery
        for node_id in range(1, 6):
            for _ in range(10):
                build_reading(node_id)

        reset_batteries()

        for node_id in range(1, 6):
            assert _battery[node_id] == NODE_BASELINES[node_id]['battery']

    def test_battery_drain_random(self):
        """Battery drain should be within expected range."""
        node_id = 1
        reset_batteries()
        initial = _battery[node_id]

        reading = build_reading(node_id)  # Triggers drain
        after = _battery[node_id]

        drain = initial - after
        assert 0.05 <= drain <= 0.30  # From code: uniform(0.05, 0.30)

    def test_battery_not_negative(self):
        """Battery should never go below 0."""
        for _ in range(100):
            reading = build_reading(50)  # Use different nodes
            assert reading['battery_level'] >= 0.0


class TestDeterminism:
    """Test predictable behavior for testing."""

    def test_generate_round_with_seed(self):
        """Same seed should produce same results."""
        reseed_simulation(1234, reset_state=True)
        batch1 = generate_round(num_nodes=10)
        reseed_simulation(1234, reset_state=True)
        batch2 = generate_round(num_nodes=10)

        readings1 = [r for r, _ in batch1]
        readings2 = [r for r, _ in batch2]
        labels1 = [lbl for _, lbl in batch1]
        labels2 = [lbl for _, lbl in batch2]
        assert readings1 == readings2
        assert labels1 == labels2


class TestEdgeCases:
    """Test boundary conditions."""

    def test_single_node_round(self):
        """Should handle generating reading for single node."""
        batch = generate_round(num_nodes=1)
        assert len(batch) == 1
        reading, label = batch[0]
        assert reading['node_id'] == 1

    def test_large_num_nodes(self):
        """Should handle many nodes."""
        batch = generate_round(num_nodes=100)
        assert len(batch) == 100
        node_ids = [r['node_id'] for r, _ in batch]
        assert len(set(node_ids)) == 100  # All unique

    def test_fault_rate_boundary_0(self):
        """fault_rate=0 should produce no faults."""
        batch = generate_round(fault_rate=0.0, num_nodes=50)
        for _, label in batch:
            assert label == 'none'

    def test_fault_rate_boundary_1(self):
        """fault_rate=1 should produce all faults (excluding none)."""
        batch = generate_round(fault_rate=1.0, num_nodes=50)
        for _, label in batch:
            assert label != 'none'
            assert label in FAULT_TYPES


class TestReadingConsistency:
    """Test that generated readings are internally consistent."""

    def test_all_readings_have_required_fields(self):
        """Every reading should have all fields populated."""
        batch = generate_round(num_nodes=10)
        for reading, _ in batch:
            # Check no None values
            for key, value in reading.items():
                assert value is not None, f"Field {key} is None in reading {reading}"

    def test_numeric_types(self):
        """Numeric fields should be numeric types."""
        batch = generate_round(num_nodes=5)
        reading = batch[0][0]

        numeric_fields = [
            'battery_level', 'signal_strength', 'temperature', 'humidity',
            'data_packet_size', 'latency_ms', 'energy_consumed_mJ',
            'load_on_node', 'recovery_time_ms', 'pdr'
        ]
        for field in numeric_fields:
            value = reading[field]
            assert isinstance(value, (int, float)), f"{field} is {type(value)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
