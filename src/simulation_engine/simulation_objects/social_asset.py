
class SocialAsset:
    def __init__(self, size: int, location: tuple, profession: str):
        self.type: str = 'social_asset'
        self.size: int = size
        self.active: bool = False
        self.location: tuple = location
        self.profession: str = profession
