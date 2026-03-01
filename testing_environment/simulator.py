from .network import SensorNetwork
from .environment_model import EnvironmentModel
from .fault_injection import inject_faults
from config import TOTAL_NODES, FAULTY_PERCENTAGE

class WSNSimulator:

    def __init__(self):
        self.network = SensorNetwork(TOTAL_NODES)
        self.environment = EnvironmentModel()
        self.actual_faulty = inject_faults(
            self.network.get_nodes(),
            FAULTY_PERCENTAGE
        )

    def generate_data(self):
        data = []
        for node in self.network.get_nodes():
            temp = self.environment.get_temperature()
            value = node.sense(temp)

            data.append({
                "node_id": node.node_id,
                "value": value,
                "energy": node.energy
            })
        return data