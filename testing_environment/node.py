import random

class SensorNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.energy = 100
        self.is_faulty = False
        self.fault_type = None
        self.x = random.uniform(0, 100)
        self.y = random.uniform(0, 100)

    def sense(self, true_value):
        self.energy -= random.randint(1, 3)

        if self.energy <= 0:
            return None

        if self.is_faulty:
            if self.fault_type == "soft":
                return true_value + random.randint(40, 60)
            if self.fault_type == "intermittent":
                if random.random() < 0.5:
                    return true_value + random.randint(50, 70)

        return true_value