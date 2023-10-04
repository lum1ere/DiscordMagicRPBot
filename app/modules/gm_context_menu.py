import discord, aiosqlite
from discord import ui
from app.objects import User, Character, Profile
from app.database import db_queries as dq
from app.modules import embeds, ctx_profile_block, ctx_stats_show, ctx_skill_panel_user_gm, inventory, ctx_grant_money
from app.utils import accessors
from app.modules.standart_modules import BackButton
from app.modules.commands import log as lg


class GmMenu(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.GMMenuEmbed(target=target)
        self.back_btn = BackButton(menu_view=self, menu_embed=self.embed)
        self.back_btn.label = "Назад"

    @ui.button(label="Статистика", style=discord.ButtonStyle.grey, emoji="📜")
    async def showShort(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ctx_stats_show.StatsView(self.target, await dq.getWorldTimeline())
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_stats", f"{interaction.user.name} смотрит статы персонажа {self.target.active_character.webhook.name}!", interaction)
        await callback(interaction=interaction)

    @ui.button(label="Заклинания", style=discord.ButtonStyle.grey, emoji="🪬")
    async def showSkills(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ctx_skill_panel_user_gm.SkillPanel(self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_spells", f"{interaction.user.name} смотрит заклинания персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Блокировка изменения анкетыㅤ", style=discord.ButtonStyle.danger, row=1, emoji="⚠️")
    async def blockProfileChanging(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ctx_profile_block.ProfileChangingBlockView(self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(
                view=view,
                embed=view.embed
            )
            await lg(self.target, "switch_p_block", f"{interaction.user.name} сменил статус блокировки персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Редактировать инвентарьㅤㅤㅤ", style=discord.ButtonStyle.grey, row=2, emoji="📦")
    async def editInventory(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = inventory.InventoryView(self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_items", f"{interaction.user.name} смотрит инвентарь персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)




