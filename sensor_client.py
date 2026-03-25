# sensor_client.py — WSN Sensor Node Simulator

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import random
import threading
import argparse
import requests
from datetime import datetime

from config import SIMULATION
from testing_environment.node_simulator import generate_round, reset_batteries


def _send(reading: dict, injected: str, stats: dict, url: str):
    try:
        resp = requests.post(url, json=reading, timeout=5)
        resp.raise_for_status()
        det = resp.json().get('detection', {})
        detected      = bool(det.get('fault_detected'))
        detected_type = det.get('fault_type', 'none')
        real_fault    = injected != 'none'
        with stats['lock']:
            stats['sent'] += 1
            if real_fault:
                stats['injected'] += 1
            if detected:
                stats['detected'] += 1
                if real_fault:
                    stats['tp'] += 1
                else:
                    stats['fp'] += 1
            elif real_fault:
                stats['fn'] += 1

    except requests.exceptions.ConnectionError:
        print("  ❌  Server not reachable — is server.py running?")
    except Exception as exc:
        print(f"  ⚠️  Send error: {exc}")


def _print_stats(stats: dict, rounds: int):
    print(f"\n  ┌─ Stats after {rounds} rounds ─────────────────")
    print(f"  │  Readings sent   : {stats['sent']}")
    print(f"  │  Faults injected : {stats['injected']}")
    print(f"  │  Faults detected : {stats['detected']}")


def run_simulation(rounds: int    = 0,
                   num_nodes: int = SIMULATION['num_nodes'],
                   fault_rate: float = SIMULATION['fault_rate'],
                   interval: float   = SIMULATION['round_interval'],
                   workers: int      = SIMULATION['thread_workers'],
                   url: str          = SIMULATION['server_url']):

    stats = dict(sent=0, injected=0, detected=0, tp=0, fp=0, fn=0,
                 lock=threading.Lock())

    print("=" * 56)
    print("  WSN Sensor Node Simulator")
    print(f"  Nodes: {num_nodes}   Clusters: {SIMULATION['num_clusters']}")
    print(f"  Fault rate: {fault_rate*100:.0f}%   Interval: {interval}s")
    print(f"  Server: {url}")
    print("=" * 56)

    round_num = 0
    try:
        while True:
            round_num += 1
            ts = datetime.now().strftime('%H:%M:%S')
            print(f"[Round {round_num:4d}] {ts} — dispatching {num_nodes} readings", end='', flush=True)

            batch   = generate_round(fault_rate, SIMULATION['intermittent_rate'], num_nodes)
            threads = []
            for reading, injected in batch:
                t = threading.Thread(
                    target=_send,
                    args=(reading, injected, stats, url),
                    daemon=True
                )
                threads.append(t)
                if len(threads) >= workers:
                    for tt in threads: tt.start()
                    for tt in threads: tt.join()
                    threads.clear()
            for tt in threads: tt.start()
            for tt in threads: tt.join()

            print(f"  ✓  (faults this round: {sum(1 for _, inj in batch if inj != 'none')})")

            if round_num % 5 == 0:
                _print_stats(stats, round_num)

            if rounds and round_num >= rounds:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n  ⏹  Simulation stopped by user.")

    _print_stats(stats, round_num)
    print(f"\nSimulation complete — {round_num} rounds run.")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='WSN Sensor Simulator')
    ap.add_argument('--rounds', type=int,   default=0,
                    help='Number of rounds (0 = infinite)')
    ap.add_argument('--nodes',  type=int,   default=SIMULATION['num_nodes'])
    ap.add_argument('--rate',   type=float, default=SIMULATION['fault_rate'],
                    help='Fault injection rate 0-1')
    ap.add_argument('--interval', type=float, default=SIMULATION['round_interval'],
                    help='Seconds between rounds')
    ap.add_argument('--url',    type=str,
                    default=SIMULATION['server_url'])
    args = ap.parse_args()

    run_simulation(
        rounds     = args.rounds,
        num_nodes  = args.nodes,
        fault_rate = args.rate,
        interval   = args.interval,
        url        = args.url,
    )
