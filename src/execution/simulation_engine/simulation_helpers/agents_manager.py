from collections import namedtuple
from simulation_engine.simulation_objects.agent import Agent

Role = namedtuple('Role', 'abilities resources size name battery speed physical_capacity virtual_capacity')


class AgentsManager:
    def __init__(self, roles_info, cdm_location):
        self.agents = {}
        self.cdm_location = cdm_location
        self.roles = self.generate_roles(roles_info)

    def restart(self, roles_info, cdm_location):
        tokens = list(self.agents.keys())
        self.agents.clear()
        self.cdm_location = cdm_location
        self.roles.clear()
        self.roles = self.generate_roles(roles_info)
        for token in tokens:
            self.connect_agent(token)

    @staticmethod
    def generate_roles(roles_info):
        roles = []
        for role in roles_info:
            temp_role = Role(
                roles_info[role]['abilities'],
                roles_info[role]['resources'],
                roles_info[role]['size'],
                role,
                roles_info[role]['battery'],
                roles_info[role]['speed'],
                roles_info[role]['physicalCapacity'],
                roles_info[role]['virtualCapacity'])
            for i in range(roles_info[role]['amount']):
                roles.append(temp_role)

        return roles

    def connect_agent(self, token):
        if not self.roles:
            return False

        role = self.roles.pop(0)
        self.agents[token] = Agent(token, self.cdm_location, *role)

        return True

    def disconnect_agent(self, token):
        if token not in self.agents:
            return False

        else:
            self.agents[token].disconnect()
            return True

    def add_physical(self, token, item):
        self.agents[token].add_physical_item(item)

    def add_virtual(self, token, item):
        self.agents[token].add_virtual_item(item)

    def add_social_asset(self, token, social_asset):
        self.agents[token].social_assets.append(social_asset)

    def charge_agent(self, token):
        self.agents[token].charge()

    def discharge_agent(self, token):
        self.agents[token].discharge()

    def get_agent(self, token):
        return self.agents.get(token)

    def get_tokens(self):
        return [token for token in self.agents if self.agents[token].is_active]

    def get_agents_info(self):
        return list(self.agents.values())

    def deliver_physical(self, token, kind, amount=1):
        return self.agents[token].remove_physical_item(kind, amount)

    def deliver_virtual(self, token, kind, amount=1):
        return self.agents[token].remove_virtual_item(kind, amount)

    def edit_agent(self, token, attribute, new_value):
        exec(f'self.agents[token].{attribute} = new_value')

    def update_agent_location(self, token):
        if self.agents[token].route:
            location = self.agents[token].route.pop(0)
            self.agents[token].location = location

    def clear_agent_physical_storage(self, token):
        self.agents[token].clear_physical_storage()

    def clear_agent_virtual_storage(self, token):
        self.agents[token].clear_virtual_storage()
