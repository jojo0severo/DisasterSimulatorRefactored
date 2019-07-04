import os
import re
import json
import pathlib
from simulation_engine.copycat import CopyCat


class JsonFormatter:
    def __init__(self, config):
        config_location = pathlib.Path(__file__).parents[4] / config
        self.copycat = CopyCat(json.load(open(config_location, 'r')))

    def log(self):
        if not self.copycat.log():
            return {'status': 0, 'message': 'No more maps available for matches.'}
        else:
            return {'status': 1, 'message': 'New match generated.'}

    def regenerate(self):
        try:
            response = self.copycat.regenerate()
            json_agents = self.jsonify_agents(response[0])
            json_events = self.jsonify_events(response[1])

            return {'status': 1, 'agents': json_agents, 'event': json_events, 'message': 'Simulation restarted.'}

        except Exception as e:
            return {'status': 0, 'agents': [], 'event': {}, 'message': f'An error occurred during restart: "{str(e)}"'}

    def connect_agent(self, token):
        try:
            response = self.copycat.connect_agent(token)
            if response:
                return {'status': 1, 'message': 'Agent connected.'}

            else:
                return {'status': 0, 'message': 'Agent could not connect. No more roles available.'}

        except Exception as e:
            return {'status': 0, 'message': f'An error occurred during connection: {str(e)}.'}

    def disconnect_agent(self, token):
        try:
            response = self.copycat.disconnect_agent(token)

            if response:
                return {'status': 1, 'message': 'Agent disconnected.'}

            else:
                return {'status': 0, 'message': 'Agent already disconnected.'}

        except Exception as e:
            return {'status': 0, 'message': f'An error occurred during connection: {str(e)}.'}

    def start(self):
        try:
            response = self.copycat.start()
            json_agents = self.jsonify_agents(response[0])
            json_events = self.jsonify_events(response[1])

            return {'status': 1, 'agents': json_agents, 'event': json_events, 'message': 'Simulation started.'}

        except Exception as e:
            return {'status': 0, 'agents': [], 'event': {}, 'message': f'An error occurred during startup: "{str(e)}"'}

    def do_step(self, agent_action_list):
        try:
            response = self.copycat.do_step(agent_action_list)
            if response is None:
                return {'status': 1, 'agents': [], 'event': {}, 'message': 'Simulation finished.'}

            json_agents = self.jsonify_agents([obj['agent'] for obj in response[0]])
            messages = [obj['message'] for obj in response[0]]
            json_agents = [{'agent': ag, 'message': ms} for ag, ms in zip(json_agents, messages)]
            json_events = self.jsonify_events(response[1])

            return {'status': 1, 'agents': json_agents, 'event': json_events, 'message': 'Step completed.'}

        except Exception as e:
            return {'status': 0, 'agents': [], 'event': {}, 'message': f'An error occurred during step: "{str(e)}"'}

    def jsonify_agents(self, agents_list):
        json_agents = []
        for agent in agents_list:
            json_agents.append(self.jsonify_agent(agent))

        return json_agents

    def jsonify_agent(self, agent):
        json_physical_items = self.jsonify_delivered_items(agent.physical_storage_vector)

        json_virtual_items = self.jsonify_delivered_items(agent.virtual_storage_vector)

        json_social_assets = []
        for social_asset in agent.social_assets:
            json_social_asset = {
                'type': social_asset.type,
                'location': social_asset.location,
                'profession': social_asset.profession
            }
            json_social_assets.append(json_social_asset)

        json_route = [list(location) for location in agent.route]

        return {'token': agent.token,
                'active': agent.is_active,
                'last_action': agent.last_action,
                'last_action_result': agent.last_action_result,
                'role': agent.role,
                'location': list(agent.location),
                'route': json_route,
                'destination_distance': agent.destination_distance,
                'battery': agent.actual_battery,
                'max_charge': agent.max_charge,
                'speed': agent.speed,
                'physical_storage': agent.physical_storage,
                'physical_capacity': agent.physical_capacity,
                'physical_storage_vector': json_physical_items,
                'virtual_storage': agent.virtual_storage,
                'virtual_capacity': agent.virtual_capacity,
                'virtual_storage_vector': json_virtual_items,
                'social_assets': json_social_assets}

    @staticmethod
    def jsonify_events(events_list):
        if events_list['flood'] is None:
            return {'flood': '', 'victims': [], 'water_samples': [], 'photos': []}

        json_flood = {
            'identifier': events_list['flood'].identifier,
            'type': 'flood',
            'location': list(events_list['flood'].dimensions['location']),
            'shape': events_list['flood'].dimensions['shape']
        }

        if events_list['flood'].dimensions['shape'] == 'circle':
            json_flood['radius'] = events_list['flood'].dimensions['radius']

        json_victims = []
        for victim in events_list['victims']:
            json_victim = {
                'identifier': victim.identifier,
                'type': 'victim',
                'location': list(victim.location),
                'size': victim.size,
                'lifetime': victim.lifetime
            }
            json_victims.append(json_victim)

        json_water_samples = []
        for water_sample in events_list['water_samples']:
            json_water_sample = {
                'identifier': water_sample.identifier,
                'type': 'water_sample',
                'location': list(water_sample.location),
                'size': water_sample.size
            }
            json_water_samples.append(json_water_sample)

        json_photos = []
        for photo in events_list['photos']:
            json_photo_victims = []
            for victim in photo.victims:
                if victim.active:
                    json_victim = {
                        'identifier': victim.identifier,
                        'type': 'victim',
                        'location': list(victim.location),
                        'size': victim.size,
                        'lifetime': victim.lifetime
                    }
                    json_photo_victims.append(json_victim)

            json_photo = {
                'identifier': photo.identifier,
                'type': 'photo',
                'location': list(photo.location),
                'size': photo.size,
                'analyzed': photo.analyzed,
                'victims': json_photo_victims
            }

            json_photos.append(json_photo)

        return {'flood': json_flood, 'victims': json_victims, 'water_samples': json_water_samples, 'photos': json_photos}

    @staticmethod
    def jsonify_delivered_items(items):
        json_items = []
        for item in items:
            if item.type == 'victim':
                json_item = {
                    'identifier': item.identifier,
                    'type': 'victim',
                    'location': list(item.location),
                    'size': item.size,
                    'lifetime': item.lifetime
                }

            elif item.type == 'photo':
                json_photo_victims = []

                for victim in item.victims:
                    json_victim = {
                        'identifier': victim.identifier,
                        'type': 'victim',
                        'location': list(victim.location),
                        'size': victim.size,
                        'lifetime': victim.lifetime
                    }
                    json_photo_victims.append(json_victim)

                json_item = {
                    'identifier': item.identifier,
                    'type': 'photo',
                    'location': list(item.location),
                    'size': item.size,
                    'victims': json_photo_victims
                }

            elif item.type == 'water_sample':
                json_item = {
                    'identifier': item.identifier,
                    'type': 'water_sample',
                    'location': list(item.location),
                    'size': item.size
                }

            else:
                json_item = {
                    'identifier': item.identifier,
                    'type': 'Unknown'
                }

            json_items.append(json_item)

        return json_items

    @staticmethod
    def jsonify_action_token_by_step(action_token_by_step):
        json_action_token_by_step = []
        for step, action_token_list in action_token_by_step:
            json_token_action = []
            for action_token in action_token_list:
                json_token_action.append({'token': action_token[1], 'action': action_token[0]})

            json_action_token_by_step.append({'step': step, 'token_action': json_token_action})

        return json_action_token_by_step

    @staticmethod
    def jsonify_amount_of_actions_by_step(amount_of_actions_by_step):
        return [{'step': step, 'actions_amount': actions_amount} for step, actions_amount in amount_of_actions_by_step]

    @staticmethod
    def jsonify_actions_by_step(actions_by_step):
        return [{'step': step, 'actions': actions} for step, actions in actions_by_step]

    def save_logs(self):
        year, month, day, hour, minute, config_file, logs = self.copycat.get_logs()
        path = pathlib.Path(__file__).parents[4] / str(year) / str(month) / str(day) / str(config_file)

        os.makedirs(str(path.absolute()), exist_ok=True)

        hour = '{:0>2d}'.format(hour)
        minute = '{:0>2d}'.format(minute)

        for log in logs:
            json_items = self.jsonify_delivered_items(logs[log]['environment']['delivered_items'])
            json_agents = self.jsonify_agents(logs[log]['agents']['agents'])
            json_active_agents = self.jsonify_agents(logs[log]['agents']['active_agents'])
            json_action_token_by_step = self.jsonify_action_token_by_step(logs[log]['actions']['action_token_by_step'])
            json_acts_by_step = self.jsonify_amount_of_actions_by_step(logs[log]['actions']['amount_of_actions_by_step'])
            json_actions_by_step = self.jsonify_actions_by_step(logs[log]['actions']['actions_by_step'])

            logs[log]['environment']['delivered_items'] = json_items
            logs[log]['agents']['agents'] = json_agents
            logs[log]['agents']['active_agents'] = json_active_agents
            logs[log]['actions']['action_token_by_step'] = json_action_token_by_step
            logs[log]['actions']['amount_of_actions_by_step'] = json_acts_by_step
            logs[log]['actions']['actions_by_step'] = json_actions_by_step

            map_log = re.sub('([\w\s\d]+?\\\\)|([\w\s\d]+?/)|(\.\w+)', '', log)

            with open(str((path / f'LOG FILE {map_log} at {hour}h {minute}min.txt').absolute()), 'w') as file:
                file.write(json.dumps(logs[log], sort_keys=False, indent=4))
                file.write('\n\n' + '=' * 120 + '\n\n')
