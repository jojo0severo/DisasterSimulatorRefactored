class Photo:

    def __init__(self, size: int, victims: list, location: list):
        self.type: str = 'photo'
        self.size: int = size
        self.victims: list = victims
        self.location: list = location
        self.active: bool = False

    def json(self):
        victims = [victim.json() for victim in self.victims if victim.active]
        copy = self.__dict__.copy()
        copy['victims'] = victims
        del copy['active']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        return copy

    def json_file(self):
        copy = self.__dict__.copy()
        del copy['active']
        del copy['type']
        copy['victims'] = [victim.json_file() for victim in copy['victims']]
        return copy
