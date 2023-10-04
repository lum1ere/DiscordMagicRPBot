import discord, aiosqlite
from discord import ui
from app.objects import User, Character, Profile
from app.database import db_queries as dq
from app.modules import embeds, user_context_menu
from app.utils import accessors
from app.modules.standart_modules import BackButton
from app.modules.reg import RegistrationModal
from app.modules.change_character import CharacterChangeSelector
from app.modules.ctx_stats_show import StatsView
from app.modules.ctx_skill_panel_user_gm_show import SkillSelector
from app.modules.inventory import ItemSelector
from app.modules.commands import log as lg
from app.modules.menu_profile_layer import ProfileLayer


class UserMenu(user_context_menu.UserMenu):
    def __init__(self, target: User):
        super().__init__(target)
        self.target = target
        self.embed = embeds.UserMenuEmbed(target=target) # !
        self.back_btn = BackButton(self, self.embed)

    @ui.button(label="Обновить анкетуㅤㅤㅤ", style=discord.ButtonStyle.grey, row=1, emoji="📝")
    async def updateProfile(self, interaction: discord.Interaction, btn):
        self.target = await self.target.update()
        @accessors.has_character
        @accessors.target_can_change_profile(self.target)
        async def callback(**kwargs):
            view = ProfileLayer(self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed(self.target))

        await callback(interaction=interaction)

    @ui.button(label="Посмотреть статистику", style=discord.ButtonStyle.grey, row=1, emoji="📜")
    async def showStats(self, interaction: discord.Interaction, btn):
        @accessors.has_character
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = StatsView(self.target, await dq.getWorldTimeline())
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_stats", f"{interaction.user.name} смотрит свои статы!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Заклинанияㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.success, row=3, emoji="🪬")
    async def castSkill(self, interaction: discord.Interaction, btn):
        @accessors.has_character
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ui.View(timeout=None).add_item(await SkillSelector.create(self.target))
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=embeds.SkillManagementEmbed(self.target))
            await lg(self.target, "show_skills", f"{interaction.user.name} смотрит свои заклинания!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Создать персонажаㅤ", style=discord.ButtonStyle.blurple, row=2, emoji="📋")
    async def createCharacter(self, interaction: discord.Interaction, btn):
        self.target = await self.target.update()
        @accessors.target_can_change_character(self.target)
        async def callback(**kwargs):
            modal = RegistrationModal()
            await interaction.response.send_modal(modal)

        await callback(interaction=interaction)

    @ui.button(label="Сменить персонажаㅤㅤ", style=discord.ButtonStyle.blurple, row=2, emoji="🔁")
    async def changeCharacter(self, interaction: discord.Interaction, btn):
        self.target = await self.target.update()
        @accessors.has_character
        @accessors.target_can_change_character(self.target)
        async def callback(interaction: discord.Interaction):
            item = await CharacterChangeSelector.create(self.target)
            item.back_view = UserMenu
            item.back_embed = embeds.UserMenuEmbed
            view = ui.View(timeout=None).add_item(item)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view)
            await lg(self.target, "change_character", f"{interaction.user.name} меняет персонажа!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Инвентарьㅤㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, row=3, emoji="📦")
    async def openInventory(self, interaction: discord.Interaction, btn):
        @accessors.has_character
        async def callback(**kwargs):
            item = ItemSelector(self.target, flag="nodelete")
            item.back_btn = self.back_btn
            view = ui.View(timeout=None).add_item(item)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=embeds.InventoryMenuEmbed(self.target))
            await lg(self.target, "show_invenroty", f"{interaction.user.name} смотрит свой инвентарь!", interaction)

        await callback(interaction=interaction)
