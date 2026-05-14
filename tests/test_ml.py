
import sys, os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from detection_system.hybrid_detector import get_detector

def test_ml():
    detector = get_detector()
    if not detector.is_ml_ready():
        print("ML Model not ready!")
        return

    # Test cases that should trigger faults
    test_cases = [
        {
            'label': 'Normal Reading',
            'node': {
                'node_id': 1, 'cluster_id': 1, 'battery_level': 80.0,
                'signal_strength': -50.0, 'temperature': 25.0, 'humidity': 50.0,
                'data_redundancy_flag': 0, 'data_packet_size': 256, 'latency_ms': 50.0,
                'energy_consumed_mJ': 0.2, 'optimized_path_flag': 1, 'load_on_node': 0.3,
                'recovery_time_ms': 0.0, 'pdr': 0.98, 'transmission_success': 1
            }
        },
        {
            'label': 'Battery Low',
            'node': {
                'node_id': 1, 'cluster_id': 1, 'battery_level': 5.0,
                'signal_strength': -50.0, 'temperature': 25.0, 'humidity': 50.0,
                'data_redundancy_flag': 0, 'data_packet_size': 256, 'latency_ms': 50.0,
                'energy_consumed_mJ': 1.9, 'optimized_path_flag': 1, 'load_on_node': 0.8,
                'recovery_time_ms': 350.0, 'pdr': 0.98, 'transmission_success': 1
            }
        },
        {
            'label': 'Link Loss',
            'node': {
                'node_id': 1, 'cluster_id': 1, 'battery_level': 80.0,
                'signal_strength': -98.0, 'temperature': 25.0, 'humidity': 50.0,
                'data_redundancy_flag': 0, 'data_packet_size': 256, 'latency_ms': 350.0,
                'energy_consumed_mJ': 0.5, 'optimized_path_flag': 1, 'load_on_node': 0.6,
                'recovery_time_ms': 420.0, 'pdr': 0.78, 'transmission_success': 0
            }
        }
    ]

    for tc in test_cases:
        print(f"\n--- Testing: {tc['label']} ---")
        result = detector.detect(tc['node'], [])
        ml = result['layers']['ml_model']
        print(f"Final Detection: {result['fault_detected']} ({result['fault_type']}) @ {result['confidence']}")
        print(f"ML Layer: fault={ml['fault']}, type={ml['fault_type']}, conf={ml['confidence']}")
        print(f"ML Reason: {ml['reason']}")
        print(f"Probabilities: {ml['probabilities']}")

if __name__ == '__main__':
    test_ml()
