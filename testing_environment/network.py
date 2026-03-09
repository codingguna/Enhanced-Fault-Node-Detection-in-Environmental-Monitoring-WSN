from .node import Node
from config import TOTAL_NODES


class Network:

    def __init__(self):

        self.nodes = [Node(i) for i in range(TOTAL_NODES)]

    def generate(self):

        return [n.generate() for n in self.nodes]