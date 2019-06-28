from src.simulation_engine.exceptions.exceptions import *
from src.simulation_engine.simulation_helpers.map import Map
from src.simulation_engine.generator.generator import Generator
from src.simulation_engine.simulation_helpers.agents_manager import AgentsManager


class Cycle:
    def __init__(self, config):
        self.map = Map(config['map']['map'][0], config['map']['proximity'])
        generator = Generator(config, self.map)
        self.steps = generator.generate_events()
        self.social_assets = generator.generate_social_assets()
        self.max_floods = generator.flood_id
        self.max_victims = generator.victim_id
        self.max_photos = generator.photo_id
        self.max_water_samples = generator.water_sample_id
        self.max_social_assets = generator.social_asset_id
        self.delivered_items = []
        self.current_step = 0
        self.max_steps = config['map']['steps']
        self.cdm_location = (config['map']['centerLat'], config['map']['centerLon'])
        self.agents_manager = AgentsManager(config['roles'], config['agents'], self.cdm_location)

    def restart(self, config_file):
        self.map.restart(config_file['map']['map'][0], config_file['map']['proximity'])
        generator = Generator(config_file, self.map)
        self.steps = generator.generate_events()
        self.social_assets = generator.generate_social_assets()
        self.max_floods = generator.flood_id
        self.max_victims = generator.victim_id
        self.max_photos = generator.photo_id
        self.max_water_samples = generator.water_sample_id
        self.max_social_assets = generator.social_asset_id
        self.delivered_items = []
        self.current_step = 0
        self.max_steps = config_file['map']['steps']
        self.cdm_location = (config_file['map']['centerLat'], config_file['map']['centerLon'])
        self.agents_manager.restart(config_file['roles'], config_file['agents'], self.cdm_location)


    def connect_agent(self, token):
        return self.agents_manager.connect_agent(token)

    def disconnect_agent(self, token):
        return self.agents_manager.disconnect_agent(token)

    def check_steps(self):
        return self.current_step == self.max_steps + 1

    def get_step(self):
        return self.steps[self.current_step]

    def get_agents_info(self):
        return self.agents_manager.get_agents_info()

    def activate_step(self):
        if self.steps[self.current_step]['flood'] is None:
            return

        self.steps[self.current_step]['flood'].active = True

        for victim in self.steps[self.current_step]['victims']:
            victim.active = True

        for water_sample in self.steps[self.current_step]['water_samples']:
            water_sample.active = True

        for photo in self.steps[self.current_step]['photos']:
            photo.active = True

    def update_steps(self):
        for i in range(self.current_step):
            if self.steps[i]['flood'] is None:
                continue

            if self.steps[i]['flood'].active:
                self.steps[i]['flood'].period -= 1

                if self.steps[i]['flood'].period == 0:
                    self.steps[i]['flood'].active = False

                    for victim in self.steps[i]['victims']:
                        victim.active = False

                    for water_sample in self.steps[i]['water_samples']:
                        water_sample.active = False

                    for photo in self.steps[i]['photos']:
                        photo.active = False

                        for victim in photo.victims:
                            victim.active = False

                else:
                    for victim in self.steps[i]['victims']:
                        if victim.lifetime <= 0:
                            victim.active = False
                        else:
                            victim.lifetime -= 1

                    for photo in self.steps[i]['photos']:
                        for victim in photo.victims:
                            if victim.lifetime <= 0:
                                victim.active = False
                            else:
                                victim.lifetime -= 1

    def execute_actions(self, token_action_dict):
        tokens = self.agents_manager.get_tokens()

        action_results = []
        for token_action_param in token_action_dict:
            token, action, parameters = token_action_param.values()
            result = self._execute(token, action, parameters)

            tokens.remove(token)
            action_results.append(result)

        for token in tokens:
            result = self._execute(token, 'inactive', [])
            action_results.append(result)

        return action_results

    def _execute(self, token, action_name, parameters):
        self.agents_manager.edit_agent(token, 'last_action', action_name)
        self.agents_manager.edit_agent(token, 'last_action_result', False)

        if action_name == 'pass':
            self.agents_manager.edit_agent(token, 'last_action_result', True)
            return {'agent': self.agents_manager.get_agent(token), 'message': ''}

        if action_name == 'inactive':
            self.agents_manager.edit_agent(token, 'last_action', 'pass')
            return {'agent': self.agents_manager.get_agent(token), 'message': 'Agent did not send any action.'}

        error_message = ''
        try:
            if action_name == 'charge':
                self._charge(token, parameters)

            elif action_name == 'move':
                self._move(token, parameters)

            elif action_name == 'rescue_victim':
                self._rescue_victim(token, parameters)

            elif action_name == 'collect_water':
                self._collect_water(token, parameters)

            elif action_name == 'take_photo':
                self._take_photo(token, parameters)

            elif action_name == 'analyze_photo':
                self._analyze_photo(token, parameters)

            elif action_name == 'search_social_asset':
                self._search_social_asset(token, parameters)

            elif action_name == 'get_social_asset':
                self._get_social_asset(token, parameters)

            elif action_name == 'deliver_physical':
                self._delivery_physical(token, parameters)

            elif action_name == 'deliver_virtual':
                self._deliver_virtual(token, parameters)

            return {'agent': self.agents_manager.get_agent(token), 'message': error_message}

        except FailedNoSocialAsset as e:
            error_message = e.message

        except FailedWrongParam as e:
            error_message = e.message

        except FailedNoRoute as e:
            error_message = e.message

        except FailedInsufficientBattery as e:
            error_message = e.message

        except FailedCapacity as e:
            error_message = e.message

        except FailedInvalidKind as e:
            error_message = e.message

        except FailedItemAmount as e:
            error_message = e.message

        except FailedLocation as e:
            return e.message

        except FailedUnknownFacility as e:
            error_message = e.message

        except FailedUnknownItem as e:
            error_message = e.message

        finally:
            return {'agent': self.agents_manager.get_agent(token), 'message': error_message}

    def _charge(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        if self.map.check_location(self.agents_manager.get_agent(token).location, self.cdm_location):
            self.agents_manager.charge_agent(token)
            self.agents_manager.edit_agent(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _move(self, token, parameters):
        if len(parameters) == 1:
            if parameters[0] == 'cdm':
                destination = self.cdm_location
            else:
                raise FailedUnknownFacility('Unknown facility')

        elif len(parameters) <= 0:
            raise FailedWrongParam('Less than 1 parameter was given')

        elif len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given')

        else:
            destination = parameters

        agent = self.agents_manager.get_agent(token)

        if self.map.check_location(agent.location, destination):
            self.agents_manager.edit_agent(token, 'route', [])
            self.agents_manager.edit_agent(token, 'destination_distance', 0)
            self.agents_manager.edit_agent(token, 'last_action_result', True)

        elif not agent.check_battery():
            raise FailedInsufficientBattery('Not enough battery to complete this step.')

        else:
            nodes = []
            for i in range(self.current_step):
                if self.steps[i]['flood'] and self.steps[i]['flood'].active:
                    nodes.extend(self.steps[i]['flood'].list_of_nodes)

            if not agent.route:
                result, route, distance = self.map.get_route(agent.location, destination, agent.role, agent.speed, nodes)

                if not result:
                    self.agents_manager.edit_agent(token, 'route', [])
                    self.agents_manager.edit_agent(token, 'destination_distance', 0)

                else:
                    self.agents_manager.edit_agent(token, 'route', route)
                    self.agents_manager.edit_agent(token, 'destination_distance', distance)

            if self.agents_manager.get_agent(token).destination_distance:
                self.agents_manager.edit_agent(token, 'last_action_result', 'True')
                self.agents_manager.discharge_agent(token)
                self.agents_manager.update_agent_location(token)

    def _rescue_victim(self, token, parameters):
        if len(parameters) > 0:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get_agent(token)

        for i in range(self.current_step):
            for victim in self.steps[i]['victims']:
                if victim.active and self.map.check_location(victim.location, agent.location):
                    victim.active = False
                    self.agents_manager.add_physical(token, victim)
                    self.agents_manager.edit_agent(token, 'last_action_result', True)
                    return

            for photo in self.steps[i]['photos']:
                for victim in photo.victims:
                    if victim.active and self.map.check_location(victim.location, agent.location):
                        victim.active = False
                        self.agents_manager.add_physical(token, victim)
                        self.agents_manager.edit_agent(token, 'last_action_result', True)
                        return

        raise FailedUnknownItem('No victim by the given location is known.')

    def _collect_water(self, token, parameters):
        if len(parameters) > 0:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get_agent(token)
        for i in range(self.current_step):
            for water_sample in self.steps[i]['water_samples']:
                if water_sample.active and self.map.check_location(water_sample.location, agent.location):
                    water_sample.active = False
                    self.agents_manager.add_physical(token, water_sample)
                    self.agents_manager.edit_agent(token, 'last_action_result', True)
                    return

        raise FailedLocation('The agent is not in a location with a water sample.')

    def _take_photo(self, token, parameters):
        if len(parameters) > 0:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get_agent(token)
        for i in range(self.current_step):
            for photo in self.steps[i]['photos']:
                if photo.active and self.map.check_location(photo.location, agent.location):
                    photo.active = False
                    self.agents_manager.add_virtual(token, photo)
                    self.agents_manager.edit_agent(token, 'last_action_result', True)
                    return

        raise FailedLocation('The agent is not in a location with a photograph event.')

    def _analyze_photo(self, token, parameters):
        if len(parameters) > 0:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get_agent(token)
        if len(agent.virtual_storage_vector) == 0:
            raise FailedItemAmount('The agent has no photos to analyze.')

        identifiers = []
        for photo in agent.virtual_storage_vector:
            for victim in photo.victims:
                identifiers.append(victim.identifier)

        self._update_victims_state(identifiers)
        self.agents_manager.edit_agent(token, 'last_action_result', True)
        self.agents_manager.clear_agent_virtual_storage(token)

    def _search_social_asset(self, token, parameters):
        if len(parameters) != 1:
            raise FailedWrongParam('Wrong amount of parameters given.')

        agent = self.agents_manager.get_agent(token)
        for social_asset in self.social_assets:
            if social_asset in agent.social_assets:
                continue

            if social_asset.active and social_asset.profession == parameters[0]:
                self.agents_manager.add_social_asset(token, social_asset)
                self.agents_manager.edit_agent(token, 'last_action_result', True)
                return

        raise FailedNoSocialAsset('No social asset found for the needed purposes.')

    def _get_social_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Wrong amount of parameters given.')

        agent = self.agents_manager.get_agent(token)

        if agent.role == 'drone':
            raise FailedInvalidKind('Agent role does not support carrying social asset.')

        for social_asset in self.social_assets:
            if social_asset in agent.social_assets:
                if social_asset.active and self.map.check_location(agent.location, social_asset.location):
                    self.agents_manager.add_physical(token, social_asset)
                    self.agents_manager.edit_agent(token, 'last_action_result', True)
                    social_asset.active = False
                    return

        raise FailedNoSocialAsset('Invalid social asset requested.')

    def _delivery_physical(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        agent = self.agents_manager.get_agent(token)
        if self.map.check_location(agent.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.agents_manager.deliver_physical(token, parameters[0])

            else:
                delivered_items = self.agents_manager.deliver_physical(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.agents_manager.edit_agent(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _deliver_virtual(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        agent = self.agents_manager.get_agent(token)
        if self.map.check_location(agent.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.agents_manager.deliver_physical(token, parameters[0])

            else:
                delivered_items = self.agents_manager.deliver_physical(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.agents_manager.edit_agent(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _update_victims_state(self, identifiers):
        for i in range(self.current_step):
            for victim in self.steps[i]['victims']:
                if victim.identifier in identifiers:
                    victim.active = False
                    identifiers.remove(victim.identifier)

                if not identifiers:
                    return

    def __del__(self):
        del self.map
