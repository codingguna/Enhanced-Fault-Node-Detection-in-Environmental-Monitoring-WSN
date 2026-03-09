from .network import Network


class WSNSimulator:

    def __init__(self):

        self.network = Network()

    def generate_data(self):

        return self.network.generate()