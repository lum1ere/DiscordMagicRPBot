import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds


class StatsView(ui.View):
    def __init__(self, target: User, current_timeline: str):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.TimelineEmbed(target, current_timeline)
