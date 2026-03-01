import random

class EnvironmentModel:
    def get_temperature(self):
        return 30 + random.uniform(-3, 3)