from simulation_environment.environment_variables.agent import Agent


class AgentsController:
    def __init__(self, config):
        self.agents = {}
        self.config = config
        self.agents_info = config['agents']
        self.roles_info = config['roles']
        self.cdm_location = config['map']['centerLat'], config['map']['centerLon']

    def create_agent(self, token):
        if self.agents_info:
            current_role = next(iter(self.agents_info))

            self.agents_info[current_role] -= 1

            if self.agents_info[current_role] == 0:
                del self.agents_info[current_role]

            role = self.roles_info[current_role]
            battery = role['battery']
            speed = role['speed']
            physical_capacity = role['physicalCapacity']
            virtual_capacity = role['virtualCapacity']

            self.agents[token] = Agent(token, current_role, self.cdm_location, battery, speed, physical_capacity,
                                       virtual_capacity)

            return True

        else:
            return False

    def get_agents(self):
        return [self.agents[token] for token in self.agents if self.agents[token].is_active]
