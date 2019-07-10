import random
from collections import namedtuple
from simulation_engine.simulation_objects.social_asset import SocialAsset


Capacities = namedtuple('Capacities', 'abilities resources location profession size speed physical_capacity virtual_capacity')


class SocialAssetsManager:
    def __init__(self, map_info, social_assets_info):
        self.social_assets = {}
        random.seed(map_info['randomSeed'])
        self.capacities = self.generate_objects(map_info, social_assets_info)

    def restart(self, map_info, social_assets_info):
        tokens = list(self.social_assets.keys())
        self.social_assets.clear()
        self.capacities = self.generate_objects(map_info, social_assets_info)
        for token in tokens:
            self.connect_social_asset(token)

    @staticmethod
    def generate_objects(map_info, social_assets_info):
        min_lon = map_info['minLon']
        max_lon = map_info['maxLon']
        min_lat = map_info['minLat']
        max_lat = map_info['maxLat']

        capacities = []
        for profession in social_assets_info:
            location = random.uniform(min_lon, max_lon), random.uniform(min_lat, max_lat)
            size = random.randint(social_assets_info[profession]['minSize'], social_assets_info[profession]['maxSize'])
            speed = social_assets_info[profession]['speed']
            physical_capacity = social_assets_info[profession]['physicalCapacity']
            virtual_capacity = social_assets_info[profession]['virtualCapacity']
            abilities = social_assets_info[profession]['abilities']
            resources = social_assets_info[profession]['resources']

            temp_capacities = Capacities(abilities, resources, location,
                                         profession, size, speed, physical_capacity, virtual_capacity)

            for i in range(social_assets_info[profession]['amount']):
                capacities.append(temp_capacities)

        return capacities

    def connect_social_asset(self, token):
        if not self.capacities:
            return None

        asset_info = self.capacities.pop(0)
        self.social_assets[token] = SocialAsset(token, *asset_info)
        return self.social_assets[token]

    def disconnect_social_asset(self, token):
        if token not in self.social_assets:
            return False

        else:
            self.social_assets[token].disconnect()
            return True

    def add_physical(self, token, item):
        self.social_assets[token].add_physical_item(item)

    def add_virtual(self, token, item):
        self.social_assets[token].add_virtual_item(item)

    def add_social_asset(self, token, social_asset):
        self.social_assets[token].social_assets.append(social_asset)

    def get_social_asset(self, token):
        return self.social_assets.get(token)

    def get_tokens(self):
        return list(self.social_assets.keys())

    def get_social_assets_info(self):
        return list(self.social_assets.values())

    def deliver_physical(self, token, kind, amount=1):
        return self.social_assets[token].remove_physical_item(kind, amount)

    def deliver_virtual(self, token, kind, amount=1):
        return self.social_assets[token].remove_virtual_item(kind, amount)

    def edit_social_asset(self, token, attribute, new_value):
        exec(f'self.social_assets[token].{attribute} = new_value')

    def update_social_asset_location(self, token):
        if self.social_assets[token].route:
            location = self.social_assets[token].route.pop(0)
            self.social_assets[token].location = location

    def clear_social_asset_physical_storage(self, token):
        self.social_assets[token].clear_physical_storage()

    def clear_social_asset_virtual_storage(self, token):
        self.social_assets[token].clear_virtual_storage()
