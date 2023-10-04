import aiosqlite
import app.database.db_queries as dq
from app.variables import get_db


class AffinityInterface:
    def __init__(self):
        self.affinity_element_id: int = 0
        self.affinity_element_name: str = ""
        self.affinity_level_name: str = ""
        self.affinity_level_value: int = 0


class Affinity(AffinityInterface):
    @classmethod
    async def create(cls, raw_data):
        self = Affinity()
        self.affinity_element_id = raw_data[0]
        self.affinity_element_name = raw_data[1]
        self.affinity_level_name = raw_data[2]
        affinity_weight = {
            'Высший': 1,
            'Высокий': 0,
            'Средний': -1,
        }
        self.affinity_level_value = affinity_weight[self.affinity_level_name]
        return self
