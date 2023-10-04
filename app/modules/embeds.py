import discord
from app.objects import User, Skill
from app.database import db_queries as dq
from math import ceil


class NoCharacterEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="(Критическая ошибка!)", color=discord.Color.from_rgb(120, 20, 0))
        self.add_field(name="Причина: [у цели нет ни одного персонажа]", value="")


class NoAccessEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="(Критическая ошибка!)", color=discord.Color.from_rgb(120, 20, 0))
        self.add_field(name="Причина: [у вас нет доступа для применения этой команды]", value="")


class NoAccessToManageEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="(Критическая ошибка)!", color=discord.Color.from_rgb(120, 20, 0))
        self.add_field(name=f"Причина: [у вас нет доступа для применения данного действия к данному пользователю]", value="")


class RegistrationFinishedEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title=f"[Персонаж был успешно зарегистрирован]", color=discord.Color.from_rgb(0, 124, 130))

class ProfileWasSuccessfullyChangedEmbed(discord.Embed):
    def __init__(self, character_name):
        super().__init__(title=f"Профиль персонажа [{character_name}] был успешно обновлен", color=discord.Color.from_rgb(0, 124, 130))


class CharacterWasSuccessfullyChangedEmbed(discord.Embed):
    def __init__(self, character_name):
        super().__init__(title=f"Ваш активный персонаж сменился на [{character_name}]", color=discord.Color.from_rgb(0, 124, 130))


class UserMenuEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title="(Меню игрока)", description=f"Цель: [{target.name}]", color=discord.Color.from_rgb(0, 124, 130))
        self = add_char_name(target, self)
        self.add_field(name="", value="", inline=False)
        self = add_avatar(target, self)
        self.add_field(name="Выберите действие для применения к данному игроку", value="", inline=False)


class GMMenuEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title="(ГМ меню)", description=f"Цель: [{target.name}]", color=discord.Color.from_rgb(0, 124, 130))
        self = add_char_name(target, self)
        self.add_field(name="", value="", inline=False)
        self = add_avatar(target, self)
        self.add_field(name="Выберите действие для применения к данному игроку", value="", inline=False)


class AdminMenuEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title="(Админ меню)", description=f"Цель: [{target.name}]", color=discord.Color.from_rgb(0, 124, 130))
        self = add_char_name(target, self)
        self.add_field(name="", value="", inline=False)
        self = add_avatar(target, self)
        self.add_field(name="Выберите действие для применения к данному игроку", value="", inline=False)


class ProfileShowerEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Анкета персонажа: [{target.active_character.webhook.name}]", color=discord.Color.from_rgb(144, 129, 163))

class TimeLineShowEmbed(discord.Embed):
    @classmethod
    async def create(cls, target: User):
        self = discord.Embed(title=f"Таймлайн персонажа: [{target.active_character.webhook.name}]", description=f"[{target.active_character.timeline}]", color=discord.Color.from_rgb(144, 129, 163))
        world_timeline = await dq.getWorldTimeline()
        self.add_field(name="", value="", inline=False)
        self.add_field(name="Общий таймлайн: ", value=f"[{world_timeline}]", inline=False)
        return self


class SkillManagementEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Управление заклинаниями персонажа [{target.active_character.webhook.name}]", color=discord.Color.from_rgb(30, 115, 125))


class SkillSingleInfoAdminEmbed(SkillManagementEmbed):
    def __init__(self, target: User, skill_id: int):
        super().__init__(target=target)
        sk = ''
        for skill in target.active_character.skills:
            if skill.id == skill_id:
                sk = skill

        self.add_field(name=f"Название заклинания: [{sk.title}]", value=f"{sk.desc}", inline=False)
        self.add_field(name="", value="", inline=False)
        self.add_field(name=f"Стоимость маны: [{sk.manacost}]", value="", inline=False)
        self.add_field(name=f"Элемент: [{sk.element_name.capitalize()}]", value="", inline=False)
        self.add_field(name=f"Ранг: [{sk.required_rank_name}]", value="", inline=False)

        if sk.learned == "Да":
            l_status = "Изучено"
        else:
            l_status = f"{sk.learn_progress} / {sk.need_to_learn}"

        self.add_field(name=f"Статус изучения: [{l_status}]", value="", inline=False)

        can_cast = "Нет"
        if sk.can_cast:
            can_cast = "Да"

        self.add_field(name=f"Может применять: [{can_cast}]", value="", inline=False)


