class Victim:

    def __init__(self, size: int, lifetime: int, location: list, photo: bool):
        self.type: str = 'victim'
        self.size: int = size
        self.lifetime: int = lifetime
        self.active: bool = False
        self.in_photo: bool = photo
        self.location: list = location

    def __eq__(self, other):
        return self.size == other['size'] and self.location == other['location'] and self.lifetime == other['lifetime']

    def json(self):
        copy = self.__dict__.copy()
        del copy['active']
        del copy['in_photo']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        return copy

    def json_file(self):
        copy = self.__dict__.copy()
        del copy['type']
        return copy
