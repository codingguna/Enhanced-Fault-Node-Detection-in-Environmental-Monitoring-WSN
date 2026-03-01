import time
import requests
from testing_environment.simulator import WSNSimulator
from config import SIMULATION_INTERVAL

sim = WSNSimulator()

while True:
    data = sim.generate_data()
    requests.post("http://127.0.0.1:5000/data", json=data)
    time.sleep(SIMULATION_INTERVAL)

    