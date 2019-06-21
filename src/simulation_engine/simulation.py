from src.simulation_engine.simulation_helpers.cycle import Cycle


class Simulation:
    def __init__(self, config):
        self.cycler = Cycle(config)
        self.terminated = False

    def connect_agent(self, token):
        return self.cycler.connect_agent(token)

    def disconnect_agent(self, token):
        return self.cycler.disconnect_agent(token)

    def start(self):
        self.cycler.activate_step()
        agents = self.cycler.get_agents_info()
        step = self.cycler.get_step()

        self.cycler.current_step += 1

        if self.cycler.check_steps():
            self.terminated = True
            return agents, step

        self.cycler.activate_step()

        return agents, step

    def do_step(self, agent_action_list):
        if self.terminated:
            return None

        actions_results = self.cycler.execute_actions(agent_action_list)
        step = self.cycler.get_step()

        self.cycler.update_steps()
        self.cycler.current_step += 1

        if self.cycler.check_steps():
            self.terminated = True
            return actions_results, step

        self.cycler.activate_step()

        return actions_results, step
