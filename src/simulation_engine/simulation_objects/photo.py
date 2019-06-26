class Photo:

    def __init__(self, identifier: int, size: int, victims: list, location: tuple):
        self.identifier: int = identifier
        self.type: str = 'photo'
        self.size: int = size
        self.victims: list = victims
        self.location: tuple = location
        self.active: bool = False
