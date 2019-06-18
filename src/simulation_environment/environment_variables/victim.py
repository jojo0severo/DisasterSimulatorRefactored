class Victim:

    def __init__(self, size: int, lifetime: int, location: tuple, photo: bool):
        self.type: str = 'victim'
        self.size: int = size
        self.lifetime: int = lifetime
        self.active: bool = False
        self.in_photo: bool = photo
        self.location: tuple = location

