import json
from src.simulation_engine.copycat import CopyCat


class JsonFormatter:
    def __init__(self, config):
        self.copycat = CopyCat(json.load(open(config, 'r')))

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
                return {'status': 0, 'agents': [], 'event': {}, 'message': 'Simulation finished.'}

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

    @staticmethod
    def jsonify_agent(agent):
        json_physical_items = [item.__dict__ for item in agent.physical_storage_vector]

        json_virtual_items = [item.__dict__ for item in agent.virtual_storage_vector]

        json_social_assets = [social_asset.__dict__ for social_asset in agent.social_assets]

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
            'type': 'flood',
            'location': list(events_list['flood'].dimensions['location']),
            'shape': events_list['flood'].dimensions['shape']
        }

        if events_list['flood'].dimensions['shape'] == 'circle':
            json_flood['radius'] = events_list['flood'].dimensions['radius']

        json_victims = []
        for victim in events_list['victims']:
            json_victim = {
                'type': 'victim',
                'location': list(victim.location),
                'size': victim.size,
                'lifetime': victim.lifetime
            }
            json_victims.append(json_victim)

        json_water_samples = []
        for water_sample in events_list['water_samples']:
            json_water_sample = {
                'type': 'water_sample',
                'location': list(water_sample.location),
                'size': water_sample.size
            }
            json_water_samples.append(json_water_sample)

        json_photos = []
        for photo in events_list['photos']:
            json_photo_victims = []
            for victim in photo.victims:
                json_victim = {
                    'type': 'victim',
                    'location': list(victim.location),
                    'size': victim.size,
                    'lifetime': victim.lifetime
                }
                json_photo_victims.append(json_victim)

            json_photo = {
                'type': 'photo',
                'location': list(photo.location),
                'size': photo.size,
                'victims': json_photo_victims
            }

            json_photos.append(json_photo)

        return {'flood': json_flood, 'victims': json_victims, 'water_samples': json_water_samples, 'photos': json_photos}
