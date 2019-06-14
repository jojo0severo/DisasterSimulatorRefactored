# based on https://github.com/agentcontest/massim/blob/master/server/src/main/java/massim/scenario/city/data/Role.java


class Role:
    def __init__(self, role_id, config):
        self.id = role_id
        self.roads = config[id]['kind']
        self.speed = config[id]['speed']
        self.battery = config[id]['battery']
        self.perceive = config[id]['perceive']
        self.abilities = config[id]['abilities']
        self.virtual_capacity = config[id]['capacity_virtual']
        self.physical_capacity = config[id]['capacity_physical']
