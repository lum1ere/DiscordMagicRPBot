import app.database.db_queries as dq


class SkillInterface:
    def __init__(self):
        self.id: int = 0
        self.title: str = ""
        self.manacost: int = 0
        self.need_to_learn: int = 0
        self.element_id: int = 0
        self.desc: str = ""
        self.required_rank_id: int = 0
        self.learn_progress: int = 0
        self.learned: str = ""
        self.required_rank_name: str = ""
        self.element_name: str = ""
        self.can_cast: bool = False

    async def push(self, target):
        await dq.initSkill(skill=self, target=target)


class Skill(SkillInterface):
    @classmethod
    async def create(cls, skill_id):
        self = Skill()
        self.id = skill_id
        raw_data = await dq.everythingAboutSkillFromSkillId(skill_id)
        self.title = raw_data[1]
        self.manacost = raw_data[2]
        self.need_to_learn = raw_data[3]
        self.element_id = raw_data[4]
        self.desc = raw_data[5]
        self.required_rank_id = raw_data[6]
        self.learn_progress = raw_data[7]
        self.learned = raw_data[8]
        self.required_rank_name = raw_data[9]
        self.element_name = raw_data[10]

        return self
