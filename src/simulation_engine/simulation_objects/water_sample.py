class WaterSample:

    def __init__(self, size: int, location: tuple):
        self.type: str = 'water_sample'
        self.size: int = size
        self.location: tuple = location
        self.active: bool = False
