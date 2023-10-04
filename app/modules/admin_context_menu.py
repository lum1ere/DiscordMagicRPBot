import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds, ctx_skill_panel, ctx_permissions_panel, ctx_core_panel, ctx_timeline_panel, ctx_edit_mana
from app.modules import ctx_mutation_panel, ctx_changing_characters_block
from app.modules.standart_modules import BackButton
from app.utils import accessors
from app.modules.commands import log as lg


class AdminMenu(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.AdminMenuEmbed(target=target)
        self.back_btn = BackButton(self, self.embed)
        self.user = target

    @ui.button(label="Панель заклинанийㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.blurple, row=1, emoji="🪬")
    async def skillPanel(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(target=self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ctx_skill_panel.SkillPanel(target=self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_skills_a", f"{interaction.user.name} смотрит скиллы персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Панель привелегийㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, row=1, emoji="⚠️")
    async def permissionsPanel(self, interaction: discord.Interaction, button: discord.Button):
        self.target = await self.target.update()
        view = ui.View(timeout=None).add_item(
            await ctx_permissions_panel.PermissionsSelector.create(self.target, interaction.user.id, self, self.embed))
        view.add_item(self.back_btn)
        await interaction.response.edit_message(view=view)
        await lg(self.target, "show_permissions_a", f"{interaction.user.name} смотрит права игрока {self.target.name}!", interaction)

    @ui.button(label="Панель ядра   ㅤㅤㅤㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, row=2, emoji="🧿")
    async def corePanel(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(target=self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ctx_core_panel.CorePanel(self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_core_a", f"{interaction.user.name} смотрит ядро персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Панель таймлайна ㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, row=2, emoji="🕓")
    async def timeLinePanel(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(target=self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ctx_timeline_panel.TimelinePanelView(self.target)
            view.add_item(self.back_btn)
            view.embed = embeds.TimelineEmbed(self.target, await dq.getWorldTimeline())
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_timeline_a", f"{interaction.user.name} смотрит таймлайн персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Менеджер мутацийㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, row=3, emoji="🎇")
    async def mutationsPanel(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(target=self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            await interaction.response.send_modal(ctx_mutation_panel.MutationEditModal(self.target))
            await lg(self.target, "show_mutations_a", f"{interaction.user.name} смотрит мутации персонажа {self.target.active_character.webhook.name}!", interaction)


        await callback(interaction=interaction)

    @ui.button(label="Редактировать мануㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, row=3, emoji="🌀")
    async def editManaPanel(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(target=self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            await interaction.response.send_modal(ctx_edit_mana.EditManaModal(self.target))
            await lg(self.target, "show_manaedit_a", f"{interaction.user.name} смотрит меню редактирования маны персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Блокировка смены персонажаㅤ", style=discord.ButtonStyle.danger, row=4, emoji="⚠️")
    async def blockChangingCharPanel(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(target=self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = ctx_changing_characters_block.CharactersChangingBlockView(self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_switch_block_a", f"{interaction.user.name} смотрит блокировку смены персонажей игрока {self.target.name}!", interaction)


        await callback(interaction=interaction)

