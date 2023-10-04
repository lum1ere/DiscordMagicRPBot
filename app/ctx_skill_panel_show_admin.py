import asyncio

import discord, aiosqlite
from discord import ui
from app.database import db_queries as dq
from app.modules import embeds, standart_modules
from app.objects import User, Skill, Character
from math import ceil
from app.utils import accessors
from app.modules.commands import log


class SkillSelector(ui.Select):
    @classmethod
    async def create(cls, target: User):
        target = await target.update()
        self = ui.Select(placeholder="Выберите заклинание", max_values=1, min_values=1, row=1)
        self.page = 1

        self.embed = embeds.SkillManagementEmbed(target)
        self.embed_multiple = embeds.SkillMultipleInfoAdminEmbed
        self.embed_single = embeds.SkillSingleInfoAdminEmbed

        self.target = target
        self.skills = target.active_character.skills
        self.back_btn = standart_modules.BackButton(self.view, self.embed)

        self.max_pages = ceil(len(self.skills) / 3)
        self.add_option(label="Вывести всё", value="_all", emoji="🔁")
        [self.add_option(
            label=skill.title.capitalize(),
            description=skill.desc.capitalize()[:99],
            value=skill.id, emoji="☄️") for skill in self.skills]

        async def _callback(interaction: discord.Interaction):
            option = self.values[0]
            if option == "_all":

                await interaction.response.edit_message(
                    embed=self.embed_multiple(self.target, page=self.page), view=await regen(None, flag="extra"))

            elif option == "nextpage":

                if self.page != self.max_pages:
                    self.page += 1
                await interaction.response.edit_message(embed=self.embed_multiple(self.target, page=self.page))

            elif option == "backpage":

                if self.page != 1:
                    self.page -= 1
                await interaction.response.edit_message(embed=self.embed_multiple(self.target, page=self.page))

            elif option == "return":

                await interaction.response.edit_message(embed=embeds.SkillManagementEmbed(self.target), view=await regen(None, ""))

            else:

                option = int(option)
                _skill = 0
                for skill in self.skills:
                    if skill.id == option:
                        _skill = skill

                view = await regen(_skill, "cast delete progress")
                await interaction.response.edit_message(embed=self.embed_single(self.target, option), view=view)

        self.callback = _callback

        async def regen(_skill, flag=""):
            view = ui.View(timeout=None)
            item = await SkillSelector.create(self.target)
            item.back_btn = self.back_btn
            if _skill is not None:
                item.placeholder = _skill.title
            else:
                item.placeholder = "Все скиллы"

            if "cast" in flag:
                cast_button = CastButton(_skill, self)
                if not _skill.can_cast:
                    cast_button.disabled = True
                else:
                    cast_button.disabled = False
                view.add_item(cast_button)

            if "delete" in flag:
                view.add_item(DeleteSkill(_skill, self.target))

            if "extra" in flag:
                item.options.clear()
                item.add_option(label="Следующая страница", value="nextpage", emoji="➡️")
                item.add_option(label="Предыдущая страница", value="backpage", emoji="⬅️")
                item.add_option(label="Назад", value="return", emoji="↩️")

            if "progress" in flag:
                pb = AddProgress(_skill, self.target)
                if _skill.learned == "Да":
                    pb.disabled = True
                view.add_item(pb)

            view.add_item(item)
            view.add_item(self.back_btn)

            return view

        self.regen = regen
        return self


class DeleteSkill(ui.Button):
    def __init__(self, skill, target):
        super().__init__(label="Удалить заклинаниеㅤㅤ", style=discord.ButtonStyle.danger, row=2, emoji="⚠️")
        self.skill = skill
        self.target = target
        self.pressed = 0

    async def callback(self, interaction: discord.Interaction):
        self.pressed += 1
        if self.pressed == 1:
            await interaction.response.send_message(ephemeral=True, embed=embeds.AreYouSure(self.target))
            await asyncio.sleep(5)
            self.pressed = 0
        if self.pressed == 2:
            self.target = await self.target.update()
            await dq.dropSkill(self.target, self.skill)
            self.target = await self.target.update()
            view = ui.View(timeout=None).add_item(await SkillSelector.create(self.target))
            await interaction.response.edit_message(embed=embeds.SkillManagementEmbed(self.target), view=view)
            await log(self.target, "skill_delete", f"Удаление скилла {self.skill.title}", interaction)


class CastButton(ui.Button):
    def __init__(self, skill, view):
        super().__init__(label="Каст заклинанияㅤㅤㅤㅤ", style=discord.ButtonStyle.success, row=2, emoji="🔮")
        self.skill = skill
        self.subview = view
        self.target = self.subview.target

    async def callback(self, interaction: discord.Interaction):
        self.target = await self.target.update()
        status = await dq.castSkill(self.target, self.skill)
        self.target = await self.target.update()
        embed = embeds.SkillSingleInfoAdminEmbed(self.target, self.skill.id)
        embed.add_field(name=f"Мана: {self.target.active_character.mana} / {self.target.active_character.manapool}", value="")
        embed.add_field(name=f"Статус каста: {status}", value="", inline=False)
        await interaction.response.edit_message(embed=embed)
        await interaction.channel.send(embed=embeds.SkillCasted(self.target, self.skill))
        await log(self.target, "cast_admin", f"Каст скилла {self.skill.title} от админа {interaction.user.name}", interaction)
        await log(self.target, "multicast", f"{self.skill.title}", interaction)


class AddProgress(ui.Button):
    def __init__(self, skill, target):
        super().__init__(label="Добавить очко прогресса", style=discord.ButtonStyle.blurple, row=3, emoji="➕")
        self.skill = skill
        self.target = target

    async def callback(self, interaction: discord.Interaction):
        self.target = await self.target.update()
        await dq.addSkillPoint(self.target, self.skill)
        self.target = await self.target.update()
        embed = embeds.SkillSingleInfoAdminEmbed(self.target, self.skill.id)
        if self.skill.learned == "Да":
            view = await SkillSelector.create(self.target)
            view = await view.regen(self.skill, "cast delete progress")

            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.edit_message(embed=embed)
        await log(self.target, "add_skill_progress", f"Админ {interaction.user.name} добавил очко прогресса к скиллу {self.skill.title}. Текущий прогресс {self.skill.learn_progress}/{self.skill.need_to_learn}", interaction)
