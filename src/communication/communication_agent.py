
class Agent:
    def __init__(self, token, obj):
        self.token = token
        self.registered = False
        self.worker = False
        self.agent_info = obj
        self.simulation_info = {}
        self.action_name = ''
        self.action_params = []

    def format(self):
        return {'token': self.token, 'agent_info': self.agent_info}
