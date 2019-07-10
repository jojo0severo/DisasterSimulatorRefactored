class WaterSample:

    def __init__(self, identifier: int, size: int, location: tuple):
        self.identifier: int = identifier
        self.active: bool = False
        self.type: str = 'water_sample'
        self.size: int = size
        self.location: tuple = location
