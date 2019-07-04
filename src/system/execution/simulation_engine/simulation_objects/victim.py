class Victim:

    def __init__(self, identifier: int, size: int, lifetime: int, location: tuple, photo: bool):
        self.identifier: int = identifier
        self.type: str = 'victim'
        self.size: int = size
        self.lifetime: int = lifetime
        self.active: bool = False
        self.in_photo: bool = photo
        self.location: tuple = location

