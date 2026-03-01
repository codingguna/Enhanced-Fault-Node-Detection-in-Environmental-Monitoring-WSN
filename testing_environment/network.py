from .node import SensorNode

class SensorNetwork:
    def __init__(self, total_nodes):
        self.nodes = [SensorNode(i) for i in range(total_nodes)]

    def get_nodes(self):
        return self.nodes