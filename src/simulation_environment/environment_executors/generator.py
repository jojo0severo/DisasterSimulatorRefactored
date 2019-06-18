import random
from simulation_environment.environment_variables.flood import Flood
from simulation_environment.environment_variables.photo import Photo
from simulation_environment.environment_variables.victim import Victim
from simulation_environment.environment_variables.water_sample import WaterSample
from simulation_environment.environment_variables.social_asset import SocialAsset


class Generator:
    def __init__(self, config, router):
        self.map_variables: dict = config['map']
        self.generate_variables: dict = config['generate']
        self.router = router
        random.seed(config['map']['randomSeed'])

    def generate_events(self) -> list:
        steps_number: int = self.map_variables['steps']
        events = [0] * steps_number

        flood = self.generate_flood()
        nodes: list = flood.list_of_nodes
        event: dict = {
            'flood': flood,
            'victims': self.generate_victims(nodes, False),
            'water_samples': self.generate_water_samples(nodes),
            'photos': self.generate_photos(nodes)
        }

        events[0] = event

        flood_probability: int = self.generate_variables['floodProbability']
        i: int = 1
        while i < steps_number:
            if random.randint(0, 100) <= flood_probability:
                event['flood'] = self.generate_flood()
                nodes: list = event['flood'].list_of_nodes
                event['victims']: list = self.generate_victims(nodes, False)
                event['water_samples']: list = self.generate_water_samples(nodes)
                event['photos']: list = self.generate_photos(nodes)

            events[i] = event
            i += 1

        return events

    def generate_flood(self) -> Flood:
        dimensions: dict = {'shape': 'circle' if random.randint(0, 0) == 0 else 'rectangle'}

        if dimensions['shape'] == 'circle':
            dimensions['radius'] = (
                random.uniform(self.generate_variables['flood']['circle']['minRadius'],
                               self.generate_variables['flood']['circle']['maxRadius'])
            )

        else:
            dimensions['height'] = (
                random.randint(self.generate_variables['flood']['rectangle']['minHeight'],
                               self.generate_variables['flood']['rectangle']['maxHeight'])
            )

            dimensions['length'] = (
                random.randint(self.generate_variables['flood']['rectangle']['minLength'],
                               self.generate_variables['flood']['rectangle']['maxLength'])
            )

        flood_lat: float = random.uniform(self.map_variables['minLat'], self.map_variables['maxLat'])
        flood_lon: float = random.uniform(self.map_variables['minLon'], self.map_variables['maxLon'])

        dimensions['location']: tuple = self.router.align_coords(flood_lat, flood_lon)

        if dimensions['shape'] == 'circle':
            list_of_nodes: list = self.router.nodes_in_radius(dimensions['location'], dimensions['radius'])

        else:
            if dimensions['height'] < dimensions['length']:
                list_of_nodes: list = self.router.nodes_in_radius(dimensions['location'], dimensions['height'])
            else:
                list_of_nodes: list = self.router.nodes_in_radius(dimensions['location'], dimensions['length'])

        period: int = random.randint(self.generate_variables['flood']['minPeriod'],
                                     self.generate_variables['flood']['maxPeriod'])

        return Flood(period, dimensions, list_of_nodes)

    def generate_photos(self, nodes: list) -> list:
        victim_probability: int = self.generate_variables['photo']['victimProbability']
        photo_size: int = self.generate_variables['photo']['size']

        amount: int = random.randint(self.generate_variables['photo']['minAmount'],
                                     self.generate_variables['photo']['maxAmount'])
        photos: list = [0] * amount
        i: int = 0
        while i < amount:
            photo_location: tuple = self.router.get_node_coord(random.choice(nodes))

            photo_victims: list = []
            if random.randint(0, 100) <= victim_probability:
                photo_victims = self.generate_victims(nodes, True)

            photos[i] = Photo(photo_size, photo_victims, photo_location)
            i += 1

        return photos

    def generate_victims(self, nodes: list, photo_call: bool) -> list:
        victim_min_size: int = self.generate_variables['victim']['minSize']
        victim_max_size: int = self.generate_variables['victim']['maxSize']

        victim_min_lifetime: int = self.generate_variables['victim']['minLifetime']
        victim_max_lifetime: int = self.generate_variables['victim']['maxLifetime']

        amount: int = random.randint(self.generate_variables['victim']['minAmount'],
                                     self.generate_variables['victim']['maxAmount'])
        victims: list = [0] * amount
        i: int = 0
        while i < amount:
            victim_size: int = random.randint(victim_min_size, victim_max_size)
            victim_lifetime: int = random.randint(victim_min_lifetime, victim_max_lifetime)
            victim_location: tuple = self.router.get_node_coord(random.choice(nodes))

            victims[i] = Victim(victim_size, victim_lifetime, victim_location, photo_call)
            i += 1

        return victims

    def generate_water_samples(self, nodes: list) -> list:
        water_sample_size: int = self.generate_variables['waterSample']['size']

        amount: int = random.randint(self.generate_variables['waterSample']['minAmount'],
                                     self.generate_variables['waterSample']['maxAmount'])
        water_samples: list = [0] * amount
        i: int = 0
        while i < amount:
            water_sample_location: tuple = self.router.get_node_coord(random.choice(nodes))
            water_samples[i] = WaterSample(water_sample_size, water_sample_location)
            i += 1

        return water_samples

    def generate_social_assets(self) -> list:
        min_lat: float = self.map_variables['minLat']
        max_lat: float = self.map_variables['maxLat']

        min_lon: float = self.map_variables['minLon']
        max_lon: float = self.map_variables['maxLon']

        asset_min_size: int = self.generate_variables['socialAsset']['minSize']
        asset_max_size: int = self.generate_variables['socialAsset']['maxSize']
        professions: list = self.generate_variables['socialAsset']['profession']

        amount: int = random.randint(self.generate_variables['socialAsset']['minAmount'],
                                     self.generate_variables['socialAsset']['maxAmount'])
        social_assets: list = [0] * amount
        i: int = 0
        while i < amount:
            asset_location: tuple = (random.uniform(min_lat, max_lat), random.uniform(min_lon, max_lon))

            social_asset_size: int = random.randint(asset_min_size, asset_max_size)
            occupation: str = random.choice(professions)

            social_assets[i] = SocialAsset(social_asset_size, asset_location, occupation)
            i += 1

        return social_assets
