import time
from src.communication.objects.agent import Agent


class Manager:
    def __init__(self):
        self.agents = {}

    def get_agents(self):
        return list(self.agents.values())

    def add_agent(self, token, agent_info):
        self.agents[token] = Agent(token, agent_info)

    def remove_agent(self, token):
        del self.agents[token]

    def edit_agent(self, token, attribute, new_value):
        exec(f'self.agents[token].{attribute} = new_value')

    def get_agents_amount(self):
        return len(self.agents)

    def get_agent(self, token):
        return self.agents.get(token)

    def get_actions(self):
        actions = []
        try:
            for token in self.agents:
                if self.agents[token].worker:
                    action_name = self.agents[token].action_name
                    action_params = self.agents[token].action_param

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        except RuntimeError:
            time.sleep(1)
            actions = []
            for token in self.agents:
                if self.agents[token].worker:
                    action_name = self.agents[token].action_name
                    action_params = self.agents[token].action_param

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        return actions

    def get_workers_amount(self):
        return sum([1 if self.agents[token].worker else 0 for token in self.agents])

    def clear_workers(self):
        for token in self.agents:
            self.agents[token].worker = False

    def clear(self):
        self.agents.clear()
        del self.agents
