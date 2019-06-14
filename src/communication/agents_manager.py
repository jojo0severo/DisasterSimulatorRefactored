import time
from communication.communication_agent import Agent


class Manager:
    def __init__(self):
        self.agents = {}

    def get_agents(self):
        return list(self.agents.values())

    def add_agent(self, token, agent_info):
        self.agents[token] = Agent(token, agent_info)

    def edit_agent(self, token, attribute, new_value):
        exec(f'self.agents[token].{attribute} = new_value')

    def get_agents_amount(self):
        return len(self.agents)

    def get_agent(self, token):
        return self.agents.get(token)

    def get_jobs(self):
        jobs = []
        try:
            for token in self.agents:
                if self.agents[token].worker:
                    action_name = self.agents[token].action_name
                    action_params = self.agents[token].action_param

                    jobs.append({'token': token, 'action': action_name, 'parameters': action_params})

                else:
                    jobs.append({'token': token, 'action': 'pass', 'parameters': []})

        except RuntimeError as r:
            if str(r) == 'dictionary changed size during iteration':
                time.sleep(2)
                jobs = []
                for token in self.agents:
                    if self.agents[token].worker:
                        action_name = self.agents[token].action_name
                        action_params = self.agents[token].action_param

                        jobs.append({'token': token, 'action': action_name, 'parameters': action_params})

                    else:
                        jobs.append({'token': token, 'action': 'pass', 'parameters': []})
            else:
                raise r

        return jobs

    def get_workers_amount(self):
        return sum([1 if self.agents[token].worker else 0 for token in self.agents])

    def update_agents(self, simulation_state):
        for agent in simulation_state['agents']:
            self.agents[agent['token']].simulation_info = agent

    def clear_workers(self):
        for token in self.agents:
            self.agents[token].worker = False

    def clear(self):
        self.agents.clear()
        del self.agents
