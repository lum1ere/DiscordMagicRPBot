import aiosqlite
from app.variables import get_db
import app.database.db_queries as dq
from app.objects.Core import Core
from app.objects.Profile import Profile
from app.objects.Skill import Skill
from app.objects.Item import Item
from app.objects.Webhook import Webhook


class CharacterInterface:
    def __init__(self):
        self.id: int = 0
        self.name: str = ""
        self.mana: int = 0
        self.manapool: int = 0
        self.rank_id: int = 0
        self.rank_name: str = ""
        self.progress_current: int = 0
        self.progress_need: int = 0
        self.timeline: str = ""
        self.can_edit_profile: str = ""
        self.money: float = 0.0
        self.core: Core = Core()
        self.profile: Profile = Profile()
        self.skills: list[Skill] = []
        self.castable_skills: list[Skill] = []
        self.inventory: list[Item] = []
        self.webhook: Webhook = Webhook()

    async def push(self, user_id):
        await dq.regCharacter(user_id, self)


class Character(CharacterInterface):
    @classmethod
    async def create(cls, character_id):
        self = Character()
        self.id = character_id
        raw_data = await dq.everythingAboutCharacterByCharacterId(self.id)
        self.name = raw_data[0]
        self.mana = raw_data[1]
        self.manapool = raw_data[2]
        self.rank_id = raw_data[3]
        self.rank_name = raw_data[4]
        self.progress_current = raw_data[5]
        self.progress_need = raw_data[6]
        self.timeline = raw_data[7]
        self.can_edit_profile = raw_data[8]
        self.money = raw_data[9]

        self.core = await Core.create(core_id=character_id)
        self.profile = await Profile.create(character_id=character_id)

        skill_ids = await dq.allSkillsIdOfCharacter(self)
        if skill_ids:
            self.skills = [await Skill.create(skill) for skill in skill_ids]
        for skill in self.skills:
            if dq.canCast(self, skill) == "Да":
                skill.can_cast = True
                self.castable_skills.append(skill)

        items = await dq.getItemsOfCharacter(self)
        if items:
            [self.inventory.append(Item(item)) for item in items]

        self.webhook = await Webhook.create(character_id)

        return self



    async def changeMana(self, value: float) -> None:
        await dq.changeMana(character=self, value=value)

    async def update(self):
        return await Character.create(character_id=self.id)

    async def profileCommit(self, args) -> None:
        await dq.changeProfileOfCharacter(self, args)

    async def profileExtraCommit(self, args) -> None:
        await dq.changeExtraProfileOfCharacter(self, args)
