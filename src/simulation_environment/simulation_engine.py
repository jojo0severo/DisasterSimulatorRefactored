import copy
import secrets
from simulation_environment.world import World
from simulation_environment.log_recorder import Logger


class Simulation:

    def __init__(self, config):
        self.step = 0
        self.pre_events = None
        self.logger = Logger(config['map']['id'])
        seed = config['map']['randomSeed']
        if not seed:
            seed = secrets.token_hex(5)
        self.world = World(config, self.logger, seed)

    def start(self):
        self.world.generate_events()

        roles = self.world.create_roles()
        agent_percepts, full_percepts = self.initial_percepts()

        self.logger.register_perceptions(percepts=full_percepts, roles=roles,
                                         agent_percepts=agent_percepts, seed=full_percepts['randomSeed'])
        return agent_percepts

    def initial_percepts(self):
        self.pre_events = self.do_pre_step()
        map_config = copy.deepcopy(self.world.config['map'])
        map_config_agents = copy.deepcopy(map_config)
        for key in ['steps', 'randomSeed', 'gotoCost', 'rechargeRate']:
            del map_config_agents[key]

        return [map_config_agents, copy.deepcopy(self.pre_events)], map_config

    def create_agent(self, token, agent_info):
        return self.world.create_agent(token, agent_info)

    def do_pre_step(self):
        try:
            events = self.world.get_current_event(self.step)
        except IndexError:
            return None

        events.extend(self.world.percepts(self.step))
        self.world.decrease_period_and_lifetime(self.step)
        return events

    def do_step(self, actions):
        if self.pre_events is None:
            total_floods = self.world.generator.total_floods
            total_victims = self.world.generator.total_victims
            total_photos = self.world.generator.total_photos
            total_water_samples = self.world.generator.total_water_samples
            completed_tasks = self.world.events_completed()

            self.logger.register_end_of_simulation(
                total_floods,
                total_victims,
                total_photos,
                total_water_samples,
                self.step-1,
                completed_tasks
            )

            return 'Simulation Ended'

        action_results = self.world.execute_actions(actions, self.step)
        results = {'action_results': action_results, 'events': self.pre_events}
        self.step += 1
        self.pre_events = self.do_pre_step()
        return results

    def start_new_match(self):
        self.world.reset_events()
        self.world.cdm.reset_events()
        self.step = 0

    def match_result(self):
        return self.world.get_agents_results()

