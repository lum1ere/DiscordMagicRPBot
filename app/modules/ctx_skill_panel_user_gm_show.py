import discord, aiosqlite
from discord import ui
from app.database import db_queries as dq
from app.modules import embeds
from app.modules.standart_modules import CastButton, BackButton
from app.objects import User, Skill, Character
from math import ceil
from app.modules.commands import log


# noinspection DuplicatedCode
class SkillSelector(ui.Select):
    @classmethod
    async def create(cls, target: User):
        target = await target.update()
        self = ui.Select(placeholder="Выберите заклинание", max_values=1, min_values=1, row=1)
        self.embed = embeds.SkillManagementEmbed(target)
        self.page = 1
        self.back_btn = BackButton(menu_view=self.view, menu_embed=self.embed)
        self.target = target
        self.skills = target.active_character.castable_skills
        self.max_pages = ceil(len(self.skills) / 3)
        self.add_option(label="Вывести всё", value="_all", emoji="🔁")
        [self.add_option(
            label=skill.title.capitalize(),
            description=skill.desc.capitalize()[:95],
            value=skill.id, emoji="☄️") for skill in self.skills]

        async def _callback(interaction: discord.Interaction):
            option = self.values[0]
            if option == "_all":
                await interaction.response.edit_message(embed=embeds.SkillMultipleInfoGMUserEmbed(self.target, page=self.page), view=await regen(None, "extra"))
            elif option == "nextpage":
                if self.page != self.max_pages:
                    self.page += 1
                await interaction.response.edit_message(embed=embeds.SkillMultipleInfoGMUserEmbed(self.target, page=self.page))
            elif option == "backpage":
                if self.page != 1:
                    self.page -= 1
                await interaction.response.edit_message(embed=embeds.SkillMultipleInfoGMUserEmbed(self.target, page=self.page))
            elif option == "return":
                await interaction.response.edit_message(embed=embeds.SkillManagementEmbed(self.target), view=await regen(None, ""))
            else:
                option = int(option)
                _skill = 0
                for skill in self.skills:
                    if skill.id == option:
                        _skill = skill

                await interaction.response.edit_message(embed=embeds.SkillSingleInfoGMUserEmbed(self.target, option), view=await regen(_skill, "cast"))

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
                view.add_item(cast_button)
            if "extra" in flag:
                item.options.clear()
                item.add_option(label="Следующая страница", value="nextpage", emoji="➡️")
                item.add_option(label="Предыдущая страница", value="backpage", emoji="⬅️")
                item.add_option(label="Назад", value="return", emoji="↩️")
            view.add_item(item)
            view.add_item(self.back_btn)

            return view

        return self
