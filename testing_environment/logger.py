# testing_environment/logger.py

import os
from datetime import datetime


class SimulationLogger:
    def __init__(self, filename="results/simulation_log.txt"):
        os.makedirs("results", exist_ok=True)
        self.filename = filename

        # Create new log file with timestamp header
        with open(self.filename, "w") as f:
            f.write("WSN Simulation Log\n")
            f.write(f"Start Time: {datetime.now()}\n")
            f.write("=" * 50 + "\n")

    def log_round(self, round_number, data):
        with open(self.filename, "a") as f:
            f.write(f"\n--- Simulation Round {round_number} ---\n")
            for node in data:
                f.write(
                    f"Node {node['node_id']} | "
                    f"Value: {node['value']} | "
                    f"Energy: {node['energy']:.2f} | "
                    f"Position: ({node['x']:.2f}, {node['y']:.2f})\n"
                )

    def log_summary(self, actual_faulty):
        with open(self.filename, "a") as f:
            f.write("\n" + "=" * 50 + "\n")
            f.write("Simulation Summary\n")
            f.write(f"Actual Faulty Nodes: {actual_faulty}\n")
            f.write(f"End Time: {datetime.now()}\n")
            f.write("=" * 50 + "\n")