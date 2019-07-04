
class Agent:
    def __init__(self, token, obj):
        self.token = token
        self.registered = False
        self.worker = False
        self.action_name = ''
        self.action_params = []
        self.agent_info = obj

