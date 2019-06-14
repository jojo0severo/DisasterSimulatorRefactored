import time
from communication.agents_manager import Manager


class Controller:

    def __init__(self, max_matches, agents_amount, time_limit, internal_secret):
        self.agents_manager = Manager()
        self.start_time = None
        self.time_limit = time_limit
        self.started = False
        self.terminated = False
        self.is_first_step = True
        self.agents_amount = agents_amount
        self.max_matches = max_matches
        self.current_match = 0
        self.secret = internal_secret

    def burn(self, max_matches, agents_amount, time_limit):
        self.agents_manager.clear()
        del self.agents_manager
        del self.start_time
        del self.time_limit
        del self.started
        del self.terminated
        del self.is_first_step
        del self.agents_amount
        del self.max_matches
        del self.current_match
        self.agents_manager = Manager()
        self.start_time = None
        self.time_limit = time_limit
        self.started = False
        self.terminated = False
        self.is_first_step = True
        self.agents_amount = agents_amount
        self.max_matches = max_matches
        self.current_match = 0

    def start_timer(self):
        self.start_time = time.time()

    def add_agent(self, token, agent_info):
        self.agents_manager.add_agent(token, agent_info)

    def get_agent(self, token):
        return self.agents_manager.get_agent(token)

    def get_jobs(self):
        return self.agents_manager.get_jobs()

    def get_agents(self):
        return self.agents_manager.get_agents()

    def edit_agent(self, token, attribute, new_value):
        self.agents_manager.edit_agent(token, attribute, new_value)

    def update_agents(self, simulation_state):
        self.agents_manager.update_agents(simulation_state)

    def clear_workers(self):
        self.agents_manager.clear_workers()

    def check_secret(self, other_secret):
        if len(other_secret) != len(self.secret):
            return False

        for mine_letter, other_letter in zip(list(self.secret), list(other_secret)):
            if mine_letter != other_letter:
                return False

        return True

    def check_population(self):
        return self.agents_manager.get_agents_amount() < self.agents_amount

    def check_timer(self):
        return time.time() - self.start_time < self.time_limit

    def check_agent_connected(self, agent_info):
        for token in self.agents_manager.agents:
            if self.agents_manager.get_agent(token).agent_info == agent_info:
                return True
        return False

    def check_agent_token(self, agent_token):
        return True if self.agents_manager.get_agent(agent_token) is not None else False

    def check_token_registered(self, info_token):
        return self.agents_manager.get_agent(info_token).registered

    def check_agent_action(self, token):
        return True if self.agents_manager.get_agent(token).action_name else False

    def check_remaining_matches(self):
        self.current_match += 1
        return self.current_match - 1 < self.max_matches

    def check_working_agents(self):
        return self.agents_manager.get_workers_amount() == self.agents_manager.get_agents_amount()
