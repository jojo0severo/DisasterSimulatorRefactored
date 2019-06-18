class Photo:

    def __init__(self, size: int, victims: list, location: tuple):
        self.type: str = 'photo'
        self.size: int = size
        self.victims: list = victims
        self.location: tuple = location
        self.active: bool = False
