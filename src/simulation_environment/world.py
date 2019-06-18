
from simulation_environment.route import Router
from simulation_environment.environment_executors.generator import Generator
from simulation_environment.environment_executors.action_executor import ActionExecutor
from simulation_environment.environment_executors.steps_controller import StepsController
from simulation_environment.environment_executors.agents_controller import AgentsController


class World:
    def __init__(self, config):
        router = Router(config['map']['map'])
        self.action_executor = ActionExecutor(router, (config['map']['centerLat'], config['map']['centerLon']))
        self.agents_controller = AgentsController(config)
        generator = Generator(config, router)
        self.steps_controller = StepsController(generator.generate_events(), generator.generate_social_assets())

    def create_agent(self, token):
        self.agents_controller.create_agent(token)

    def get_initial_perceptions(self, config):
        map_perception = {}
        for key in config:
            if key not in ['id', 'steps', 'randomSeed', 'gotoCos', 'rechargeRate']:
                map_perception[key] = config[key]

        perceptions = []
        for agent in self.agents_controller.get_agents():
            perceptions.append({'agent_perception': agent, 'map_perception': map_perception})

        return perceptions

    def execute_actions(self, token_action_list):
        steps = self.steps_controller.get_steps()
        agents = self.agents_controller.get_agents()

        self.action_executor.execute_actions(steps, agents, token_action_list)

    def do_step(self):
        current_step = self.steps_controller.get_step()
        self.steps_controller.increase_step()
        self.steps_controller.activate_next_step()
        self.steps_controller.decrease_period_and_lifetime()

        return current_step
