import discord, aiosqlite
from discord import ui
from app.database import db_queries as dq
from app.objects import User, Skill, Si
from app.utils import accessors


class SkillInitRankSelector(ui.Select):
    @classmethod
    async def create(cls, target: User):
        self = ui.Select(placeholder="Выберите ранг заклинания", min_values=1, max_values=1)
        self.target = target
        ranks = await dq.getAllRanks()
        [self.add_option(label=rank[1].capitalize(), value=rank[0]) for rank in ranks]

        async def _callback(interaction: discord.Interaction):
            option = int(self.values[0])
            skill = Si()
            skill.required_rank_id = option
            item = await ElementSelector.create(target=self.target, skill=skill)
            item.back_btn = self.back_btn
            view = ui.View(timeout=None).add_item(item)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view)

        self.callback = _callback
        return self


class ElementSelector(ui.Select):
    @classmethod
    async def create(cls, target: User, skill: Si, page=1):
        self = ui.Select(placeholder="Выберите элемент", min_values=1, max_values=1)
        options: list = []
        self.page = page
        self.target = target
        self.skill = skill
        if page == 1:
            options = (await dq.getAllElements())[:15]
        if page == 2:
            self.add_option(label="Вернуться назад", value="goback")
            options = (await dq.getAllElements())[15:]

        [self.add_option(label=f"{option[1].capitalize()}", value=option[0]) for option in options]
        if page == 1: self.add_option(label="Посмотреть больше", value="gonext")

        async def _callback(interaction: discord.Interaction) -> None:
            selected_value = self.values[0]
            if selected_value == "gonext":
                item = await ElementSelector.create(target=self.target, page=2, skill=self.skill)
                item.back_btn = self.back_btn
                view = ui.View(timeout=None).add_item(item)
                view.add_item(self.back_btn)
                await interaction.response.edit_message(view=view)
            elif selected_value == "goback":
                item = await ElementSelector.create(target=self.target, page=1, skill=self.skill)
                item.back_btn = self.back_btn
                view = ui.View(timeout=None).add_item(item)
                view.add_item(self.back_btn)
                await interaction.response.edit_message(view=view)
            else:
                element_id = int(selected_value)
                self.skill.element_id = element_id
                modal = SkillInitModal(target=self.target, skill=self.skill)
                modal.back_btn = self.back_btn
                await interaction.response.send_modal(modal)

        self.callback = _callback
        return self


class SkillInitModal(ui.Modal):
    def __init__(self, target: User, skill: Si):
        super().__init__(title="Создание заклинания")
        self.add_item(ui.TextInput(label="Название", max_length=50))
        self.add_item(ui.TextInput(label="Описание", max_length=1000, style=discord.TextStyle.long))
        self.add_item(ui.TextInput(label="Стоимость маны", max_length=4, default="4"))
        self.add_item(ui.TextInput(label="Цена прогресса", max_length=50, default="5"))
        self.target = target
        self.skill = skill

    async def on_submit(self, interaction: discord.Interaction) -> None:
        @accessors.log(self.target, "init_skill", f"Скилл инициирован")
        async def _callback(**kwargs) -> None:
            lines = self.children
            skill = self.skill
            skill.title = str(lines[0]).capitalize()
            skill.desc = str(lines[1])
            skill.manacost = int(str(lines[2]))
            skill.need_to_learn = int(str(lines[3]))
            skill.learn_progress = 0
            await skill.push(target=self.target)
            await interaction.response.edit_message(view=self.back_btn.getView(), embed=self.back_btn.getEmbed())
        await _callback(interaction=interaction)