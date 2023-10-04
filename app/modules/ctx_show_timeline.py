import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds


class TimeLineView(ui.View):
    @classmethod
    async def create(cls, target: User):
        self = ui.View(timeout=None)
        self.target = target
        self.embed = await embeds.TimeLineShowEmbed.create(target=target)

        return self
