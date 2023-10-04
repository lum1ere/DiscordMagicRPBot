

class ItemInterface:
    def __init__(self):
        self.id: int = 0
        self.name: str = ""
        self.desc: str = ""

    async def push(self, character):
        pass


class Item:
    def __init__(self, raw_data):
        self.id: int = raw_data[0]
        self.name: str = raw_data[1]
        self.desc: str = raw_data[2]
