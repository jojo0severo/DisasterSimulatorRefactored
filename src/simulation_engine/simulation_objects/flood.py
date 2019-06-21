class Flood:

    def __init__(self, period: int, dimensions: dict, list_of_nodes: list):
        self.type: str = 'flood'
        self.active: bool = False
        self.period: int = period
        self.dimensions: dict = dimensions
        self.list_of_nodes: list = list_of_nodes