class SkillMultipleInfoAdminEmbed(SkillManagementEmbed):
    def __init__(self, target: User, page=1):
        super().__init__(target=target)
        sk = ''
        max_page = ceil(len(target.active_character.skills) / 3)
        if max_page == 0: max_page += 1
        for skill in target.active_character.skills[(page - 1) * 3:page * 3]:
            sk = skill
            learn = f"{sk.learn_progress}/{sk.need_to_learn}"
            if sk.learned:
                learn = "Изучено"
            can = "Нет"
            if sk.can_cast:
                can = "Да"
            self.add_field(name=f"Название заклинания: [{sk.title}]", value=f"{sk.desc}", inline=False)
            self.add_field(name="", value="", inline=False)
            self.add_field(name=f"Стоимость маны: [{sk.manacost}]", value="", inline=False)
            self.add_field(name=f"Элемент: [{sk.element_name.capitalize()}]", value="", inline=False)
            self.add_field(name=f"Ранг: [{sk.required_rank_name}]", value="", inline=False)
            self.add_field(name=f"Статус изучения: [{learn}]", value="", inline=False)
            self.add_field(name=f"Может применять: [{can}]", value="", inline=False)
            self.add_field(name=f"", value="", inline=False)
        self.add_field(name="", value=f"Страница [{page}] из [{max_page}]", inline=False)


class PermissionsManagementEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Управление правами игрока [{target.name}]", color=discord.Color.from_rgb(76, 97, 122))


class PermissionsManagementSuccessEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(
            title=f"Права игрока [{target.name}] были успешно изменены!",
            description="Редирект через 3 секунды...", color=discord.Color.from_rgb(0, 124, 130))


class CoreProgressEmbed(discord.Embed):
    def __init__(self, target: User):
        t_ac = target.active_character
        super().__init__(title=f"Прогресс ядра персонажа [{t_ac.webhook.name}]: [{t_ac.progress_current} / {t_ac.progress_need}]", description="", color=discord.Color.from_rgb(76, 97, 122))
        self.add_field(name=f"Ранг: [{t_ac.rank_name}]", value="", inline=False)

    @staticmethod
    def update(target: User):
        return CoreProgressEmbed(target)


class ShowShortInfo(discord.Embed):
    def __init__(self, target: User):
        self.target = target
        ac = target.active_character
        super().__init__(title=f"Статистика персонажа [{ac.name}]", description="", color=discord.Color.from_rgb(76, 97, 122))
        self.add_field(name=f"Мутации:", value=f"{ac.profile.mutations}", inline=False)
        for affinity in ac.core.affinities:
            self.add_field(name=f"Сродство: [{affinity.affinity_element_name.capitalize()}]", value=f"Уровень: [{affinity.affinity_level_name}]")
        self.add_field(name=f"Ранг: [{ac.rank_name}]", value="", inline=False)
        self.add_field(name=f"Мана: [{ac.mana} / {ac.manapool}]", value="")
        self.add_field(name=f"Регенерация: [{ac.manapool / 5} в час]", value="")
        self.add_field(name=f"Таймлайн: [{ac.timeline}]", value="", inline=False)

    async def update(self, target: User):
        target = await self.target.update()
        return ShowShortInfo(target)


class TimelineEmbed(ShowShortInfo):
    def __init__(self, target: User, current_timeline: str):
        super().__init__(target)
        self.target = target
        self.add_field(name=f"Общий таймлайн: [{current_timeline}]", value="", inline=False)

    async def update(self, target: User):
        target = await self.target.update()
        return TimelineEmbed(target, await dq.getWorldTimeline())


