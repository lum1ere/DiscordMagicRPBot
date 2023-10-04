import aiosqlite
import app.database.db_queries as dq
from app.variables import get_db
from app.objects.Affinity import Affinity


class CoreInterface:
    def __init__(self):
        self.id: int = 0
        self.affinities: list = []
        self.core_type: str = ""


class Core(CoreInterface):

    @classmethod
    async def create(cls, core_id):
        self = Core()
        self.id = core_id
        raw_data = await dq.everythingAboutCoreFromCoreId(core_id)
        self.affinities = [await Affinity.create(statement) for statement in raw_data]
        async with aiosqlite.connect(get_db()) as connection:
            async with connection.execute(f"SELECT type from core_types WHERE core_id = {self.id}") as cursor:
                core_type = (await cursor.fetchall())
                if not core_type:
                    self.core_type = None
                else:
                    self.core_type = core_type[0][0]
        return self

    async def addAffinity(self, element_id, level):
        await dq.addAffinity(self, element_id, level)

    async def update(self):
        return await Core.create(core_id=self.id)