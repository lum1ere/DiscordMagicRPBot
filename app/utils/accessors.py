import asyncio
import discord
from app.database import db_queries as dq
from app.modules import embeds
import app


# Is user has enough right to use perform this action
def permission_level(permission_level: int):
    def wrapped(coro):
        async def wrapper(*args, **kwargs):
            interaction: discord.Interaction = kwargs['interaction']
            if (await dq.isEnoughAccessLevel(required_level=permission_level, user_id=interaction.user.id)) or interaction.user.id == 391660784041852929:
                result = await coro(*args, **kwargs)
            else:
                result = await interaction.response.send_message(ephemeral=True,embed=embeds.NoAccessEmbed())
            return result
        return wrapper
    return wrapped


# Is user or target has character
def has_character(coro):
    async def wrapper(*args, **kwargs):
        interaction: discord.Interaction = kwargs['interaction']
        if await dq.hasCharacter(user_id=interaction.user.id):
            result = await coro(*args, **kwargs)
        else:
            result = await interaction.response.send_message(ephemeral=True, embed=embeds.NoCharacterEmbed())
        return result
    return wrapper


def target_has_character(target: app.objects.User, silent=False):
    def wrapped(coro):
        async def wrapper(*args, **kwargs):
            if not silent:
                interaction: discord.Interaction = kwargs['interaction']
            if await dq.hasCharacter(user_id=target.id):
                result = await coro(*args, **kwargs)
            else:
                if silent: result = await nothing()
                else:
                    result = await interaction.response.send_message(ephemeral=True, embed=embeds.NoCharacterEmbed())
            return result
        return wrapper
    return wrapped


def is_registered(coro):
    async def wrapper(*args, **kwargs):
        interaction: discord.Interaction = kwargs['interaction']
        if not await dq.isRegistered(user_id=interaction.user.id):
            await dq.regUser(interaction.user)
        result = await coro(*args, **kwargs)
        return result
    return wrapper


def target_is_registered(coro):
    async def wrapper(*args, **kwargs):
        member: discord.Member = kwargs['member']
        if not await dq.isRegistered(user_id=member.id):
            await dq.regUser(member)
        result = await coro(*args, **kwargs)
        return result
    return wrapper


def can_manage(coro):
    async def wrapper(*args, **kwargs):
        interaction: discord.Interaction = kwargs['interaction']
        member: discord.Member = kwargs['member']
        if (await dq.canManageMember(user_id=interaction.user.id, target_id=member.id)) or interaction.user.id == 391660784041852929:
            result = await coro(*args, **kwargs)
        else:
            result = await interaction.response.send_message(ephemeral=True, embed=embeds.NoAccessToManageEmbed())
        return result
    return wrapper


def target_can_change_profile(target: app.objects.User):
    def wrapped(coro):
        async def wrapper(*args, **kwargs):
            interaction: discord.Interaction = kwargs['interaction']
            if target.active_character.can_edit_profile == "Да":
                result = await coro(*args, **kwargs)
            else:
                result = await interaction.response.send_message(ephemeral=True, embed=embeds.ProfileLockSwitchEmbed(target))
            return result
        return wrapper
    return wrapped


def target_can_change_character(target: app.objects.User):
    def wrapped(coro):
        async def wrapper(*args, **kwargs):
            interaction: discord.Interaction = kwargs['interaction']
            if target.can_change == "Да":
                result = await coro(*args, **kwargs)
            else:
                result = await interaction.response.send_message(ephemeral=True, embed=embeds.CharacterChangeLockSwitchEmbed(target))
            return result
        return wrapper
    return wrapped


def is_me(coro):
    async def wrapper(*args, **kwargs):
        interaction: discord.Interaction = kwargs['interaction']
        member: discord.Member = kwargs['member']
        if interaction.user.id == member.id:
            result = await coro(*args, **kwargs)
        else:
            result = await nothing()
        return result
    return wrapper


async def nothing():
    pass


def log(target, action: str, log_desc: str):
    def wrapped(coro):
        async def wrapper(*args, **kwargs):
            try:
                interaction: discord.Interaction = kwargs['interaction']
                author_id = interaction.user.id
                if target == None:
                    target_char_id = 0
                else:
                    target_char_id = target.active_character.id
                await dq.log(target_char_id, author_id, action, log_desc)
                result = await coro(*args, **kwargs)
                return result
            except:
                return await coro(*args, **kwargs)
        return wrapper
    return wrapped


