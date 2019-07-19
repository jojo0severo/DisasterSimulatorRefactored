from simulation_engine.exceptions.exceptions import *
from simulation_engine.simulation_helpers.map import Map
from simulation_engine.generator.generator import Generator
from simulation_engine.simulation_helpers.agents_manager import AgentsManager
from simulation_engine.simulation_helpers.social_assets_manager import SocialAssetsManager


class Cycle:
    def __init__(self, config):
        self.map = Map(config['map']['maps'][0], config['map']['proximity'])
        self.actions = config['actions']
        self.max_steps = config['map']['steps']
        generator = Generator(config, self.map)
        self.steps = generator.generate_events()
        self.max_floods = generator.flood_id
        self.max_victims = generator.victim_id
        self.max_photos = generator.photo_id
        self.max_water_samples = generator.water_sample_id
        self.delivered_items = []
        self.current_step = 0
        self.cdm_location = (config['map']['centerLat'], config['map']['centerLon'])
        self.agents_manager = AgentsManager(config['agents'], self.cdm_location)
        self.social_assets_manager = SocialAssetsManager(config['map'], config['socialAssets'])

    def restart(self, config_file):
        self.map.restart(config_file['map']['maps'][0], config_file['map']['proximity'])
        generator = Generator(config_file, self.map)
        self.steps = generator.generate_events()
        self.max_floods = generator.flood_id
        self.max_victims = generator.victim_id
        self.max_photos = generator.photo_id
        self.max_water_samples = generator.water_sample_id
        self.delivered_items = []
        self.current_step = 0
        self.max_steps = config_file['map']['steps']
        self.cdm_location = (config_file['map']['centerLat'], config_file['map']['centerLon'])
        self.agents_manager.restart(config_file['agents'], self.cdm_location)
        self.social_assets_manager.restart(config_file['map'], config_file['socialAssets'])

    def connect_agent(self, token):
        return self.agents_manager.connect_agent(token)

    def connect_social_asset(self, token):
        return self.social_assets_manager.connect_social_asset(token)

    def disconnect_agent(self, token):
        return self.agents_manager.disconnect_agent(token)

    def disconnect_social_asset(self, token):
        return self.social_assets_manager.disconnect_social_asset(token)

    def get_agents_info(self):
        return self.agents_manager.get_agents_info()

    def get_active_agents_info(self):
        return self.agents_manager.get_active_agents_info()

    def get_assets_info(self):
        return self.social_assets_manager.get_social_assets_info()

    def get_active_assets_info(self):
        return self.social_assets_manager.get_active_social_assets_info()

    def get_step(self):
        return self.steps[self.current_step]

    def get_previous_steps(self):
        previous_steps = []
        for i in range(self.current_step):
            if self.steps[i]['flood'] is None:
                continue

            if self.steps[i]['flood'].active:
                previous_steps.append(self.steps[i])

        return previous_steps

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

    def check_steps(self):
        return self.current_step == self.max_steps

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
        agents_tokens = self.agents_manager.get_tokens()
        assets_tokens = self.social_assets_manager.get_tokens()

        special_action_tokens = []

        action_results = []
        for token_action_param in token_action_dict:
            token, action, parameters = token_action_param.values()

            if action == 'carry' or action == 'getCarried':
                special_action_tokens.append([token, action, parameters])
                continue

            if token in agents_tokens:
                result = self._execute_agent_action(token, action, parameters)
                agents_tokens.remove(token)

            else:
                result = self._execute_asset_action(token, action, parameters)
                assets_tokens.remove(token)

            action_results.append(result)

        results, tokens = self._execute_special_actions(special_action_tokens)
        action_results.extend(results)

        for token in tokens:
            if self.agents_manager.get_agent(token) is None:
                assets_tokens.remove(token)
            else:
                agents_tokens.remove(token)

        for token in agents_tokens:
            action_results.append(self._execute_agent_action(token, 'inactive', []))

        for token in assets_tokens:
            action_results.append(self._execute_asset_action(token, 'inactive', []))

        return action_results

    def _execute_special_actions(self, special_action_tokens):
        action_results = []
        computed_tokens = []
        for i in range(len(special_action_tokens)):
            token, action, parameters = special_action_tokens[i]

            if token in computed_tokens:
                continue

            if self.agents_manager.get_agent(token) is None:
                if self.social_assets_manager.get_social_asset(token).carried:
                    action_results.append({
                        'social_asset': self.social_assets_manager.get_social_asset(token),
                        'message': 'Social asset can not do any action while being carried.'
                    })
                    continue
            else:
                if self.agents_manager.get_agent(token).carried:
                    action_results.append({
                        'agent': self.agents_manager.get_agent(token),
                        'message': 'Agent can not do any action while being carried.'
                    })
                    continue

            if not self._check_abilities_and_resources(token, action):
                if self.agents_manager.get_agent(token) is None:
                    self.social_assets_manager.edit_social_asset(token, 'last_action', action)
                    self.social_assets_manager.edit_social_asset(token, 'last_action_result', False)
                    action_results.append({
                        'social_asset': self.social_assets_manager.get_social_asset(token),
                        'message': 'Social asset does not have the abilities or resources to do the action'
                    })
                else:
                    self.agents_manager.edit_agent(token, 'last_action', action)
                    self.agents_manager.edit_agent(token, 'last_action_result', False)
                    action_results.append({
                        'agent': self.social_assets_manager.get_social_asset(token),
                        'message': 'Agent does not have the abilities or resources to do the action'
                    })

            elif action == 'carry':
                if len(parameters) != 1:
                    if self.agents_manager.get_agent(token) is None:
                        self.social_assets_manager.edit_social_asset(token, 'last_action', 'carry')
                        self.social_assets_manager.edit_social_asset(token, 'last_action_result', False)
                        action_results.append({
                            'social_asset': self.social_assets_manager.get_social_asset(token),
                            'message': 'Wrong amount of parameters given.'
                        })

                    else:
                        self.agents_manager.edit_agent(token, 'last_action', 'carry')
                        self.agents_manager.edit_agent(token, 'last_action_result', False)
                        action_results.append({
                            'agent': self.agents_manager.get_agent(token),
                            'message': 'Wrong amount o parameters given.'
                        })
                else:
                    result = self._carry(i, special_action_tokens)
                    if result[1] is None:
                        if self.agents_manager.get_agent(token) is None:
                            action_results.append({
                                'social_asset': self.social_assets_manager.get_social_asset(token),
                                'message': 'No other actor wanted to be carried.'
                            })
                        else:
                            action_results.append({
                                'agent': self.agents_manager.get_agent(token),
                                'message': 'No other actor wanted to be carried.'
                            })

                    else:
                        if self.agents_manager.get_agent(token) is None:
                            action_results.append({
                                'social_asset': self.social_assets_manager.get_social_asset(token),
                                'message': ''
                            })
                        else:
                            action_results.append({
                                'agent': self.agents_manager.get_agent(token),
                                'message': ''
                            })

                        if self.agents_manager.get_agent(result[1]) is None:
                            action_results.append({
                                'social_asset': self.social_assets_manager.get_social_asset(result[1]),
                                'message': ''
                            })
                        else:
                            action_results.append({
                                'agent': self.agents_manager.get_agent(result[1]),
                                'message': ''
                            })

                        computed_tokens.append(result[1])

            else:
                if len(parameters) != 1:
                    if self.agents_manager.get_agent(token) is None:
                        self.social_assets_manager.edit_social_asset(token, 'last_action', 'get_carried')
                        self.social_assets_manager.edit_social_asset(token, 'last_action_result', False)
                        action_results.append({
                            'social_asset': self.social_assets_manager.get_social_asset(token),
                            'message': 'Wrong amount of parameters given.'
                        })

                    else:
                        self.agents_manager.edit_agent(token, 'last_action', 'get_carried')
                        self.agents_manager.edit_agent(token, 'last_action_result', False)
                        action_results.append({
                            'agent': self.agents_manager.get_agent(token),
                            'message': 'Wrong amount o parameters given.'
                        })
                else:
                    result = self._get_carried(i, special_action_tokens)
                    if result[1] is None:
                        if self.agents_manager.get_agent(token) is None:
                            action_results.append({
                                'social_asset': self.social_assets_manager.get_social_asset(token),
                                'message': 'No other actor wanted to be carried or accomplishes the requirements to be.'
                            })
                        else:
                            action_results.append({
                                'agent': self.agents_manager.get_agent(token),
                                'message': 'No other actor wanted to be carried or accomplishes the requirements to be..'
                            })

                    else:
                        if self.agents_manager.get_agent(token) is None:
                            action_results.append({
                                'social_asset': self.social_assets_manager.get_social_asset(token),
                                'message': ''
                            })
                        else:
                            action_results.append({
                                'agent': self.agents_manager.get_agent(token),
                                'message': ''
                            })

                        if self.agents_manager.get_agent(result[1]) is None:
                            action_results.append({
                                'social_asset': self.social_assets_manager.get_social_asset(result[1]),
                                'message': ''
                            })
                        else:
                            action_results.append({
                                'agent': self.agents_manager.get_agent(result[1]),
                                'message': ''
                            })

                        computed_tokens.append(result[1])

            computed_tokens.append(token)

        return action_results, computed_tokens

    def _execute_agent_action(self, token, action_name, parameters):
        self.agents_manager.edit_agent(token, 'last_action', action_name)
        self.agents_manager.edit_agent(token, 'last_action_result', False)

        if action_name == 'inactive':
            self.agents_manager.edit_agent(token, 'last_action', 'pass')
            return {'agent': self.agents_manager.get_agent(token), 'message': 'Agent did not send any action.'}

        if action_name not in self.actions:
            return {'agent': self.agents_manager.get_agent(token),
                    'message': 'Wrong action name given.'}

        if not self.agents_manager.get_agent(token).is_active:
            return {'agent': self.agents_manager.get_agent(token), 'message': 'Agent is not active.'}

        if self.agents_manager.get_agent(token).carried:
            return {'agent': self.agents_manager.get_agent(token),
                    'message': 'Agent can not do any action while being carried.'}

        if action_name == 'pass':
            self.agents_manager.edit_agent(token, 'last_action_result', True)
            return {'agent': self.agents_manager.get_agent(token), 'message': ''}

        if not self._check_abilities_and_resources(token, action_name):
            return {'agent': self.agents_manager.get_agent(token),
                    'message': 'Agent does not have the abilities or resources to complete the action.'}

        error_message = ''
        try:
            if action_name == 'charge':
                self._charge_agent(token, parameters)

            elif action_name == 'move':
                self._move_agent(token, parameters)

            elif action_name == 'rescueVictim':
                self._rescue_victim_agent(token, parameters)

            elif action_name == 'collectWater':
                self._collect_water_agent(token, parameters)

            elif action_name == 'takePhoto':
                self._take_photo_agent(token, parameters)

            elif action_name == 'analyzePhoto':
                self._analyze_photo_agent(token, parameters)

            elif action_name == 'searchSocialAsset':
                self._search_social_asset_agent(token, parameters)

            elif action_name == 'deliverPhysical':
                self._deliver_physical_agent(token, parameters)

            elif action_name == 'deliverVirtual':
                self._deliver_virtual_agent(token, parameters)

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
            error_message = e.message

        except FailedUnknownFacility as e:
            error_message = e.message

        except FailedUnknownItem as e:
            error_message = e.message

        except Exception as e:
            error_message = str(e)

        finally:
            return {'agent': self.agents_manager.get_agent(token), 'message': error_message}

    def _execute_asset_action(self, token, action_name, parameters):
        self.social_assets_manager.edit_social_asset(token, 'last_action', action_name)
        self.social_assets_manager.edit_social_asset(token, 'last_action_result', False)

        if action_name == 'inactive':
            self.social_assets_manager.edit_social_asset(token, 'last_action', 'pass')
            return {'social_asset': self.social_assets_manager.get_social_asset(token),
                    'message': 'Social asset did not send any action.'}

        if action_name not in self.actions:
            return {'social_asset': self.social_assets_manager.get_social_asset(token),
                    'message': 'Wrong action name given.'}

        if not self.social_assets_manager.get_social_asset(token).is_active:
            return {'social_asset': self.social_assets_manager.get_social_asset(token),
                    'message': 'Social asset is not active.'}

        if self.social_assets_manager.get_social_asset(token).carried:
            return {'social_asset': self.social_assets_manager.get_social_asset(token),
                    'message': 'Social asset can not do any action while being carried.'}

        if action_name == 'pass':
            self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)
            return {'social_asset': self.social_assets_manager.get_social_asset(token), 'message': ''}

        if not self._check_abilities_and_resources(token, action_name):
            return {'social_asset': self.social_assets_manager.get_social_asset(token),
                    'message': 'Social asset does not have the abilities or resources to complete the action.'}

        error_message = ''
        try:
            if action_name == 'move':
                self._move_asset(token, parameters)

            elif action_name == 'rescueVictim':
                self._rescue_victim_asset(token, parameters)

            elif action_name == 'collectWater':
                self._collect_water_asset(token, parameters)

            elif action_name == 'takePhoto':
                self._take_photo_asset(token, parameters)

            elif action_name == 'analyzePhoto':
                self._analyze_photo_asset(token, parameters)

            elif action_name == 'searchSocialAsset':
                self._search_social_asset_asset(token, parameters)

            elif action_name == 'deliverPhysical':
                self._deliver_physical_asset(token, parameters)

            elif action_name == 'deliverVirtual':
                self._deliver_virtual_asset(token, parameters)

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
            error_message = e.message

        except FailedUnknownFacility as e:
            error_message = e.message

        except FailedUnknownItem as e:
            error_message = e.message

        except UnableToReach as e:
            error_message = e.message

        except Exception as e:
            error_message = str(e)

        finally:
            return {'social_asset': self.social_assets_manager.get_social_asset(token), 'message': error_message}

    def _check_abilities_and_resources(self, token, action):
        if self.agents_manager.get_agent(token) is None:
            actor = self.social_assets_manager.get_social_asset(token)
        else:
            actor = self.agents_manager.get_agent(token)

        if actor is None:
            exit('Internal error. Non registered token requested.')

        for ability in self.actions[action]['abilities']:
            if ability not in actor.abilities:
                return False

        for resource in self.actions[action]['resources']:
            if resource not in actor.resources:
                return False

        return True

    def _carry(self, current_position, special_action_tokens):
        token, action, parameters = special_action_tokens[current_position]

        for j in range(current_position + 1, len(special_action_tokens)):
            sub_token, sub_action, sub_parameters = special_action_tokens[j]
            if sub_action == 'getCarried' and sub_token == parameters[0] and sub_parameters[0] == token:
                if self.agents_manager.get_agent(token) is None:
                    self.social_assets_manager.edit_social_asset(token, 'last_action', 'carry')
                    self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)

                else:
                    self.agents_manager.edit_agent(token, 'last_action', 'carry')
                    self.agents_manager.edit_agent(token, 'last_action_result', True)

                if self.agents_manager.get_agent(sub_token) is None:
                    self.social_assets_manager.edit_social_asset(sub_token, 'last_action', 'getCarried')
                    self.social_assets_manager.edit_social_asset(sub_token, 'last_action_result', True)
                    self.social_assets_manager.edit_social_asset(sub_token, 'carried', True)

                else:
                    self.agents_manager.edit_agent(sub_token, 'last_action', 'getCarried')
                    self.agents_manager.edit_agent(sub_token, 'last_action_result', True)
                    self.social_assets_manager.edit_social_asset(sub_token, 'carried', True)

                return token, sub_token

        if self.agents_manager.get_agent(token) is None:
            self.social_assets_manager.edit_social_asset(token, 'last_action', 'carry')
            self.social_assets_manager.edit_social_asset(token, 'last_action_result', False)

        else:
            self.agents_manager.edit_agent(token, 'last_action', 'carry')
            self.agents_manager.edit_agent(token, 'last_action_result', False)

        return token, None

    def _get_carried(self, current_position, special_action_tokens):
        token, action, parameters = special_action_tokens[current_position]

        for j in range(current_position + 1, len(special_action_tokens)):
            sub_token, sub_action, sub_parameters = special_action_tokens[j]
            if sub_action == 'carry' and sub_token == parameters[0] and sub_parameters[0] == token:
                if self.agents_manager.get_agent(token) is None:
                    self.social_assets_manager.edit_social_asset(token, 'last_action', 'getCarried')
                    self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)
                    self.social_assets_manager.edit_social_asset(sub_token, 'carried', True)

                else:
                    self.agents_manager.edit_agent(token, 'last_action', 'getCarried')
                    self.agents_manager.edit_agent(token, 'last_action_result', True)
                    self.agents_manager.edit_agent(token, 'carried', True)

                if self.agents_manager.get_agent(sub_token) is None:
                    self.social_assets_manager.edit_social_asset(sub_token, 'last_action', 'carry')
                    self.social_assets_manager.edit_social_asset(sub_token, 'last_action_result', True)

                else:
                    self.agents_manager.edit_agent(sub_token, 'last_action', 'carry')
                    self.agents_manager.edit_agent(sub_token, 'last_action_result', True)

                return token, sub_token

        if self.agents_manager.get_agent(token) is None:
            self.social_assets_manager.edit_social_asset(token, 'last_action', 'getCarried')
            self.social_assets_manager.edit_social_asset(token, 'last_action_result', False)

        else:
            self.agents_manager.edit_agent(token, 'last_action', 'getCarried')
            self.agents_manager.edit_agent(token, 'last_action_result', False)

        return token, None

    def _charge_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        if self.map.check_location(self.agents_manager.get_agent(token).location, self.cdm_location):
            self.agents_manager.charge_agent(token)
            self.agents_manager.edit_agent(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _move_agent(self, token, parameters):
        if len(parameters) == 1:
            if parameters[0] == 'cdm':
                destination = self.cdm_location
            else:
                raise FailedUnknownFacility('Unknown facility.')

        elif len(parameters) <= 0:
            raise FailedWrongParam('Less than 1 parameter was given.')

        elif len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        else:
            destination = parameters

        agent = self.agents_manager.get_agent(token)

        if not agent.check_battery():
            raise FailedInsufficientBattery('Not enough battery to complete this step.')

        elif self.map.check_location(agent.location, destination):
            self.agents_manager.edit_agent(token, 'route', [])
            self.agents_manager.edit_agent(token, 'destination_distance', 0)
            self.agents_manager.edit_agent(token, 'last_action_result', True)

        else:
            if not agent.route or destination != agent.route[-1]:
                nodes = []
                for i in range(self.current_step):
                    if self.steps[i]['flood'] and self.steps[i]['flood'].active:
                        nodes.extend(self.steps[i]['flood'].list_of_nodes)

                result, route, distance = self.map.get_route(agent.location, destination, agent.role, agent.speed, nodes)

                if not result:
                    self.agents_manager.edit_agent(token, 'route', [])
                    self.agents_manager.edit_agent(token, 'destination_distance', 0)

                    raise UnableToReach('Agent is not capable of entering flood locations.')

                else:
                    self.agents_manager.edit_agent(token, 'route', route)
                    self.agents_manager.edit_agent(token, 'destination_distance', distance)

            if self.agents_manager.get_agent(token).destination_distance:
                self.agents_manager.update_agent_location(token)
                _, _, distance = self.map.get_route(agent.location, destination, agent.role, agent.speed, [])
                self.agents_manager.edit_agent(token, 'destination_distance', distance)
                self.agents_manager.edit_agent(token, 'last_action_result', True)
                self.agents_manager.discharge_agent(token)

    def _move_asset(self, token, parameters):
        if len(parameters) == 1:
            if parameters[0] == 'cdm':
                destination = self.cdm_location
            else:
                raise FailedUnknownFacility('Unknown facility.')

        elif len(parameters) <= 0:
            raise FailedWrongParam('Less than 1 parameter was given.')

        elif len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        else:
            destination = parameters

        asset = self.social_assets_manager.get_social_asset(token)

        if self.map.check_location(asset.location, destination):
            self.social_assets_manager.edit_social_asset(token, 'route', [])
            self.social_assets_manager.edit_social_asset(token, 'destination_distance', 0)
            self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)

        else:
            if not asset.route:
                nodes = []
                for i in range(self.current_step):
                    if self.steps[i]['flood'] and self.steps[i]['flood'].active:
                        nodes.extend(self.steps[i]['flood'].list_of_nodes)

                result, route, distance = self.map.get_route(asset.location, destination, 'car', asset.speed, nodes)

                if not result:
                    self.social_assets_manager.edit_social_asset(token, 'route', [])
                    self.social_assets_manager.edit_social_asset(token, 'destination_distance', 0)

                    raise UnableToReach('Asset is not capable of entering flood locations.')

                else:
                    self.social_assets_manager.edit_social_asset(token, 'route', route)
                    self.social_assets_manager.edit_social_asset(token, 'destination_distance', distance)

            if self.social_assets_manager.get_social_asset(token).destination_distance:
                self.social_assets_manager.update_social_asset_location(token)
                _, _, distance = self.map.get_route(asset.location, destination, 'car', asset.speed, [])
                self.social_assets_manager.edit_social_asset(token, 'destination_distance', distance)
                self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)

    def _rescue_victim_agent(self, token, parameters):
        if parameters:
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

    def _rescue_victim_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get_social_asset(token)

        for i in range(self.current_step):
            for victim in self.steps[i]['victims']:
                if victim.active and self.map.check_location(victim.location, asset.location):
                    victim.active = False
                    self.social_assets_manager.add_physical(token, victim)
                    self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)
                    return

            for photo in self.steps[i]['photos']:
                for victim in photo.victims:
                    if victim.active and self.map.check_location(victim.location, asset.location):
                        victim.active = False
                        self.social_assets_manager.add_physical(token, victim)
                        self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)
                        return

        raise FailedUnknownItem('No victim by the given location is known.')

    def _collect_water_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get_agent(token)
        for i in range(self.current_step):
            for water_sample in self.steps[i]['water_samples']:
                if water_sample.active and self.map.check_location(water_sample.location, agent.location):
                    water_sample.active = False
                    self.agents_manager.add_physical(token, water_sample)
                    self.agents_manager.edit_agent(token, 'last_action_result', True)
                    return

        raise FailedLocation('The agent is not in a location with a water sample event.')

    def _collect_water_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get_social_asset(token)
        for i in range(self.current_step):
            for water_sample in self.steps[i]['water_samples']:
                if water_sample.active and self.map.check_location(water_sample.location, asset.location):
                    water_sample.active = False
                    self.social_assets_manager.add_physical(token, water_sample)
                    self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)
                    return

        raise FailedLocation('The asset is not in a location with a water sample event.')

    def _take_photo_agent(self, token, parameters):
        if parameters:
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

    def _take_photo_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get_social_asset(token)
        for i in range(self.current_step):
            for photo in self.steps[i]['photos']:
                if photo.active and self.map.check_location(photo.location, asset.location):
                    photo.active = False
                    self.social_assets_manager.add_virtual(token, photo)
                    self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)
                    return

        raise FailedLocation('The asset is not in a location with a photograph event.')

    def _analyze_photo_agent(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        agent = self.agents_manager.get_agent(token)
        if len(agent.virtual_storage_vector) == 0:
            raise FailedItemAmount('The agent has no photos to analyze.')

        photo_identifiers = []
        victim_identifiers = []
        for photo in agent.virtual_storage_vector:
            for victim in photo.victims:
                victim_identifiers.append(victim.identifier)

            photo_identifiers.append(photo.identifier)

        self._update_photos_state(photo_identifiers)
        self.agents_manager.edit_agent(token, 'last_action_result', True)
        self.agents_manager.clear_agent_virtual_storage(token)

    def _analyze_photo_asset(self, token, parameters):
        if parameters:
            raise FailedWrongParam('Parameters were given.')

        asset = self.social_assets_manager.get_social_asset(token)
        if len(asset.virtual_storage_vector) == 0:
            raise FailedItemAmount('The asset has no photos to analyze.')

        photo_identifiers = []
        victim_identifiers = []
        for photo in asset.virtual_storage_vector:
            for victim in photo.victims:
                victim_identifiers.append(victim.identifier)

            photo_identifiers.append(photo.identifier)

        self._update_photos_state(photo_identifiers)
        self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)
        self.social_assets_manager.clear_social_asset_virtual_storage(token)

    def _search_social_asset_agent(self, token, parameters):
        if not self.social_assets_manager.get_tokens():
            raise FailedNoSocialAsset('No social asset connected.')

        if len(parameters) != 1:
            raise FailedWrongParam('Wrong amount of parameters given.')

        closer_asset = None
        distance = 999999
        for asset_token in self.social_assets_manager.get_tokens():
            asset = self.social_assets_manager.get_social_asset(asset_token)
            if asset.is_active:
                if parameters[0] == asset.profession:
                    current_dist = self.map.euclidean_distance(self.agents_manager.get_agent(token).location, asset.location)
                    if current_dist <= distance:
                        distance = current_dist
                        closer_asset = asset

        if closer_asset is None:
            raise FailedNoSocialAsset('No social asset found for the needed purposes.')

        else:
            self.agents_manager.add_social_asset(token, closer_asset)
            self.agents_manager.edit_agent(token, 'last_action_result', True)

    def _search_social_asset_asset(self, token, parameters):
        if not self.social_assets_manager.get_tokens():
            raise FailedNoSocialAsset('No social asset connected.')

        if len(parameters) != 1:
            raise FailedWrongParam('Wrong amount of parameters given.')

        closer_asset = None
        distance = 999999
        for asset_token in self.social_assets_manager.get_tokens():
            asset = self.social_assets_manager.get_social_asset(asset_token)
            if asset.is_active:
                if parameters[0] == asset.profession:
                    current_dist = self.map.euclidean_distance(
                        self.social_assets_manager.get_social_asset(token).location, asset.location)
                    if current_dist <= distance:
                        distance = current_dist
                        closer_asset = asset

        if closer_asset is None:
            raise FailedNoSocialAsset('No social asset found for the needed purposes.')

        else:
            self.social_assets_manager.add_social_asset(token, closer_asset)
            self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)

    def _deliver_physical_agent(self, token, parameters):
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

    def _deliver_physical_asset(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        asset = self.social_assets_manager.get_social_asset(token)
        if self.map.check_location(asset.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.social_assets_manager.deliver_physical(token, parameters[0])

            else:
                delivered_items = self.social_assets_manager.deliver_physical(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _deliver_virtual_agent(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        agent = self.agents_manager.get_agent(token)
        if self.map.check_location(agent.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.agents_manager.deliver_virtual(token, parameters[0])

            else:
                delivered_items = self.agents_manager.deliver_virtual(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.agents_manager.edit_agent(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _deliver_virtual_asset(self, token, parameters):
        if len(parameters) < 1:
            raise FailedWrongParam('Less than 1 parameter was given.')

        if len(parameters) > 2:
            raise FailedWrongParam('More than 2 parameters were given.')

        asset = self.social_assets_manager.get_social_asset(token)
        if self.map.check_location(asset.location, self.cdm_location):
            if len(parameters) == 1:
                delivered_items = self.social_assets_manager.deliver_virtual(token, parameters[0])

            else:
                delivered_items = self.social_assets_manager.deliver_virtual(token, parameters[0], parameters[1])

            self.delivered_items.append({
                'token': token,
                'kind': 'physical',
                'items': delivered_items,
                'step': self.current_step})

            self.social_assets_manager.edit_social_asset(token, 'last_action_result', True)

        else:
            raise FailedLocation('The agent is not located at the CDM.')

    def _update_photos_state(self, identifiers):
        for i in range(self.current_step):
            for photo in self.steps[i]['photos']:
                if photo.identifier in identifiers:
                    identifiers.remove(photo.identifier)
                    photo.analyzed = True
                    for victim in photo.victims:
                        victim.active = True
