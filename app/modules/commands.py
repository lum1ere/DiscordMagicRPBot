import discord
import asyncio
from app.objects import User
from app.database import db_queries as dq
from app.utils import accessors
from app.objects.Character import Character
from app.objects.Skill import Skill
import re
from aiohttp import ClientSession
import json


async def log(target, action: str, log_desc: str, interaction: discord.Interaction):
    await dq.log(target.active_character.id, interaction.user.id, action, log_desc)


def checkTags(tags):
    for tag in tags:
        if "rp" in tag.name or "Rp" in tag.name or "RP" in tag.name: return True
    return False


async def processThreadWebhooks(msg: discord.Message, Bot):
    if not await dq.hasCharacter(msg.author.id): return
    user = await User.create(user_id=msg.author.id)
    if user.active_character.webhook.status == "deactivated": return

    tags = msg.channel.applied_tags
    if not checkTags(tags): return

    sel_webhook = await getActiveWebHook(msg.channel.id, msg.channel.parent, Bot)
    msg.content = msg.content.replace("-", "—", 12)
    await sendWebhook(msg, sel_webhook, user)

    await msg.delete()

    await processSyncCheck(msg, user.active_character.webhook, sel_webhook, msg.channel.id)
    await registerOfUsingWebhook(msg)


async def sendWebhook(msg, sel_webhook, user):
    async with ClientSession() as cs:

        url = f"https://discord.com/api/webhooks/{sel_webhook.id}/{sel_webhook.token}?thread_id={msg.channel.id}"
        data = {
                "username": f"{user.active_character.webhook.name}",
                "content": f"{msg.content}",
            }
        if user.active_character.webhook.avatar_url == "None" or user.active_character.webhook.avatar_url is None:
            pass
        else:
            data["avatar_url"] = f"{user.active_character.webhook.avatar_url}"

        await cs.post(url=url, data=data)


async def processNormalWebhooks(msg: discord.Message, Bot):
    if not await dq.hasCharacter(msg.author.id): return
    user = await User.create(msg.author.id)
    if user.active_character.webhook.status == "disabled": return

    sel_webhook = await getActiveWebHook(msg.channel.id, msg.channel, Bot)
    msg.content = msg.content.replace("-", "—", 12)
    if user.active_character.webhook.avatar_url == "None" or user.active_character.webhook.avatar_url is None:
        await sel_webhook.send(content=msg.content, username=user.active_character.webhook.name)
    else:
        await sel_webhook.send(content=msg.content, username=user.active_character.webhook.name, avatar_url=user.active_character.webhook.avatar_url)

    await msg.delete()

    await processSyncCheck(msg, user.active_character.webhook, sel_webhook, msg.channel.id)
    await registerOfUsingWebhook(msg)


async def getActiveWebHook(channel_id, channel, Bot):
    webhooks = await channel.webhooks()
    sel_webhook = ""
    for wh in webhooks:
        if wh.user.id == Bot.user.id:
            sel_webhook = wh
            break

    if sel_webhook == "":
        sel_webhook = await channel.create_webhook(name="RP")
        await dq.createWebhook(sel_webhook.id, channel_id)
        await dq.useWebhook(sel_webhook.id, 1, channel_id)

    return sel_webhook


async def processWebhookCheck(msg: discord.Message, Bot):
    if (msg.channel.type.name == "public_thread" or msg.channel.type.name == "private_thread") and not "/" in msg.content[:2] and msg.webhook_id is None and msg.author.id != Bot.user.id:
        if await envCheck(msg, Bot, flag="thread"): return
        await processThreadWebhooks(msg, Bot)

    elif not msg.author.id == Bot.user.id and not "/" in msg.content[:2] and msg.webhook_id is None:
        if await envCheck(msg, Bot): return
        if msg.channel.topic is None: msg.channel.topic = "ooc"
        if "rp" in msg.channel.topic:
            await processNormalWebhooks(msg, Bot)

    if msg.author.id == Bot.user.id and msg.embeds:
        if "произнес" in msg.embeds[0].title and not "x" in msg.embeds[0].title:
            await multicastingCheck(msg, Bot)


async def processSyncCheck(msg: discord.Message, uhook, selected_webhook, channel_id):
    character1 = await Character.create(uhook.character_id)
    character2 = await dq.getLastUsed(selected_webhook.id, channel_id)
    async def comparement():
        await compare_timeline(character1, character2, msg.channel, selected_webhook, channel_id)

    await comparement()


async def registerOfUsingWebhook(msg):
    previous_messages = msg.channel.history(limit=5)
    async for message in previous_messages:
        if message.webhook_id is None:
            pass
        else:
            if not (await dq.webhookMessageCheck(message.id, msg.author.id)):
                await dq.webhookMessageRegister(message.id, msg.author.id)


async def delay_delete(message: discord.Message):
    await asyncio.sleep(8)
    await message.delete()


