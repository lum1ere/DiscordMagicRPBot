import aiosqlite

import app.database.db_queries
from app.variables import get_db
import app.database.db_queries as dq
from app.objects.Character import Character


class UserInterface:
    def __init__(self):
        self.id: int = 0
        self.name: str = ""
        self.can_change: str = ""
        self.active_character: Character = Character()


class User(UserInterface):
    @classmethod
    async def create(cls, user_id, flag=""):
        self = User()
        self.id = user_id
        self.name = await dq.getNameById(user_id)
        self.can_change = await dq.canChange(user_id)
        if await app.database.db_queries.hasCharacter(user_id):
            active_character_id = await dq.currentCharacterIdOfUser(user_id)
            self.active_character = await Character.create(character_id=active_character_id)
        return self

    async def changeCharacter(self, character_id: int):
        self.active_character = await Character.create(character_id=character_id)

    async def update(self):
        return await User.create(user_id=self.id)