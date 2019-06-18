from simulation_environment.exceptions.exceptions import *


class ActionExecutor:

    def __init__(self, router, cdm_location):
        self.router = router
        self.cdm_location = cdm_location

    def execute_actions(self, steps, agents, token_action_list):
        action_results = []

        for token, action in token_action_list:
            action_name = action[0]
            parameters = action[1]
            result = self.execute(steps, agents[token], action_name, parameters)

            action_results.append((token, result))

        return action_results

    def execute(self, steps, agent, action_name, parameters):
        if action_name is None:
            return 'No action given.'

        elif action_name == 'pass':
            agent.last_action_result = True
            return
        try:
            if action_name == 'move':
                if len(parameters) == 1:
                    if parameters[0] == 'cdm':
                        location = self.cdm_location
                    else:
                        raise FailedUnknownFacility('Unknown facility')
                else:
                    raise FailedWrongParam('More than 1 or less than than 1 parameters were given')

                if self.check_location(agent.location, location):
                    agent.route, distance = [], 0
                    return

                if not agent.check_battery():
                    raise FailedInsufficientBattery('Not enough battery to complete this step.')

                list_of_nodes = []
                for event in self.world.events[:step]:
                    if event['flood'] and event['flood'].active:
                        list_of_nodes.extend(event['flood'].list_of_nodes)

                if not agent.route:
                    self.get_route(agent, location, list_of_nodes)
                elif agent.route[0] != location:
                    self.get_route(agent, location, list_of_nodes)

                if not agent.destination_distance:
                    return

                agent.last_action_result = True
                agent.discharge()
                dict_location = agent.route.pop(0)
                agent.location = [dict_location['lat'], dict_location['lon']]

            elif action_name == 'deliver_physical':
                if len(parameters) < 1 or len(parameters) > 2:
                    raise FailedWrongParam('Less than 1 or more than 2 parameters were given.')

                if self.check_location(agent.location, self.cdm_location):
                    if len(parameters) == 1:
                        self.agent_delivery(agent=agent, kind='physical', item=parameters[0])

                    elif len(parameters) == 2:
                        self.agent_delivery(agent=agent, kind='physical', item=parameters[0], amount=parameters[1])

                    agent.last_action_result = True
                else:
                    raise FailedLocation('The agent is not located at the CDM.')

            elif action_name == 'deliver_virtual':
                if len(parameters) < 1 or len(parameters) > 2:
                    raise FailedWrongParam('Less than 1 or more than 2 parameters were given.')

                if self.check_location(agent.location, self.cdm_location):
                    if len(parameters) == 1:
                        self.agent_delivery(agent=agent, kind='virtual', item=parameters[0])

                    elif len(parameters) == 2:
                        self.agent_delivery(agent=agent, kind='virtual', item=parameters[0], amount=parameters[1])

                    agent.last_action_result = True
                else:
                    raise FailedLocation('The agent is not located at the CDM.')

            elif action_name == 'charge':
                if len(parameters) > 0:
                    raise FailedWrongParam('Parameters were given.')

                if self.check_location(agent.location, self.cdm_location):
                    agent.charge()
                    agent.last_action_result = True

                else:
                    raise FailedLocation('The agent is not located at the CDM.')

            elif action_name == 'rescue_victim':
                if len(parameters) > 0:
                    raise FailedWrongParam('Parameters were given.')

                for event in self.world.events:
                    for victim in event['victims']:

                        if victim.active and self.check_location(victim.location, agent.location):
                            agent.add_physical_item(victim)
                            victim.active = False
                            agent.last_action_result = True
                            return

                raise FailedUnknownItem('No victim by the given location is known.')

            elif action_name == 'collect_water':
                if len(parameters) > 0:
                    raise FailedWrongParam('Parameters were given.')

                for event in self.world.events:
                    for water_sample in event['water_samples']:

                        if water_sample.active and self.check_location(water_sample.location, agent.location):
                            agent.add_physical_item(water_sample)
                            water_sample.active = False
                            agent.last_action_result = True
                            return

                raise FailedLocation('The agent is not in a location with a water sample.')

            elif action_name == 'photograph':
                if len(parameters) > 0:
                    raise FailedWrongParam('Parameters were given.')

                for event in self.world.events:
                    for photo in event['photos']:

                        if photo.active and self.check_location(photo.location, agent.location):
                            agent.add_virtual_item(photo)
                            photo.active = False
                            agent.last_action_result = True
                            return

                raise FailedLocation('The agent is not in a location with a photograph event.')

            elif action_name == 'search_social_asset':
                if len(parameters) != 1:
                    raise FailedWrongParam('Wrong amount of parameters given.')

                for social_asset in self.world.social_assets:
                    if social_asset in agent.social_assets:
                        continue

                    if social_asset.active and social_asset.profession == parameters[0]:
                        agent.social_assets.append(social_asset)
                        agent.last_action_result = True
                        return

                raise FailedNoSocialAsset('No social asset found for the needed purposes.')

            elif action_name == 'get_social_asset':
                if parameters:
                    raise FailedWrongParam('Wrong amount of parameters given.')

                if agent.role == 'drone':
                    raise FailedInvalidKind('Agent role does not support carrying social asset.')

                for social_asset in self.world.social_assets:
                    for social_asset_agent in agent.social_assets:
                        if social_asset_agent == social_asset:
                            if self.check_location(agent.location, social_asset.location) and social_asset.active:
                                agent.add_physical(social_asset)
                                agent.last_action_result = True
                                social_asset.active = False
                                return

                raise FailedNoSocialAsset('Invalid social asset requested.')

            elif action_name == 'analyze_photo':
                if len(parameters) > 0:
                    raise FailedWrongParam('Parameters were given.')

                if len(agent.virtual_storage_vector) == 0:
                    raise FailedItemAmount('The agent has no photos to analyze.')

                for photo in agent.virtual_storage_vector:
                    for victim in photo.victims:
                        victim.active = True

                agent.last_action_result = True
                agent.virtual_storage_vector.clear()
                agent.virtual_storage = agent.virtual_capacity

            else:
                return 'Wrong action name.'

        except FailedNoSocialAsset as e:
            return e.message

        except FailedWrongParam as e:
            return e.message

        except FailedNoRoute as e:
            return e.message

        except FailedInsufficientBattery as e:
            return e.message

        except FailedCapacity as e:
            return e.message

        except FailedInvalidKind as e:
            return e.message

        except FailedItemAmount as e:
            return e.message

        except FailedLocation as e:
            return e.message

        except FailedUnknownFacility as e:
            return e.message

        except FailedUnknownItem as e:
            return e.message

    def agent_delivery(self, agent, kind, item, amount=None):
        removed_items = []

        if amount is None:
            if kind == 'physical':
                removed_items = agent.remove_physical_item(item)

            elif kind == 'virtual':
                removed_items = agent.remove_virtual_item(item)

            else:
                raise FailedInvalidKind('Invalid item to deliver')

        else:

            if amount < 1:
                raise FailedItemAmount('The given amount is less than 1')

            if kind == 'physical':
                if amount > len(agent.physical_storage_vector):
                    raise FailedItemAmount('The given amount is greater than what the agent is carrying')

                removed_items = agent.remove_physical_item(item, amount)

            elif kind == 'virtual':
                if amount > len(agent.virtual_storage_vector):
                    raise FailedItemAmount('The given amount is greater than what the agent is carrying')

                removed_items = agent.remove_virtual_item(item, amount)

        if len(removed_items) == 0:
            raise FailedUnknownItem('No item by the given name is known.')

        if kind == 'physical':
            self.world.cdm.add_physical_items(removed_items, agent.token)

        else:
            self.world.cdm.add_virtual_items(removed_items, agent.token)

    def get_route(self, agent, location, list_of_nodes):
        if agent.role == 'drone' or agent.role == 'boat':
            agent.route, distance = self.router.get_route(agent.location, location, agent.role, int(agent.speed) / 2,
                                                          list_of_nodes)
            agent.destination_distance = distance
        else:
            start_node = self.router.get_closest_node(*agent.location)
            end_node = self.router.get_closest_node(*location)
            route_result, route = self.router.get_route(start_node, end_node, False, 4, list_of_nodes)

            if route_result == 'success':
                agent.route = route
            else:
                raise FailedNoRoute()

            agent.destination_distance = self.router.node_distance(start_node, end_node)

    def check_location(self, x, y):
        proximity = self.proximity

        if x[0] < y[0]:
            if x[0] + proximity >= y[0]:
                lat = True
            else:
                lat = False
        else:
            if x[0] - proximity <= y[0]:
                lat = True
            else:
                lat = False

        if x[1] < y[1]:
            if x[1] + proximity >= y[1]:
                lon = True
            else:
                lon = False
        else:
            if x[1] - proximity <= y[1]:
                lon = True
            else:
                lon = False

        return lat and lon
