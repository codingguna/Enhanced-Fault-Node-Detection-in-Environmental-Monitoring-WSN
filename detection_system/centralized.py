from collections import defaultdict

class CentralizedConfirmation:
    def __init__(self):
        self.history = defaultdict(int)

    def confirm(self, suspected):
        confirmed = []
        for node_id, fault_type in suspected:
            self.history[node_id] += 1
            if self.history[node_id] >= 2:
                confirmed.append((node_id, fault_type))
        return confirmed