async def compare_timeline(c1: Character, c2: Character, channel: discord.TextChannel, selected_webhook, channel_id):
    timeline_1 = c1.timeline
    timeline_2 = c2.timeline
    embed = discord.Embed(
        title=f"Внимание! Таймлайн персонажей [{c1.webhook.name}] и [{c2.webhook.name}] не совпадает!")
    if timeline_1 != timeline_2:
        await channel.send(embed=embed)
        message = [message async for message in channel.history(limit=1)][0]
        loop = asyncio.get_event_loop()
        loop.create_task(coro=delay_delete(message))
    await dq.useWebhook(selected_webhook.id, c1.id, channel_id)


async def envCheck(msg: discord.Message, Bot, flag="normal"):
    if not await dq.hasCharacter(msg.author.id): return
    user = await User.create(msg.author.id)
    if "env" in msg.content[:5]:
        permission_level = await dq.getAccessLevel(msg.author.id)
        if permission_level <= 2:
            content = (msg.content.split("$"))
            embed = discord.Embed(title="")

            for line in content[1:]:
                sublines = line.split("!")
                if len(sublines) == 1: sublines.insert(0, "")
                for i, subline in enumerate(sublines):
                    url_pattern = r"<([^>]+)>"
                    url = re.findall(url_pattern, subline)
                    try:
                        if not url:
                            pass
                        else:
                            embed.set_image(url=url[0])
                            sublines[i] = subline.replace(f"<{url[0]}>", "")
                    except discord.HTTPException:
                        pass

                embed.add_field(name=sublines[0], value=sublines[1], inline=False)

            webhook = ""
            if "normal" in flag:
                webhook = await getActiveWebHook(msg.channel.id, msg.channel, Bot)
            if "thread" in flag:
                webhook = await getActiveWebHook(msg.channel.id, msg.channel.parent, Bot)

            if "normal" in flag:

                await webhook.send(embed=embed, username="ٴٴٴٴٴ ", avatar_url="https://cdn.discordapp.com/attachments/661231649895350272/1044700937685573772/-1.png")

            if "thread" in flag:

                await webhook.send(embed=embed, username="ٴٴٴٴٴ ", avatar_url="https://cdn.discordapp.com/attachments/661231649895350272/1044700937685573772/-1.png", thread=msg.channel)

            await msg.delete()
            return True

        return False
    elif "gm" in msg.content[:5]:
        permission_level = await dq.getAccessLevel(msg.author.id)
        if permission_level <= 2:
            content = (msg.content.replace("gm", ""))

            webhook = ""

            if "normal" in flag:
                webhook = await getActiveWebHook(msg.channel.id, msg.channel, Bot)
            if "thread" in flag:
                webhook = await getActiveWebHook(msg.channel.id, msg.channel.parent, Bot)

            if "normal" in flag:
                try:
                    await webhook.send(content=content, username="ٴٴٴٴٴ ", avatar_url="https://cdn.discordapp.com/attachments/661231649895350272/1044700937685573772/-1.png")
                except discord.HTTPException:
                    pass
            if "thread" in flag:
                user.active_character.webhook.name = "ٴٴٴٴٴ "
                user.active_character.webhook.avatar_url = "https://cdn.discordapp.com/attachments/661231649895350272/1044700937685573772/-1.png"
                msg.content = content
                msg.content = msg.content.replace("-", "—", 12)
                await sendWebhook(msg, webhook, user)

            await msg.delete()
            return True

    return False


async def multicastingCheck(msg: discord.Message, Bot):
    await asyncio.sleep(8)
    spells = []
    char_id = msg.embeds[0].author.name.split("]")[0][1:]
    character = await Character.create(int(char_id))

    result = await dq.getMulticast(character)
    await dq.delMulticast(character)

    for statement in result:
        for spell_name in statement:
            spells.append(spell_name)
    used_count = {}
    for spell in spells:
        if spell in used_count.keys():
            used_count[spell] += 1
        else:
            used_count[spell] = 1

    for spell in used_count:
        title = f"Персонаж [{character.webhook.name}] произнес заклинания \n({spell} x{used_count[spell]})"
        embed = discord.Embed(title=title, color=discord.Color.from_rgb(0, 124, 130) )
        skill = await Skill.create(await dq.getSkillIdBySkillName(spell))
        embed.add_field(name=f"Ранг: [{skill.required_rank_name}]", value="")
        embed.add_field(name=f"Элемент: [{skill.element_name.capitalize()}]", value="")
        embed.set_author(name=f"[{character.id}] {character.webhook.name}")
        if not character.webhook.avatar_url == 'None' or character.webhook.avatar_url is not None:
            embed.author.icon_url = character.webhook.avatar_url
        try:
            await msg.channel.send(embed=embed)
        except Exception as ex:
            print(ex)
    await msg.delete()








