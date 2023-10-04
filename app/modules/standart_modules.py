import asyncio
import discord
from discord import ui
import app.database.db_queries as dq
from app.modules import embeds
from app.utils import accessors
from app.modules.commands import log


class BackButton(ui.Button):
    def __init__(self, menu_view: ui.View, menu_embed: discord.Embed):
        super().__init__(label="Вернуться в меню", style=discord.ButtonStyle.blurple, row=4, emoji="↩️")
        self.menu_view = menu_view
        self.menu_embed = menu_embed

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=self.menu_view, embed=self.menu_embed, content=None)

    def getView(self):
        return self.menu_view

    def getEmbed(self):
        return self.menu_embed


class CastButton(ui.Button):
    def __init__(self, skill, view):
        super().__init__(label="Каст заклинания", style=discord.ButtonStyle.success, row=2, emoji="🔮")
        self.skill = skill
        self.subview = view
        self.target = self.subview.target

    async def callback(self, interaction: discord.Interaction):
        self.target = await self.target.update()
        status = await dq.castSkill(self.target, self.skill)
        self.target = await self.target.update()
        embed = embeds.SkillSingleInfoGMUserEmbed(self.target, self.skill.id)
        embed.add_field(name=f"Статус каста: {status}", value="", inline=False)
        await interaction.response.edit_message(embed=embed)
        await interaction.channel.send(embed=embeds.SkillCasted(self.target, self.skill))
        self.disabled = False
        await log(self.target, "cast", f"Каст скилла {self.skill.title} персонажа {self.target.active_character.webhook.name} by {interaction.user.name}", interaction)
        await log(self.target, "multicast", f"{self.skill.title}", interaction)



