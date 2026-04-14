"""
Tests for Flask server API endpoints
"""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app as flask_app
from detection_system.hybrid_detector import get_detector
import database.db_manager as dbm


class TestServerRoutes:
    """Test all API endpoints."""

    @pytest.fixture
    def client(self):
        """Flask test client."""
        flask_app.config['TESTING'] = True
        with flask_app.test_client() as client:
            yield client

    def test_index_serves_dashboard(self, client):
        """GET / should serve dashboard HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() or b'html' in response.data

    def test_status_endpoint(self, client):
        """GET /status should return server status."""
        response = client.get('/status')
        assert response.status_code == 200
        data = json.loads(response.data)

        required_keys = [
            'server', 'version', 'timestamp', 'ml_model_loaded',
            'active_clusters', 'total_detections', 'total_faults',
            'total_readings', 'fault_rate', 'last_reading'
        ]
        for key in required_keys:
            assert key in data, f"Missing key in status: {key}"

        assert data['server'] == 'WSN Hybrid Fault Detection Server'
        assert data['version'] == '2.0'

    def test_sensor_data_post_valid(self, client):
        """POST /sensor_data with valid data should succeed."""
        payload = {
            'node_id': 123,
            'cluster_id': 2,
            'battery_level': 75.5,
            'signal_strength': -65.0,
            'temperature': 22.5,
            'humidity': 45.0,
            'data_redundancy_flag': 0,
            'data_packet_size': 256,
            'latency_ms': 120.0,
            'energy_consumed_mJ': 0.45,
            'optimized_path_flag': 1,
            'load_on_node': 0.6,
            'recovery_time_ms': 0.0,
            'pdr': 0.92,
            'transmission_success': 1
        }

        response = client.post(
            '/sensor_data',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'detection' in data

        # Check detection structure
        detection = data['detection']
        assert 'node_id' in detection
        assert 'cluster_id' in detection
        assert 'timestamp' in detection
        assert 'fault_detected' in detection
        assert 'fault_type' in detection
        assert 'confidence' in detection
        assert 'layers' in detection

    def test_sensor_data_missing_fields(self, client):
        """POST /sensor_data with missing fields should fail."""
        payload = {
            'node_id': 1,
            'cluster_id': 1,
            # Missing required fields
        }

        response = client.post(
            '/sensor_data',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 422  # Unprocessable Entity
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required fields' in data['error']

    def test_sensor_data_invalid_json(self, client):
        """POST /sensor_data with invalid JSON should fail."""
        response = client.post(
            '/sensor_data',
            data='invalid{json',
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_detections_endpoint_default(self, client):
        """GET /detections should return paginated results."""
        response = client.get('/detections')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'limit' in data
        assert 'offset' in data
        assert 'data' in data

    def test_detections_with_limit(self, client):
        """Should respect limit parameter."""
        response = client.get('/detections?limit=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['limit'] == 10
        assert len(data['data']) <= 10

    def test_detections_with_offset(self, client):
        """Should respect offset parameter."""
        response = client.get('/detections?offset=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['offset'] == 5

    def test_detections_fault_only(self, client):
        """fault_only parameter should filter results."""
        response = client.get('/detections?fault_only=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        for row in data['data']:
            assert row['fault_detected'] == 1

    def test_detections_invalid_limit_returns_400(self, client):
        """Non-integer limit should return 400."""
        response = client.get('/detections?limit=abc')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'limit' in data['error']

    def test_detections_invalid_offset_returns_400(self, client):
        """Non-integer offset should return 400."""
        response = client.get('/detections?offset=abc')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'offset' in data['error']

    def test_node_detections_endpoint(self, client):
        """GET /detections/<node_id> should return node history."""
        node_id = 999
        response = client.get(f'/detections/{node_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['node_id'] == node_id
        assert 'history' in data

    def test_node_detections_invalid_limit_returns_400(self, client):
        """Non-integer limit for node history should return 400."""
        response = client.get('/detections/1?limit=bad')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'limit' in data['error']

    def test_cluster_endpoint(self, client):
        """GET /cluster/<cluster_id> should return cluster summary."""
        cluster_id = 1
        response = client.get(f'/cluster/{cluster_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cluster_id'] == cluster_id
        assert 'nodes' in data

    def test_metrics_endpoint(self, client):
        """GET /metrics should return ML metrics JSON."""
        response = client.get('/metrics')
        # May return 404 if metrics file doesn't exist, or 200 if it does
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'accuracy' in data
            assert 'per_class' in data
        else:
            assert response.status_code == 404

    def test_network_summary_endpoint(self, client):
        """GET /network_summary should return full network snapshot."""
        response = client.get('/network_summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'fault_distribution' in data
        assert 'node_states' in data
        assert 'hourly_stats' in data

    def test_reset_endpoint(self, client):
        """POST /reset should clear database and return success."""
        response = client.post('/reset')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'reset complete'
        assert 'timestamp' in data

    def test_cors_headers(self, client):
        """All endpoints should have CORS headers."""
        response = client.get('/status')
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'


class TestServerErrorHandling:
    """Test error handling in server."""

    @pytest.fixture
    def client(self):
        """Flask test client."""
        flask_app.config['TESTING'] = True
        with flask_app.test_client() as client:
            yield client

    def test_404_handling(self, client):
        """Non-existent routes should return 404."""
        response = client.get('/nonexistent')
        assert response.status_code == 404


class TestDetectionIntegration:
    """Integration tests for detection with database."""

    @pytest.fixture
    def client(self):
        """Flask test client with fresh DB."""
        # Reset DB before integration tests
        detector = get_detector()
        assert detector.is_ml_ready()

        flask_app.config['TESTING'] = True
        with flask_app.test_client() as client:
            yield client

    def test_full_sensor_data_flow(self, client):
        """POST sensor data should trigger detection and store result."""
        payload = {
            'node_id': 500,
            'cluster_id': 3,
            'battery_level': 12.0,  # Triggers battery rule
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

        response = client.post(
            '/sensor_data',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        detection = result['detection']

        # Verify detection result
        assert detection['node_id'] == 500
        assert detection['cluster_id'] == 3
        assert 'timestamp' in detection
        assert isinstance(detection['fault_detected'], bool)
        assert isinstance(detection['fault_type'], str)
        assert 0 <= detection['confidence'] <= 1

        # Verify stored in DB
        get_response = client.get('/detections/500')
        assert get_response.status_code == 200
        history = json.loads(get_response.data)
        assert len(history['history']) > 0
        assert history['history'][0]['node_id'] == 500


class TestResponseTimes:
    """Performance and response time tests."""

    @pytest.fixture
    def client(self):
        """Flask test client."""
        flask_app.config['TESTING'] = True
        with flask_app.test_client() as client:
            yield client

    def test_status_response_time(self, client):
        """GET /status should respond quickly (< 100ms)."""
        import time
        start = time.time()
        response = client.get('/status')
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1, f"Status took {elapsed}s, expected < 0.1s"

    def test_sensor_data_response_time(self, client):
        """POST /sensor_data should respond quickly (< 200ms)."""
        import time
        payload = {
            'node_id': 1,
            'cluster_id': 1,
            'battery_level': 80.0,
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

        start = time.time()
        response = client.post(
            '/sensor_data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.2, f"Sensor data took {elapsed}s, expected < 0.2s"

    def test_sensor_data_invalid_numeric_type_returns_422(self, client):
        """Invalid numeric payload values should return 422."""
        payload = {
            'node_id': 'not-an-int',
            'cluster_id': 1,
            'battery_level': 80.0,
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
        response = client.post(
            '/sensor_data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 422
        data = json.loads(response.data)
        assert 'error' in data
        assert 'node_id' in data['error']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
