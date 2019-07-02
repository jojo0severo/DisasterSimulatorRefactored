import json


class Checker:
    def __init__(self, config_file):
        self.config = config_file

    def test_json_load(self):
        try:
            with open(self.config, 'r') as config:
                json.load(config)
            return 1, 'Load: Ok.'
        except json.JSONDecodeError:
            return 0, 'Error loading the file.'

    def test_main_keys(self):
        keys = ['map', 'agents', 'roles', 'generate']

        config = json.load(open(self.config, 'r'))
        for key in keys:
            if key not in config:
                return 0, f'General: {key} is missing.'

        for key in config:
            if key not in keys:
                return 0, f'General: Key {key} not in the allowed list of keys.'

            if not isinstance(config[key], dict):
                return 0, f'General: Key {key} is not a dict.'

        return 1, 'General: Ok.'

    def test_map_key(self):
        keys = ['id', 'steps', 'maps', 'minLon', 'maxLon', 'minLat', 'maxLat', 'centerLat', 'centerLon', 'proximity',
                'randomSeed']

        map = json.load(open(self.config, 'r'))['map']
        for key in keys:
            if key not in list(map.keys()):
                return 0, f'Map: {key} is missing.'

        for key in map:
            if key not in keys:
                return 0, f'Map: Key {key} is not in the list of allowed keys.'

        if not isinstance(map['id'], str) and not isinstance(map['id'], int):
            return 0, 'Map: ID is not a valid type.'

        if not isinstance(map['steps'], int):
            return 0, 'Map: Steps is not a valid type.'

        if map['steps'] <= 0:
            return 0, 'Map: Steps can not be zero or negative.'

        if not isinstance(map['maps'], list):
            return 0, 'Map: Maps is not a valid type.'

        if not map['maps']:
            return 0, 'Map: Maps is empty.'

        for key in ['minLat', 'minLon', 'maxLat', 'maxLon']:
            if not isinstance(map[key], float) and not isinstance(map[key], int):
                return 0, f'Map: Key {key} is not a valid type.'

        if map['minLon'] > map['maxLon']:
            return 0, f'Map: MinLon can not be bigger than MaxLon.'

        if map['minLat'] > map['maxLat']:
            return 0, f'Map: MinLat can not be bigger than MaxLat.'

        if not isinstance(map['centerLat'], float) and not isinstance(map['centerLat'], int):
            return 0, 'Map: CenterLat is not a valid type.'

        if map['minLat'] > map['centerLat'] or map['centerLat'] > map['maxLat']:
            return 0, 'Map: CenterLat can not be over the limits of minLat or maxLat.'

        if not isinstance(map['centerLon'], float) and not isinstance(map['centerLon'], int):
            return 0, 'Map: CenterLon is not a valid type.'

        if map['minLon'] > map['centerLon'] or map['centerLon'] > map['maxLon']:
            return 0, 'Map: CenterLon can not be over the limits of minLat or maxLat.'

        if not isinstance(map['proximity'], int):
            return 0, 'Map: Proximity is not a valid type.'

        if not isinstance(map['randomSeed'], str) and not isinstance(map['randomSeed'], int):
            return 0, 'Map: RandomSeed is not a valid type.'

        if map['proximity'] <= 0:
            return 0, 'Map: Proximity can not be zero or negative.'

        return 1, 'Map: Ok.'

    def test_agents_key(self):
        keys = ['drone', 'car', 'boat']

        agents = json.load(open(self.config, 'r'))['agents']

        for key in agents:
            if key not in keys:
                return 0, f'Agents: Key {key} not in the list of allowed keys.'

            if not isinstance(agents[key], int):
                return 0, f'Agents: {key.title()} is not a valid type.'

        return 1, 'Agents: Ok.'

    def test_roles_key(self):
        keys = ['drone', 'car', 'boat']
        sub_keys = ['speed', 'physicalCapacity', 'virtualCapacity', 'battery', 'kind']

        roles = json.load(open(self.config, 'r'))['roles']

        for key in roles:
            if key not in keys:
                return 0, f'Roles: Key {key} not in the list of allowed keys.'

            for sub_key in sub_keys:
                if sub_key not in roles[key]:
                    return 0, f'Roles: Sub key {sub_key} of {key} is missing.'

            for sub_key in roles[key]:
                if sub_key not in sub_keys:
                    return 0, f'Roles: Sub key {sub_key} of {key} is not in the list of allowed keys.'

        return 1, 'Roles: Ok.'

    def test_generate_key(self):
        keys = ['floodProbability', 'flood', 'photo', 'victim', 'waterSample', 'socialAsset']

        generate = json.load(open(self.config, 'r'))['generate']

        for key in keys:
            if key not in generate:
                return 0, f'Generate: {key} is missing.'

        for key in generate:
            if key not in keys:
                return 0, f'Generate: Key {key} is not in the list of allowed keys.'

        if not isinstance(generate['floodProbability'], int) and not isinstance(generate[key], float):
            return 0, 'Generate: FloodProbability is not a valid type.'

        if not isinstance(generate['flood'], dict):
            return 0, 'Generate: Flood is not a valid type.'

        test = self._test_flood_keys(generate['flood'])
        if not test[0]:
            return test

        if not isinstance(generate['photo'], dict):
            return 0, 'Generate: Photo is not a valid type.'

        test = self._test_photo_keys(generate['photo'])
        if not test[0]:
            return test

        if not isinstance(generate['victim'], dict):
            return 0, 'Generate: Victim is not a valid type.'

        test = self._test_victim_keys(generate['victim'])
        if not test[0]:
            return test

        if not isinstance(generate['waterSample'], dict):
            return 0, 'Generate: WaterSample is not a valid type.'

        test = self._test_water_sample_keys(generate['waterSample'])
        if not test[0]:
            return test

        if not isinstance(generate['socialAsset'], dict):
            return 0, 'Generate: SocialAsset is not a valid type.'

        test = self._test_social_asset_keys(generate['socialAsset'])
        if not test[0]:
            return test

        return 1, 'Generate: Ok.'

    @staticmethod
    def _test_flood_keys(flood):
        keys = ['minPeriod', 'maxPeriod', 'circle']
        sub_keys = ['minRadius', 'maxRadius']

        for key in keys:
            if key not in flood:
                return 0, f'Generate: Key {key} from Flood is missing.'

        for key in flood:
            if key not in keys:
                return 0, f'Generate: Key {key} from Flood is not in the list of allowed keys.'

        if not isinstance(flood['minPeriod'], int):
            return 0, 'Generate: MinPeriod from Flood is not a valid type.'

        if not isinstance(flood['maxPeriod'], int):
            return 0, 'Generate: MaxPeriod from Flood is not a valid type.'

        if flood['minPeriod'] > flood['maxPeriod']:
            return 0, 'Generate: MinPeriod from Flood can not be bigger than MaxPeriod from Flood.'

        if flood['minPeriod'] <= 0:
            return 0, 'Generate: MinPeriod from Flood can not be zero or negative.'

        if not isinstance(flood['circle'], dict):
            return 0, 'Generate: Circle from Flood is not a valid type.'

        for sub_key in sub_keys:
            if sub_key not in flood['circle']:
                return 0, f'Generate: Key {sub_key} from Flood is missing.'

        for sub_key in flood['circle']:
            if sub_key not in sub_keys:
                return 0, f'Generate: Key {sub_key} from Flood is not in the list of allowed subKeys.'

        if not isinstance(flood['circle']['minRadius'], float):
            return 0, 'Generate: MinRadius from Flood is not a valid type.'

        if not isinstance(flood['circle']['maxRadius'], float):
            return 0, 'Generate: MaxRadius from Flood is not a valid type.'

        if flood['circle']['minRadius'] > flood['circle']['maxRadius']:
            return 0, 'Generate: MinRadius from Flood can not be bigger than MaxRadius from Flood.'

        if flood['circle']['minRadius'] <= 0:
            return 0, 'Generate: MinRadius from Flood can not be zero or negative.'

        return 1, 'Generate: Ok from Flood.'

    @staticmethod
    def _test_photo_keys(photo):
        keys = ['size', 'minAmount', 'maxAmount', 'victimProbability']

        for key in keys:
            if key not in photo:
                return 0, f'Generate: Key {key} from Photo is missing.'

        for key in photo:
            if not isinstance(photo[key], int):
                return 0, f'Generate: Key {key} from Photo is not a valid type.'

            if key not in keys:
                return 0, f'Generate: Key {key} from Photo is not in the list of allowed keys.'

        if photo['minAmount'] > photo['maxAmount']:
            return 0, f'Generate: MinAmount from Photo can not be bigger than MaxAmount from Photo.'

        if photo['minAmount'] < 0:
            return 0, 'Generate: MinAmount can not be negative.'

        if photo['size'] <= 0:
            return 0, f'Generate: Size from Photo can not be zero or negative.'

        return 1, 'Generate: Ok from Photo.'

    @staticmethod
    def _test_victim_keys(victim):
        keys = ['minSize', 'maxSize', 'minAmount', 'maxAmount', 'minLifetime', 'maxLifetime']

        for key in keys:
            if key not in victim:
                return 0, f'Generate: Key {key} from Victim is missing.'

        for key in victim:
            if not isinstance(victim[key], int):
                return 0, f'Generate: Key {key} from Victim is not a valid type.'

            if key not in keys:
                return 0, f'Generate: Key {key} from Victim is not in the list of allowed keys.'

        if victim['minAmount'] > victim['maxAmount']:
            return 0, 'Generate: MinAmount from Victim can not be bigger than MaxAmount from Victim.'

        if victim['minAmount'] < 0:
            return 0, 'Generate: MinAmount from Victim can not be negative.'

        if victim['minSize'] > victim['maxSize']:
            return 0, 'Generate: MinSize from Victim can not be bigger than MaxSize from Victim.'

        if victim['minSize'] <= 0:
            return 0, 'Generate: MinSize from Victim can not be zero or negative.'

        if victim['minLifetime'] > victim['maxLifetime']:
            return 0, 'Generate: MinLifetime from Victim can not be bigger than MaxLifetime from Victim.'

        if victim['minLifetime'] <= 0:
            return 0, 'Generate: MinLifetime from Victim can not be zero or negative.'

        return 1, 'Generate: Ok from Victim.'

    @staticmethod
    def _test_water_sample_keys(water_sample):
        keys = ['size', 'minAmount', 'maxAmount']

        for key in keys:
            if key not in water_sample:
                return 0, f'Generate: Key {key} from WaterSample is missing.'

        for key in water_sample:
            if not isinstance(water_sample[key], int):
                return 0, f'Generate: Key {key} from WaterSample is not a valid type.'

            if key not in keys:
                return 0, f'Generate: Key {key} from WaterSample not in the list of allowed keys.'

        if water_sample['size'] <= 0:
            return 0, 'Generate: Size from WaterSample can not be zero or negative.'

        if water_sample['minAmount'] > water_sample['maxAmount']:
            return 0, 'Generate: MinAmount from WaterSample can not be bigger than MaxAmount from WaterSample.'

        if water_sample['minAmount'] < 0:
            return 0, 'Generate: MinAmount from WaterSample can not be negative.'

        return 1, 'Generate: Ok from WaterSample.'

    @staticmethod
    def _test_social_asset_keys(social_asset):
        keys = ['minAmount', 'maxAmount', 'minSize', 'maxSize', 'profession']

        for key in keys:
            if key not in social_asset:
                return 0, f'Generate: Key {key} from SocialAsset is missing.'

        for key in social_asset:
            if key != 'profession':
                if not isinstance(social_asset[key], int):
                    return 0, f'Generate: Key {key} from SocialAsset is not a valid type.'

            if key not in keys:
                return 0, f'Generate: Key {key} from SocialAsset not in the list of allowed keys.'

        if social_asset['minAmount'] > social_asset['maxAmount']:
            return 0, f'Generate: MinAmount from SocialAsset can not be bigger than MaxAmount from SocialAsset.'

        if social_asset['minAmount'] < 0:
            return 0, f'Generate: MinAmount from SocialAsset can not be negative.'

        if social_asset['minSize'] > social_asset['maxSize']:
            return 0, 'Generate: MinSize from SocialAsset can not be bigger than MaxSize from Victim.'

        if social_asset['minSize'] <= 0:
            return 0, 'Generate: MinSize from SocialAsset can not be zero or negative.'

        if not isinstance(social_asset['profession'], list):
            return 0, 'Generate: Profession from SocialAsset is not a valid type.'

        if not social_asset['profession']:
            return 0, 'Generate: Profession from SocialAsset can not be empty.'

        return 1, 'Generate: Ok from SocialAsset.'