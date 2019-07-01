import copy
import datetime
from execution.simulation_engine.simulation import Simulation


class CopyCat:
    def __init__(self, config):
        self.config = config
        self.logs = {}
        self.simulation = Simulation(config)

    def log(self):
        self.logs[self.config['map']['maps'][0]] = self.simulation.log()
        self.config['map']['maps'].pop(0)

        if not self.config['map']['maps']:
            return 0
        return 1

    def regenerate(self):
        return self.simulation.restart(self.config)

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

    def get_logs(self):
        return [
            datetime.datetime.now().year,
            datetime.datetime.now().strftime('%B'),
            datetime.datetime.now().strftime('%A'),
            datetime.datetime.now().hour,
            datetime.datetime.now().minute,
            copy.deepcopy(self.config['map']['id']),
            copy.deepcopy(self.logs)
        ]
