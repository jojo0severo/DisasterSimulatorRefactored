from simulation_environment.world import World


class Simulation:
    def __init__(self, config):
        self.world = World(config)
