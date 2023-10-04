import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds
from app.modules.commands import log


class TimelinePanelView(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target

    @ui.button(label="Редактироватьㅤㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, row=0, emoji="📝")
    async def edit(self, interaction: discord.Interaction, button: ui.Button):
        self.target = await self.target.update()
        await interaction.response.send_modal(TimelineEditModal(self.target, self.embed))
        self.target = await self.target.update()
        await log(self.target, "edit_timeline", f"Админ {interaction.user.name} поменял таймлайн {self.target.active_character.name} на {self.target.active_character.timeline}", interaction)


    @ui.button(label="Синхронизировать с общим", style=discord.ButtonStyle.grey, row=0, emoji="🕓")
    async def sync(self, interaction: discord.Interaction, button: ui.Button):
        await dq.changeTimeline(self.target, await dq.getWorldTimeline())
        self.target = await self.target.update()
        await interaction.response.edit_message(embed=await self.embed.update(self.target))
        await log(self.target, "sync_timeline", f"Админ {interaction.user.name} синхронизировал таймлайн {self.target.active_character.name} с общим", interaction)

    @ui.button(label="Редактировать Общийㅤㅤㅤ", style=discord.ButtonStyle.success, row=1, emoji="⏱️")
    async def setWorldTimeline(self, interaction: discord.Interaction, button: ui.Button):
        self.target = await self.target.update()
        await interaction.response.send_modal(WorldTimelineEditModal(self.target, self.embed, await dq.getWorldTimeline()))
        await log(self.target, "edit_world_timeline", f"Админ {interaction.user.name} поменял общий таймлайн.", interaction)


class TimelineEditModal(ui.Modal):
    def __init__(self, target: User, embed: embeds.TimelineEmbed):
        super().__init__(title="Редактирование таймлайна")
        self.target = target
        self.embed = embed
        timeline = target.active_character.timeline
        components = timeline.split(" ")
        days = components[0][:-1]
        hours = components[1].split(":")[0]
        self.add_item(ui.TextInput(label="Дни", required=True, default=days, max_length=2))
        self.add_item(ui.TextInput(label="Часы", required=True, default=hours))

    async def on_submit(self, interaction: discord.Interaction):
        days = str(self.children[0])
        hours = str(self.children[1])
        timeline = f"{days}d {hours}:00:00"
        await dq.changeTimeline(self.target, timeline)
        await interaction.response.edit_message(embed=await self.embed.update(self.target))


class WorldTimelineEditModal(ui.Modal):
    def __init__(self, target: User, embed: embeds.TimelineEmbed, world_timeline: str):
        super().__init__(title="Редактирование таймлайна")
        self.target = target
        self.embed = embed
        timeline = world_timeline
        components = timeline.split(" ")
        days = components[0][:-1]
        hours = components[1].split(":")[0]
        self.add_item(ui.TextInput(label="Дни", required=True, default=days, max_length=2))
        self.add_item(ui.TextInput(label="Часы", required=True, default=hours))

    async def on_submit(self, interaction: discord.Interaction):
        days = str(self.children[0])
        hours = str(self.children[1])
        timeline = f"{days}d {hours}:00:00"
        await dq.setWorldTimeline(timeline)
        await interaction.response.edit_message(embed=await self.embed.update(self.target))
