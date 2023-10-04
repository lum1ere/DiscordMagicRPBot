import discord, aiosqlite
from discord import ui
from app.objects import User, Character, Profile
from app.database import db_queries as dq
from app.modules import embeds, ctx_skill_panel_initiate, ctx_skill_panel_show_admin
from app.modules.standart_modules import BackButton
from app.utils import accessors
from app.modules.commands import log


class SkillPanel(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.SkillManagementEmbed(self.target)
        self.back_btn = BackButton(self, self.embed)

    @ui.button(label="Показать заклинанияㅤㅤㅤ", style=discord.ButtonStyle.grey, row=1, emoji="🪬")
    async def showSkills(self, interaction: discord.Interaction, button: discord.Button):
        item = await ctx_skill_panel_show_admin.SkillSelector.create(target=self.target)
        item.back_btn = self.back_btn
        view = ui.View(timeout=None).add_item(item)
        view.add_item(self.back_btn)
        await interaction.response.edit_message(view=view)
        await log(self.target, "show_skill", f"Запущена показ скиллов админом", interaction)

    @ui.button(label="Инициировать заклинание", style=discord.ButtonStyle.grey, row=1, emoji="🌀")
    async def initiateSkill(self, interaction: discord.Interaction, button: discord.Button):
        item = await ctx_skill_panel_initiate.SkillInitRankSelector.create(target=self.target)
        item.back_btn = self.back_btn
        view = ui.View().add_item(item)
        view.add_item(self.back_btn)
        await interaction.response.edit_message(view=view, embed=None)
        await log(self.target, "init_skill", f"Запущена инициировка скила", interaction)

