import time
from src.communication.controllers.socket_manager import SocketManager
from src.communication.controllers.agents_manager import Manager


class Controller:

    def __init__(self, agents_amount, time_limit, internal_secret):
        self.agents_manager = Manager()
        self.socket_manager = SocketManager()
        self.start_time = None
        self.time_limit = time_limit
        self.started = False
        self.terminated = False
        self.agents_amount = agents_amount
        self.secret = internal_secret
        self.processing_actions = False

    def start_timer(self):
        self.start_time = time.time()

    def add_agent(self, token, agent_info):
        self.agents_manager.add_agent(token, agent_info)

    def add_socket(self, token, socket_id):
        self.socket_manager.add_socket(token, socket_id)

    def get_agent(self, token):
        return self.agents_manager.get_agent(token)

    def get_socket(self, token):
        return self.socket_manager.get_socket(token)

    def get_actions(self):
        return self.agents_manager.get_actions()

    def get_agents(self):
        return self.agents_manager.get_agents()

    def get_sockets(self):
        return self.socket_manager.get_sockets()

    def edit_agent(self, token, attribute, new_value):
        self.agents_manager.edit_agent(token, attribute, new_value)

    def disconnect_agent(self, token):
        self.agents_manager.remove_agent(token)
        self.socket_manager.remove_socket(token)

    def clear_workers(self):
        self.agents_manager.clear_workers()

    def finish_connection_timer(self):
        self.start_time -= self.time_limit

    def check_socket_connected(self, token):
        return True if self.socket_manager.get_socket(token) is not None else False

    def check_socket_agents(self):
        return len(self.socket_manager.socket_clients) == len(self.agents_manager.get_agents())

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

    def check_working_agents(self):
        return self.agents_manager.get_workers_amount() == self.agents_manager.get_agents_amount()
