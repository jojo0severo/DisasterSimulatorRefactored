import copy
from src.simulation_engine.simulation import Simulation


class CopyCat:
    def __init__(self, config):
        self.simulation = Simulation(config)

    def connect_agent(self, token):
        response = self.simulation.connect_agent(token)
        return copy.deepcopy(response)

    def disconnect_agent(self, token):
        response = self.simulation.disconnect_agent(token)
        return copy.deepcopy(response)

    def start(self):
        response = self.simulation.start()
        return copy.deepcopy(response)

    def do_step(self, agent_action_list):
        response = self.simulation.do_step(agent_action_list)
        return copy.deepcopy(response)
