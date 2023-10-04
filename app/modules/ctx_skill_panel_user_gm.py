import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds, ctx_skill_panel_user_gm_show
from app.modules.standart_modules import BackButton


class SkillPanel(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.SkillManagementEmbed(self.target)
        self.back_btn = BackButton(self, self.embed)

    @ui.button(label="Показать заклинания", style=discord.ButtonStyle.grey, row=1, emoji="🪬")
    async def showSkills(self, interaction: discord.Interaction, button: discord.Button):
        item = await ctx_skill_panel_user_gm_show.SkillSelector.create(target=self.target)
        item.back_btn = self.back_btn
        view = ui.View(timeout=None).add_item(item)
        view.add_item(self.back_btn)
        await interaction.response.edit_message(view=view)
