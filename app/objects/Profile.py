import aiosqlite
import app.database.db_queries as dq
from app.variables import get_db


class ProfileInterface:
    def __init__(self):
        self.short_desc: str = ""
        self.field_1: str = ""
        self.field_2: str = ""
        self.field_3: str = ""
        self.mutations: str = ""
        self.extra_1: str = ""
        self.extra_2: str = ""
        self.extra_3: str = ""
        self.extra_4: str = ""


class Profile(ProfileInterface):
    @classmethod
    async def create(cls, character_id):
        self = Profile()
        raw_data = await dq.everythingAboutProfileByCharacterId(character_id)
        self.short_desc = raw_data[1]
        self.field_1 = raw_data[2]
        self.field_2 = raw_data[3]
        self.field_3 = raw_data[4]
        self.mutations = raw_data[5]
        self.extra_1 = raw_data[6]
        self.extra_2 = raw_data[7]
        self.extra_3 = raw_data[8]
        self.extra_4 = raw_data[9]

        return self