class ManaChanged(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Мана персонажа [{target.active_character.webhook.name}] обновлена", color=discord.Color.from_rgb(0, 124, 130))


class MutationsChanged(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Мутации персонажа [{target.active_character.webhook.name}] обновлены", color=discord.Color.from_rgb(0, 124, 130))


class ProfileLockSwitchEmbed(discord.Embed):
    def __init__(self, target: User):
        self.target = target
        super().__init__(title=f"Персонаж [{target.active_character.webhook.name}] может менять профиль: [{target.active_character.can_edit_profile}]", color=discord.Color.from_rgb(120, 20, 0))

    async def update(self):
        target = await self.target.update()
        return ProfileLockSwitchEmbed(target)


class CharacterChangeLockSwitchEmbed(discord.Embed):
    def __init__(self, target: User):
        self.target = target
        super().__init__(title=f"Игрок [{target.name}] может переключать персонажей: [{target.can_change}]", color=discord.Color.from_rgb(120, 20, 0))

    async def update(self):
        target = await self.target.update()
        return CharacterChangeLockSwitchEmbed(target)


class ProfileLocked(discord.Embed):
    def __init__(self, target: User):
        self.target = target
        super().__init__(title=f"Персонаж [{target.active_character.webhook.name}] не может менять профиль", color=discord.Color.from_rgb(120, 20, 0))


class CharacterChangeLocked(discord.Embed):
    def __init__(self, target: User):
        self.target = target
        super().__init__(title=f"Игрок [{target.name}] не может менять персонажей", color=discord.Color.from_rgb(120, 20, 0))


class SkillSingleInfoGMUserEmbed(SkillManagementEmbed):
    def __init__(self, target: User, skill_id: int):
        super().__init__(target=target)
        self.target = target
        self.skill_id = skill_id
        sk = ''
        for skill in target.active_character.castable_skills:
            if skill.id == skill_id:
                sk = skill

        self.add_field(name=f"Название заклинания: [{sk.title}]", value=f"{sk.desc}", inline=False)
        self.add_field(name="", value="", inline=False)
        self.add_field(name=f"Стоимость маны: [{sk.manacost}]", value="", inline=False)
        self.add_field(name=f"Элемент: [{sk.element_name.capitalize()}]", value="", inline=False)
        self.add_field(name=f"Ранг: [{sk.required_rank_name}]", value="", inline=False)
        self.add_field(name=f"Мана: [{target.active_character.mana} / {target.active_character.manapool}]", value="", inline=False)

    async def update(self):
        target = await self.target.update()
        return SkillSingleInfoGMUserEmbed(target, self.skill_id)


class SkillMultipleInfoGMUserEmbed(SkillManagementEmbed):
    def __init__(self, target: User, page):
        super().__init__(target=target)
        sk = ''
        max_page = ceil(len(target.active_character.castable_skills) / 3)
        if max_page == 0: max_page += 1
        for skill in target.active_character.castable_skills[(page-1)*3:page*3]:
            sk = skill
            self.add_field(name=f"Название заклинания: [{sk.title}]", value=f"{sk.desc}", inline=False)
            self.add_field(name="", value="", inline=False)
            self.add_field(name=f"Стоимость маны: [{sk.manacost}]", value="", inline=False)
            self.add_field(name=f"Элемент: [{sk.element_name.capitalize()}]", value="", inline=False)
            self.add_field(name=f"Ранг: [{sk.required_rank_name}]", value="", inline=False)
            self.add_field(name=f"Мана: [{target.active_character.mana} / {target.active_character.manapool}]", value="", inline=False)
        self.add_field(name="", value=f"Страница [{page}] из [{max_page}]", inline=False)


class SkillCasted(discord.Embed):
    def __init__(self, target: User, skill: Skill):
        super().__init__(title=f"Персонаж [{target.active_character.webhook.name}] произнес заклинание \n({skill.title})", color=discord.Color.from_rgb(0, 124, 130))
        self.add_field(name=f"Ранг: [{skill.required_rank_name}]", value="")
        self.add_field(name=f"Элемент: [{skill.element_name.capitalize()}]", value="")
        self.set_author(name=f"[{target.active_character.id}] {target.active_character.webhook.name}")
        if not target.active_character.webhook.avatar_url == 'None' or target.active_character.webhook.avatar_url is not None:
            self.author.icon_url = target.active_character.webhook.avatar_url


class InventoryMenuEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Инвентарь персонажа [{target.active_character.webhook.name}]", color=discord.Color.from_rgb(144, 129, 163))
        self.add_field(name=f"Деньги: {target.active_character.money}", value="", inline=False)


class InventoryShowEmbed(InventoryMenuEmbed):
    def __init__(self, target: User, page=1):
        super().__init__(target)
        self.target = target
        max_page = ceil(len(target.active_character.inventory) / 5)
        if max_page == 0: max_page += 1
        for item in target.active_character.inventory[(page-1)*5:page*5]:
            self.add_field(name=f"[{item.name}]", value=f"[{item.desc}]", inline=False)
        self.add_field(name="", value=f"Страница [{page}] из [{max_page}]", inline=False)

    def update(self, page):
        return InventoryShowEmbed(self.target, page)


class InventorySingleShowEmbed(InventoryMenuEmbed):
    def __init__(self, target: User, item):
        super().__init__(target)
        self.target = target
        self.add_field(name=f"Предмет: [{item.name}]", value=f"Описание: {item.desc}")

    def update(self):
        return InventoryShowEmbed(self.target)


class WebhookMenuEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Управление Вебхуком персонажа [{target.active_character.webhook.name}]", description="(Вебкухи работают только в каналах с 'rp' в теме, либо в форумных тредах с тегом 'rp')", color=discord.Color.from_rgb(158, 68, 68))
        webhook = target.active_character.webhook
        self.add_field(name=f"Псевдоним: {webhook.name}", value="", inline=False)
        self = add_avatar(target, self)
        status = "Неактивен"
        if webhook.status == "activated":
            status = "Активирован"
        self.add_field(name=f"Текущий статус: {status}", value="", inline=False)


def add_avatar(target: User, embed: discord.Embed):
    webhook = target.active_character.webhook
    if webhook.avatar_url != "None" and webhook.avatar_url is not None:
        try:
            embed.set_image(url=webhook.avatar_url)
        except discord.HTTPException:
            pass
    return embed


def add_char_name(target: User, embed: discord.Embed):
    if target.active_character is not None:
        embed.add_field(name=f"Текущий персонаж: [{target.active_character.webhook.name}]", value="")
    return embed


class AreYouSure(discord.Embed):
    def __init__(self, target: User):
        self.target = target
        super().__init__(title=f"Вы уверены? В течении трех секунд нажмите на кнопку еще раз, чтобы удалить данный объект.", color=discord.Color.from_rgb(120, 20, 0))


class ProfileLayerEmbed(discord.Embed):
    def __init__(self, target: User):
        super().__init__(title=f"Управление профилем персонажа [{target.active_character.webhook.name}]", color=discord.Color.from_rgb(0, 124, 130))

