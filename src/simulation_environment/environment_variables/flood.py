class Flood:

    def __init__(self, period: int, dimensions: dict, list_of_nodes: list):
        self.type: str = 'flood'
        self.active: bool = False
        self.period: int = period
        self.dimensions: dict = dimensions
        self.list_of_nodes: list = list_of_nodes

    def json(self):
        copy = self.__dict__.copy()
        del copy['list_of_nodes']
        del copy['period']
        del copy['active']
        lat = copy['dimensions']['location'][0]
        lon = copy['dimensions']['location'][1]
        copy['dimensions']['location'] = {'lat': lat, 'lon': lon}
        return copy

    def json_file(self, locations):
        copy = self.__dict__.copy()
        del copy['active']
        del copy['type']
        copy['list_of_nodes'] = locations
        return copy

