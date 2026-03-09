import random


class Node:

    def __init__(self, node_id):

        self.node_id = node_id

    def generate(self):

        return {

            "node_id": self.node_id,
            "temperature": random.uniform(18, 35),
            "humidity": random.uniform(40, 80),
            "pressure": random.uniform(1000, 1020),
            "light": random.uniform(100, 500),
            "energy": random.uniform(10, 100),
            "packet_loss": random.uniform(0, 0.2)
        }