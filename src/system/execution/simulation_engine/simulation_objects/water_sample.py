class WaterSample:

    def __init__(self, identifier: int, size: int, location: tuple):
        self.identifier: int = identifier
        self.type: str = 'water_sample'
        self.size: int = size
        self.location: tuple = location
        self.active: bool = False
