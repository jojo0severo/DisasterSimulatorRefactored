
class SocialAsset:
    def __init__(self, identifier: int, size: int, location: tuple, profession: str):
        self.identifier: int = identifier
        self.type: str = 'social_asset'
        self.size: int = size
        self.active: bool = False
        self.location: tuple = location
        self.profession: str = profession
