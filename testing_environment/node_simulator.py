# testing_environment/node_simulator.py


import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import random
import threading
from typing import Optional
from config import SIMULATION, FAULT_TYPES


_rng = random.Random(2024)

NODE_BASELINES: dict[int, dict] = {
    i: {
        'temperature': _rng.uniform(18.0, 35.0),
        'humidity':    _rng.uniform(30.0, 70.0),
        'battery':     _rng.uniform(60.0, 100.0),
    }
    for i in range(1, SIMULATION['num_nodes'] + 1)
}

# Mutable battery state shared across rounds (degraded over time) 
_battery_lock = threading.Lock()
_battery: dict[int, float] = {
    i: NODE_BASELINES[i]['battery']
    for i in range(1, SIMULATION['num_nodes'] + 1)
}


def _drain_battery(node_id: int) -> float:
    with _battery_lock:
        drain = random.uniform(0.05, 0.30)
        _battery[node_id] = max(0.0, _battery[node_id] - drain)
        return _battery[node_id]


def reset_batteries():
    
    with _battery_lock:
        for i in _battery:
            _battery[i] = NODE_BASELINES[i]['battery']


# Fault injection 
def inject_fault(reading: dict, fault_type: str) -> dict:
    
    r = reading.copy()
    if fault_type == 'battery_low':
        r['battery_level']        = round(random.uniform(2.0, 14.0), 2)
        r['energy_consumed_mJ']   = round(random.uniform(1.80, 2.00), 3)

    elif fault_type == 'link_loss':
        r['signal_strength']      = round(random.uniform(-99.0, -95.0), 2)
        r['pdr']                  = round(random.uniform(0.750, 0.810), 3)
        r['latency_ms']           = round(random.uniform(290.0, 420.0), 2)
        r['transmission_success'] = 0

    elif fault_type == 'sensor_fail':
        if random.random() < 0.5:
            r['temperature'] = round(
                random.choice([random.uniform(-15, 3), random.uniform(58, 85)]), 2
            )
        else:
            r['humidity'] = round(
                random.choice([random.uniform(0, 7), random.uniform(97, 110)]), 2
            )

    elif fault_type == 'intermittent':
        r['temperature'] = round(
            r['temperature'] + random.choice([-1, 1]) * random.uniform(10, 22), 2
        )
        r['latency_ms']  = round(r['latency_ms'] * random.uniform(1.5, 3.5), 2)
        r['pdr']         = round(r['pdr'] * random.uniform(0.65, 0.88), 3)

    return r

def build_reading(node_id: int,
                  num_clusters: int = SIMULATION['num_clusters']) -> dict:
    
    base    = NODE_BASELINES[node_id]
    cluster = ((node_id - 1) % num_clusters) + 1
    battery = _drain_battery(node_id)
    temp    = base['temperature'] + random.gauss(0, 1.5)
    hum     = base['humidity']    + random.gauss(0, 2.0)

    return {
        'node_id':              node_id,
        'cluster_id':           cluster,
        'battery_level':        round(battery, 2),
        'signal_strength':      round(random.uniform(-80.0, -30.0), 2),
        'temperature':          round(max(-40, min(85, temp)), 2),
        'humidity':             round(max(0, min(100, hum)), 2),
        'data_redundancy_flag': random.randint(0, 1),
        'data_packet_size':     random.randint(64, 512),
        'latency_ms':           round(random.uniform(20.0, 200.0), 2),
        'energy_consumed_mJ':   round(random.uniform(0.10, 1.80), 3),
        'optimized_path_flag':  random.randint(0, 1),
        'load_on_node':         round(random.uniform(0.10, 1.00), 2),
        'recovery_time_ms':     0.0,
        'pdr':                  round(random.uniform(0.85, 0.99), 3),
        'transmission_success': 1,
    }


def generate_round(fault_rate: float   = SIMULATION['fault_rate'],
                   intermittent_rate: float = SIMULATION['intermittent_rate'],
                   num_nodes: int       = SIMULATION['num_nodes'],
                   ) -> list[tuple[dict, str]]:
    
    results = []
    for node_id in range(1, num_nodes + 1):
        reading = build_reading(node_id)
        label   = 'none'

        if random.random() < fault_rate:
            label   = random.choice(FAULT_TYPES[1:])   # skip 'none'
            reading = inject_fault(reading, label)
        elif random.random() < intermittent_rate:
            label   = 'intermittent'
            reading = inject_fault(reading, label)

        results.append((reading, label))
    return results
