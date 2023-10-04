from app.variables import get_token, get_db, get_logs_db, get_active_guilds
from app.objects.User import User
import app.database.db_queries as dq
from app.database import db_init
from app.utils.accessors import permission_level, has_character, is_registered, target_has_character, can_manage, target_is_registered, log
from app.modules import reg, profile, change_character, user_context_menu, embeds, gm_context_menu, admin_context_menu, ctx_skill_panel_user_gm
from app.modules import standart_modules, menu, superadmin, webhooks_panel
from app.modules.commands import processSyncCheck as psc
from app.modules.commands import processWebhookCheck as pwc
from app.modules.commands import log as lg
import os
import asyncio
import discord
from discord import ui
from discord import ext
from discord.ext import commands

TOKEN = get_token()
intents = discord.Intents.all()
intents.message_content = True
Bot = commands.Bot(command_prefix="$$", intents=intents)
Tree: discord.app_commands.CommandTree = Bot.tree
guilds = get_active_guilds()


@Bot.event
async def on_ready():
    if os.path.exists(get_db()):
        print("База найдена")
    else:
        print("База не найдена. Создаем...")
        await db_init.create()
        await db_init.primary_insert()
        print("База данных rp создана")
    if os.path.exists(get_logs_db()):
        print("База найдена")
    else:
        print("База не найдена. Создаем...")
        await db_init.create_messages()
        print("База данных messages создана")
    #loop = asyncio.get_event_loop()
    #loop.create_task(coro=dq.clearBadCharacters(3600))
    status, text_status = await dq.getDiscordSettings()
    if status == 'dnd':
        await Bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(name=text_status, type=discord.ActivityType.watching))
    elif status == 'online':
        await Bot.change_presence(status=discord.Status.online, activity=discord.Activity(name=text_status, type=discord.ActivityType.watching))
    elif status == 'offline':
        await Bot.change_presence(status=discord.Status.invisible, activity=discord.Activity(name=text_status, type=discord.ActivityType.watching))
    elif status == 'idle':
        await Bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name=text_status, type=discord.ActivityType.watching))
    for guild in guilds:
        await Tree.sync(guild=guild)


@Bot.event
async def on_message(msg: discord.Message):
    await Bot.process_commands(msg)
    try:
        await pwc(msg, Bot)
    except Exception as ex:
        print(f"[Exception]: {ex}")


@Bot.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
    channel = await Bot.fetch_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    if message.webhook_id is None:
        pass
    else:
        if await dq.webhookMessageCheck(message.id, reaction.user_id) and reaction.emoji.name == "❌":
            await message.delete()
            await dq.webhookMessageDelete(message.id)


@Tree.command(name="menu", guilds=guilds, description="Открыть меню")
async def menuUser(interaction: discord.Interaction):
    @is_registered
    async def callback(**kwargs):
        user = await User.create(interaction.user.id)
        view = menu.UserMenu(user)
        try:
            await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)
        except:
            target_user.active_character.webhook.avatar_url = 'None'
            await dq.webhookChange(target_user, target_user.active_character.webhook)
            await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)
        await lg(user, "opened_menu", f"Пользователь {user.name} открыл меню", interaction)

    await callback(interaction=interaction)


@Tree.command(name="cast", guilds=guilds, description="Быстрый каст")
async def castSkill(interaction: discord.Interaction):
    @is_registered
    @has_character
    async def callback(**kwargs):
        target = await User.create(interaction.user.id)
        view = ctx_skill_panel_user_gm.SkillPanel(target=target)
        await interaction.response.send_message(view=view, embed=view.embed, ephemeral=True)
    await callback(interaction=interaction)


@Tree.context_menu(name="[U] Меню игрока", guilds=guilds)
async def userMenu(interaction: discord.Interaction, member: discord.Member):
    @is_registered
    @target_is_registered
    async def callback(**kwargs):
        target_user = await User.create(user_id=member.id)

        view = user_context_menu.UserMenu(target=target_user)
        try:
            await interaction.response.send_message(view=view, ephemeral=True, embed=view.embed)
        except:
            target_user.active_character.webhook.avatar_url = 'None'
            await dq.webhookChange(target_user, target_user.active_character.webhook)
            await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)

    await callback(interaction=interaction, member=member)


@Tree.context_menu(name="[GM] ГМ меню", guilds=guilds)
async def gmMenu(interaction: discord.Interaction, member: discord.Member):
    @is_registered
    @target_is_registered
    @permission_level(2)
    @can_manage
    async def callback(**kwargs):
        target_user = await User.create(user_id=member.id)
        view = gm_context_menu.GmMenu(target=target_user)
        try:
            await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)
        except:
            target_user.active_character.webhook.avatar_url = 'None'
            await dq.webhookChange(target_user, target_user.active_character.webhook)
            await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)


    await callback(interaction=interaction, member=member)


@Tree.context_menu(name="[A] Админ меню", guilds=guilds)
async def adminMenu(interaction: discord.Interaction, member: discord.Member):
    @is_registered
    @target_is_registered
    @permission_level(1)
    @can_manage
    async def callback(**kwargs):
        target_user = await User.create(user_id=member.id)
        view = admin_context_menu.AdminMenu(target=target_user)
        try:
            await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)
        except:
            target_user.active_character.webhook.avatar_url = 'None'
            await dq.webhookChange(target_user, target_user.active_character.webhook)
            await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)

    await callback(interaction=interaction, member=member)


@Tree.context_menu(name="...", guilds=guilds)
async def sadminMenu(interaction: discord.Interaction, member: discord.Member):
    @is_registered
    @target_is_registered
    @permission_level(0)
    async def callback(**kwargs):
        target_user = await User.create(user_id=member.id)
        modal = superadmin.Super(target_user)
        await interaction.response.send_modal(modal)

    await callback(interaction=interaction, member=member)


@Tree.command(name="webhooks", guilds=guilds, description="Управление вебхуками")
async def webhooks(interaction: discord.Interaction):
    @is_registered
    @has_character
    async def callback(**kwargs):
        target_user = await User.create(user_id=interaction.user.id)
        view = webhooks_panel.WebhookMenu(target_user)
        await interaction.response.send_message(ephemeral=True, view=view, embed=view.embed)

    await callback(interaction=interaction)


Bot.run(TOKEN)
