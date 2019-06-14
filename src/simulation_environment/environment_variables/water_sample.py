class WaterSample:

    def __init__(self, size: int, location: list):
        self.type: str = 'water_sample'
        self.size: int = size
        self.location: list = location
        self.active: bool = False

    def json(self):
        copy = self.__dict__.copy()
        del copy['active']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        return copy

    def json_file(self):
        copy = self.__dict__.copy()
        del copy['active']
        del copy['type']
        return copy
