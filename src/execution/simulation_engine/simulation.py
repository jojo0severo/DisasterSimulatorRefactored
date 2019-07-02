from execution.simulation_engine.simulation_helpers.cycle import Cycle


class Simulation:
    def __init__(self, config):
        self.cycler = Cycle(config)
        self.terminated = False
        self.actions_amount = 0
        self.actions_amount_by_step = []
        self.actions_by_step = []
        self.action_token_by_step = []

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

    def restart(self, config_file):
        self.cycler.restart(config_file)
        self.terminated = False
        self.actions_amount = 0
        self.actions_by_step.clear()
        self.actions_amount_by_step.clear()
        self.action_token_by_step.clear()

        return self.start()

    def do_step(self, agent_action_list):
        actions = [token_action_param['action'] for token_action_param in agent_action_list]
        tokens = [token_action_param['token'] for token_action_param in agent_action_list]

        self.actions_amount += len(agent_action_list)
        self.actions_amount_by_step.append((self.cycler.current_step, len(agent_action_list)))
        self.actions_by_step.append((self.cycler.current_step, actions))
        self.action_token_by_step.append((self.cycler.current_step, zip(tokens, actions)))

        if self.terminated:
            return None

        actions_results = self.cycler.execute_actions(agent_action_list)
        step = self.cycler.get_step()

        self.cycler.current_step += 1
        self.cycler.update_steps()

        if self.cycler.check_steps():
            self.terminated = True
            return actions_results, step

        self.cycler.activate_step()

        return actions_results, step

    def log(self):
        current_step = self.cycler.current_step
        max_steps = self.cycler.max_steps
        delivered_items = self.cycler.delivered_items
        agents_amount = len(self.cycler.agents_manager.get_tokens())
        agents = self.cycler.agents_manager.get_agents_info()
        active_agents_amount = sum([1 if agent.is_active else 0 for agent in self.cycler.agents_manager.get_agents_info()])
        active_agents = [agent for agent in self.cycler.agents_manager.get_agents_info() if agent.is_active]

        floods_amount = 0
        victims_saved = 0
        victims_dead = 0
        photos_taken = 0
        photos_analyzed = 0
        photos_ignored = 0
        water_samples_collected = 0
        water_samples_ignored = 0

        for i in range(current_step):
            if not self.cycler.steps[i]['flood']:
                continue

            floods_amount += 1

            for victim in self.cycler.steps[i]['victims']:
                if not victim.active and victim.lifetime > 0:
                    victims_saved += 1

                elif not victim.lifetime:
                    victims_dead += 1

            for photo in self.cycler.steps[i]['photos']:
                if not photo.active:
                    photos_taken += 1

                if photo.analyzed:
                    photos_analyzed += 1

                    for victim in photo.victims:
                        if not victim.active and victim.lifetime > 0:
                            victims_saved += 1

                        elif not victim.lifetime:
                            victims_dead += 1

                else:
                    photos_ignored += 1

            for water_sample in self.cycler.steps[i]['water_samples']:
                if not water_sample.active:
                    water_samples_collected += 1

                else:
                    water_samples_ignored += 1

        return {
            'environment': {
                'current_step': max_steps if current_step >= max_steps else current_step,
                'max_steps': max_steps,
                'delivered_items': delivered_items,
                'floods_amount': floods_amount,
                'total_victims': self.cycler.max_victims,
                'victims_saved': victims_saved,
                'victims_dead': victims_dead,
                'total_photos': self.cycler.max_photos,
                'photos_taken': photos_taken,
                'photos_analyzed': photos_analyzed,
                'photos_ignored': photos_ignored,
                'total_water_samples': self.cycler.max_water_samples,
                'water_samples_collected': water_samples_collected,
                'water_samples_ignored': water_samples_ignored,
                'total_social_assets': self.cycler.max_social_assets
            },
            'agents': {
                'active_agents_amount': active_agents_amount,
                'agents_amount': agents_amount,
                'active_agents': active_agents,
                'agents': agents,
            },
            'actions': {
                'amount_of_actions_executed': self.actions_amount,
                'amount_of_actions_by_step': self.actions_amount_by_step,
                'actions_by_step': self.actions_by_step,
                'action_token_by_step': self.action_token_by_step
            },
        }
