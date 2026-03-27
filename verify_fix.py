import json
from detection_system.hybrid_detector import get_detector

# Mock node data
node = {
    'node_id': 26,
    'cluster_id': 1,
    'battery_level': 91.88,
    'signal_strength': -57.49,
    'temperature': 24.25,
    'humidity': 32.93,
    'data_redundancy_flag': 0,
    'data_packet_size': 299,
    'latency_ms': 164.74,
    'energy_consumed_mJ': 0.15,
    'optimized_path_flag': 0,
    'load_on_node': 0.92,
    'recovery_time_ms': 0.0,
    'pdr': 0.91,
    'transmission_success': 1
}

# Mock peers for Layer 2 (Cluster Level)
peers = [
    {'node_id': 27, 'temperature': 24.0, 'humidity': 33.0, 'battery_level': 92.0},
    {'node_id': 28, 'temperature': 24.5, 'humidity': 32.5, 'battery_level': 91.5},
    {'node_id': 29, 'temperature': 24.1, 'humidity': 33.1, 'battery_level': 91.9},
]

detector = get_detector()
result = detector.detect(node, peers)

print("Detection Result:")
print(json.dumps(result, indent=2))

print("\nVerifying types:")
print(f"fault_detected type: {type(result['fault_detected'])}")
print(f"confidence type: {type(result['confidence'])}")

# Check nested types
l2 = result['layers']['cluster']
print(f"Layer 2 confidence type: {type(l2['confidence'])}")

try:
    json.dumps(result)
    print("\n✅ Verification successful: Result is JSON serializable.")
except TypeError as e:
    print(f"\n❌ Verification failed: {e}")
    exit(1)
