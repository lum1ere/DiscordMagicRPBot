import discord, aiosqlite
from discord import ui
from app.objects import User, Character, Profile
from app.database import db_queries as dq
from app.modules import embeds, ctx_skill_panel_initiate, ctx_skill_panel_show_admin
from app.utils import accessors
from app.modules.commands import log


class CorePanel(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.CoreProgressEmbed(target)

    @ui.button(label="Добавить +1 к прогрессу", emoji="➕", style=discord.ButtonStyle.blurple)
    async def add_progress(self, interaction: discord.Interaction, btn):
        await dq.addProgressPoint(target=self.target)
        self.target = await self.target.update()
        await interaction.response.edit_message(embed=self.embed.update(self.target))
        await log(self.target, "add_core_progress", f"Ядро {self.target.active_character.progress_current}/{self.target.active_character.progress_need}", interaction)
