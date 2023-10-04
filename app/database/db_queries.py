import asyncio
from sqlite3 import Row
from typing import Iterable
from datetime import datetime

import discord

import app.objects
from app.variables import get_db, get_logs_db
from app.objects import User, Character, Core, Skill, Profile, Affinity
import aiosqlite


# Get user name by user id
async def getNameById(user_id: int) -> str:
    async with aiosqlite.connect(database=get_db()) as connection:
        query = "SELECT name FROM rp_users WHERE user_id = %i" % user_id
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response[0][0]


# get canChange statement of user by user id
async def canChange(user_id: int) -> str:
    async with aiosqlite.connect(database=get_db()) as connection:
        query = "SELECT can_change FROM rp_users WHERE user_id = %i" % user_id
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response[0][0]


# get full information about skill
async def everythingAboutSkillFromSkillId(skill_id: int) -> tuple:
    query = """
            SELECT skills.*, skillsets.learn_progress, skillsets.learned,
            ranks.name AS rank_name, elements.name AS element_name  FROM skillsets
            JOIN skills ON skillsets.skill_id = skills.skill_id
            JOIN elements ON skills.element_id = elements.element_id
            JOIN ranks ON skills.required_rank_id = ranks.rank_id
            WHERE skills.skill_id = %i
            """ % skill_id
    async with aiosqlite.connect(database=get_db()) as connection:
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response[0]


# get * about Core
async def everythingAboutCoreFromCoreId(core_id: int) -> tuple:
    query = """
            SELECT core_affinities.element_id, elements.name AS element_name, core_affinities.affinity_level
            FROM core_affinities
            JOIN elements ON elements.element_id = core_affinities.element_id
            WHERE core_affinities.core_id = %i 
            """ % core_id
    async with aiosqlite.connect(database=get_db()) as connection:
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response


# get current if of current character of selected user
async def currentCharacterIdOfUser(user_id: int) -> int:
    async with aiosqlite.connect(database=get_db()) as connection:
        query = "SELECT active_character_id FROM rp_users WHERE user_id = %i" % user_id
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            if not response:
                return None
            return response[0][0]


# get * about character
async def everythingAboutCharacterByCharacterId(character_id: int) -> tuple:
    query = """
            SELECT rp_characters.name, rp_characters.mana, rp_characters.manapool, 
            rp_characters.rank_id, ranks.name as rank_name, rp_characters.core_progress_curent, 
            rp_characters.core_progress_need, rp_characters.character_timeline, rp_characters.profile_edit, rp_characters.money
            FROM rp_characters JOIN ranks ON rp_characters.rank_id = ranks.rank_id
            WHERE rp_characters.character_id = %i
            """ % character_id
    async with aiosqlite.connect(database=get_db()) as connection:
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response[0]


# get * about profile of character
async def everythingAboutProfileByCharacterId(character_id: int) -> tuple:
    query = "SELECT * FROM profiles WHERE character_id = %i" % character_id
    async with aiosqlite.connect(database=get_db()) as connection:
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response[0]


# custom query with return
async def customQueryRead(query: str) -> Iterable[Row]:
    async with aiosqlite.connect(database=get_db()) as connection:
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response


# custom query without return
# NOTE THAT IT REQUIRES COMMIT() OR ROLLBACK() !!!
async def coreIdOfCharacterByCharacterId(character_id: int) -> int:
    async with aiosqlite.connect(database=get_db()) as connection:
        query = "SELECT core_id FROM characters_lists WHERE character_id = %i" % character_id
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            return response[0][0]


async def getDiscordSettings() -> tuple:
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(sql="SELECT * FROM discord_settings") as cursor:
            response = await cursor.fetchall()
            return response[0]


async def isEnoughAccessLevel(required_level: int, user_id: int) -> bool:
    response = await getAccessLevel(user_id)
    if response <= required_level:
        return True
    else:
        return False


async def hasCharacter(user_id: int) -> bool:
    async with aiosqlite.connect(database=get_db()) as connection:
        query = "SELECT character_id FROM rp_characters WHERE user_id = %i" % user_id
        async with connection.execute(sql=query) as cursor:
            response = await cursor.fetchall()
            if not response:
                return False
            else:
                return True


async def getAccessLevel(user_id: int):
    async with aiosqlite.connect(database=get_db()) as connection:
        async with connection.execute(sql=f"""
            SELECT permissions.permission_level FROM permissions 
            JOIN rules ON permissions.permission_id = rules.permission_id 
            WHERE rules.user_id = {user_id}
            """) as cursor:
            response = await cursor.fetchall()
            return response[0][0]


async def isRegistered(user_id: int):
    async with aiosqlite.connect(database=get_db()) as connection:
        async with connection.execute(sql=f"SELECT user_id FROM rp_users WHERE user_id = {user_id}") as cursor:
            response = await cursor.fetchall()
            if not response:
                return False
            else:
                return True


async def regUser(user):
    query_set = [f"INSERT INTO rp_users VALUES ({user.id}, '{user.name}', NULL, 'Да' )",
                 f"INSERT INTO rules VALUES ({user.id}, 4)"]
    async with aiosqlite.connect(database=get_db()) as connection:
        try:
            [await customQueryWrite(connection, query) for query in query_set]
            await connection.commit()
        except Exception as ex:
            await connection.rollback()


async def canManageMember(user_id: int, target_id, soft=True) -> bool:
    user_level = await getAccessLevel(user_id)
    target_level = await getAccessLevel(target_id)
    if soft:
        if user_level < target_level or (user_id == target_id and user_level <= 1):
            return True
        else:
            return False
    else:
        if user_level < target_level or user_id == target_id:
            return True
        else:
            return False


async def customQueryWrite(connection: aiosqlite.Connection, query: str) -> None:
    await connection.execute(sql=query)


async def changeMana(character: Character, value: float):
    current_mana = character.mana
    query = f"UPDATE rp_characters SET mana = {current_mana + value} WHERE character_id = {character.id}"
    async with aiosqlite.connect(get_db()) as connection:
        await customQueryWrite(connection, query=query)
        await connection.commit()


async def regCharacter(user_id: int, character) -> None:
    async with aiosqlite.connect(get_db()) as connection:
        manapool = (await getRankAttrib(3))[2]
        timeline = await getWorldTimeline()
        query = f"""INSERT INTO rp_characters VALUES
                    (NULL, {user_id}, '%s', {manapool}, {manapool}, 3, 5, 0, '{timeline}', 'Да', 0.0)
                """ % character.name
        await connection.execute(query)
        await connection.commit()
        cursor = await connection.execute(f"SELECT character_id FROM rp_characters WHERE user_id = {user_id}")
        character.id = (await cursor.fetchall())[-1][0]
        queries = [
            f"UPDATE rp_users SET active_character_id = {character.id} WHERE user_id = {user_id}",
            f"INSERT INTO characters_lists VALUES ({character.id}, {character.id}, {character.id})",
            f"INSERT INTO profiles VALUES ({character.id}, '-', '-', '-', '-', '-', '-', '-', '-', '-')",
            f"INSERT INTO webhooks VALUES (NULL, {character.id}, '%s', NULL, 'deactivated')" % (character.name, )
        ]
        [await connection.execute(query) for query in queries]
        await connection.commit()

        await customQueryWrite(connection, f"INSERT INTO core_types VALUES ({character.id}, '{character.core.core_type}')")

        for affinity in character.core.affinities:
            await customQueryWrite(connection, f"INSERT INTO core_affinities VALUES (NULL, {character.id}, {affinity.affinity_element_id}, '{affinity.affinity_level_name}')")
        await connection.commit()



async def getRankAttrib(rank_id) -> tuple:
    query = f"SELECT * FROM ranks WHERE rank_id = %i" % rank_id
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(query) as cursor:
            response = await cursor.fetchall()
            return response[0]


async def getWorldTimeline() -> str:
    query="SELECT value FROM environment WHERE variable_id = 'world_time'"
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(query) as cursor:
            response = await cursor.fetchall()
            return response[0][0]

async def getAllElements() -> list:
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute("SELECT * FROM elements") as cursor:
            response = await cursor.fetchall()
            return response


async def getNeededAffinityLevel(core):
    core_type = core.core_type
    current_length = len(core.affinities)
    if core_type == "Стандартный":
        if current_length == 0:
            return "Высокий"
        elif current_length == 1 or current_length == 2:
            return "Средний"
        else:
            return "STOP"

    if core_type == "Дуальный":
        if current_length == 0 or current_length == 1:
            return "Высокий"
        else:
            return "STOP"

    if core_type == "Аспект":
        if current_length == 0:
            return "Высший"
        else:
            return "STOP"

async def addAffinity(core: Core, aff: Affinity):
    affinities = core.affinities
    elems_id = []
    for affinity in affinities:
        elems_id.append(affinity.affinity_element_id)
    core_id = core.id
    flag = True
    for elem_id in elems_id:
        if element_id == elem_id:
            flag = False

    if flag:
        async with aiosqlite.connect(get_db()) as connection:
            await customQueryWrite(connection, f"INSERT INTO core_affinities VALUES (NULL, {core_id}, {element_id}, '{level}')")
            await connection.commit()


async def clearBadCharacters(delay=100):
    while True:
        async with aiosqlite.connect(get_db()) as connection:
            bad = await connection.execute("SELECT character_id FROM rp_characters WHERE character_id NOT IN (SELECT core_id FROM core_types)")
            bad_list = await bad.fetchall()
            await connection.execute("DELETE FROM rp_characters WHERE character_id NOT IN (SELECT core_id FROM core_types)")
            await connection.commit()
            #counter = 0
            #for statement in bad_list: counter += 1
            #print(f"Удалено {counter} дефектных персонажей!")
        await asyncio.sleep(delay=delay)


async def changeProfileOfCharacter(character: Character, args):
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(f"""
        UPDATE profiles 
        SET short_desc = '%s',
            field_1 = '%s',
            field_2 = '%s',
            field_3 = '%s'
            WHERE character_id = {character.id}
        """ % (args[0], args[1], args[2], args[3]))
        await connection.commit()


async def changeExtraProfileOfCharacter(character: Character, args):
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(f"""
        UPDATE profiles 
        SET extra_field_1 = '%s',
            extra_field_2 = '%s',
            extra_field_3 = '%s',
            extra_field_4 = '%s'
            WHERE character_id = {character.id}
        """ % (args[0], args[1], args[2], args[3]))
        await connection.commit()


async def getCharactersOfUser(user: User) -> list:
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(f"SELECT character_id, name FROM rp_characters WHERE user_id = {user.id}") as cursor:
            response = await cursor.fetchall()
            return response


async def changeActiveCharacterOfUser(user: User, character_id) -> None:
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(f"UPDATE rp_users SET active_character_id = {character_id} WHERE user_id = {user.id}")
        await connection.commit()


async def allSkillsIdOfCharacter(character: Character):
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(f"SELECT skill_id from skillsets WHERE skillset_id = "
                                      f"(SELECT skillset_id FROM characters_lists WHERE character_id = {character.id})") as cursor:
            response = await cursor.fetchall()
            if not response:
                return []
            return [statement[0] for statement in response]


async def allSkillsOfCharacter(character: Character):
    await skil

def canCast(character: Character, skill: Skill):
    for affinity in character.core.affinities:
        aff_elem = affinity.affinity_element_id
        weight = affinity.affinity_level_value
        if aff_elem == skill.element_id and (character.rank_id + weight >= skill.required_rank_id) and skill.learned == "Да":
            return "Да"
        elif character.rank_id >= skill.required_rank_id and character.core.core_type != "Аспект" and skill.element_name == 'базовый' and skill.learned == "Да":
            return "Да"
    return "Нет"


async def getAllRanks():
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(f"SELECT * FROM ranks") as cursor:
            response = await cursor.fetchall()
            return response

async def initSkill(skill, target: User):
    query = f"""
    INSERT INTO skills VALUES 
    (NULL, '%s', {skill.manacost}, {skill.need_to_learn}, {skill.element_id}, '%s', {skill.required_rank_id})
             """ % (skill.title, skill.desc)

    skill_id_query = f"SELECT skill_id from skills"
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(query)
        await connection.commit()
        async with connection.execute(skill_id_query) as cursor:
            response = await cursor.fetchall()
            skill_id = response[-1][0]

        if skill.need_to_learn <= skill.learn_progress:
            skill.learned = "Да"
        else:
            skill.learned = "Нет"
        query_for_set = f"""
            INSERT INTO skillsets VALUES (NULL, {target.active_character.id}, {skill_id}, '{skill.learned}', {skill.learn_progress})
                         """
        await connection.execute(query_for_set)
        await connection.commit()


async def allPermissions(user_id):
    user_access = await getAccessLevel(user_id)
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute("SELECT * FROM permissions") as cursor:
            response = await cursor.fetchall()
            result = []
            for statement in response:
                if user_access < statement[2] or user_id == 391660784041852929:
                    result.append(statement)
            return result


async def changePermission(target: User, perm_id):
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(f"UPDATE rules SET permission_id = {perm_id} WHERE user_id = {target.id}")
        await connection.commit()


async def addProgressPoint(target: User):
    t_ac = target.active_character
    if t_ac.progress_current + 1 >= t_ac.progress_need:
        async with aiosqlite.connect(get_db()) as connection:
            normal_manapool = (await(await connection.execute(f"SELECT standart_manapool FROM ranks WHERE rank_id = {t_ac.rank_id}")).fetchall())[0][0]
            next_manapool = (await(await connection.execute(f"SELECT standart_manapool FROM ranks WHERE rank_id = {t_ac.rank_id + 1}")).fetchall())[0][0]
            new_manapool = (t_ac.manapool / normal_manapool) * next_manapool
            await connection.execute(f"""
            UPDATE rp_characters SET core_progress_curent = 0,
            rank_id = {t_ac.rank_id + 1},
            manapool = {new_manapool},
            core_progress_need = {t_ac.progress_need + 4}
            WHERE character_id = {t_ac.id}""")
            await connection.commit()

    else:
        async with aiosqlite.connect(get_db()) as connection:
            await connection.execute(f"UPDATE rp_characters SET core_progress_curent = {t_ac.progress_current + 1} WHERE character_id = {t_ac.id}")
            await connection.commit()
    t_ac.progress_current += 1

# async def getElementName(element_id: int):
#     query = f"SELECT name from elements WHERE element_id = {element_id}"
#     async with aiosqlite.connect(get_db()) as conn:
#         async with conn.execute(query) as c:
#             response = await c.fetchall()
#             return response[0][0]


async def changeTimeline(target: User, timeline):
    current_timeline = target.active_character.timeline

    input_components = timeline.split(" ")
    input_days = input_components[0][:-1]
    input_hours = input_components[1].split(":")[0]
    input_int_days = int(input_days)
    input_int_hours = int(input_hours)

    components = current_timeline.split(" ")
    days = components[0][:-1]
    hours = components[1].split(":")[0]
    int_days = int(days)
    int_hours = int(hours)
    value = (input_int_days - int_days)*24 + (input_int_hours - int_hours)
    int_hours += value
    while int_hours >= 24 or int_hours < 0:
        if int_hours >= 24:
            int_days += 1
            int_hours = int_hours - 24
        elif int_hours < 0:
            int_days -= 1
            int_hours += 24

    new_days = str(int_days)
    if int_hours <= 9:
        new_hours = '0' + str(int_hours)

    else:
        new_hours = str(int_hours)
    current_timeline = current_timeline.replace(f"{days}d", f"{new_days}d", 1)
    current_timeline = current_timeline.replace(f"{hours}:00:00", f"{new_hours}:00:00", 1)

    async with aiosqlite.connect(get_db()) as connection:
        query = f"UPDATE rp_characters SET character_timeline = '{current_timeline}' WHERE character_id = {target.active_character.id}"
        await connection.execute(query)
        await connection.commit()

    current_mana = target.active_character.mana
    manapool = target.active_character.manapool
    regen = manapool / 5
    current_mana += regen * value
    if value > 0:
        await target.active_character.changeMana(value=regen*value)


async def changeManapoolAndMana(target: User, manapool: float, mana: float):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(f"UPDATE rp_characters SET manapool = {manapool} WHERE character_id = {target.active_character.id}")
        await conn.execute(f"UPDATE rp_characters SET mana = {mana} WHERE character_id = {target.active_character.id}")
        await conn.commit()


async def changeMutations(target: User, mutations: str):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(f"UPDATE profiles SET mutations = '%s' WHERE character_id = {target.active_character.id}" % mutations)
        await conn.commit()


async def switchProfileBlock(target: User):
    async with aiosqlite.connect(get_db()) as conn:
        if target.active_character.can_edit_profile == "Да":
            insert = "Нет"
        else:
            insert = "Да"

        await conn.execute(
            f"UPDATE rp_characters SET profile_edit = '{insert}' WHERE character_id = {target.active_character.id}")

        await conn.commit()


async def switchCharactersChangingBlock(target: User):
    async with aiosqlite.connect(get_db()) as conn:
        if target.can_change == "Да":
            insert = "Нет"
        else:
            insert = "Да"

        await conn.execute(
            f"UPDATE rp_users SET can_change = '{insert}' WHERE user_id = {target.id}")

        await conn.commit()


async def castSkill(target: User, skill: Skill):
    query = f"UPDATE rp_characters SET mana = {target.active_character.mana - skill.manacost} WHERE character_id = {target.active_character.id}"
    if target.active_character.mana >= skill.manacost:
        async with aiosqlite.connect(get_db()) as conn:
            await conn.execute(query)
            await conn.commit()
            return "Каст заклинания успешен!"
    else:
        return "Каст заклинания провален из-за недостатка маны!"


async def superCommand(query: str):
    async with aiosqlite.connect(get_db()) as conn:
        async with conn.execute(query) as cursor:
            result = []
            while True:
                row = await cursor.fetchone()
                if not row: break
                result.append(row)
            await conn.commit()
            return result


async def changeMoney(target: User, value: float):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(f"UPDATE rp_characters SET money = {value} WHERE character_id = {target.active_character.id}")
        await conn.commit()


async def addItem(target: User, item):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(f"INSERT INTO inventory VALUES (NULL, {target.active_character.id}, '%s', '%s')" % (item.name, item.desc))
        await conn.commit()


async def dropItem(item):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(
            f"DELETE FROM inventory WHERE item_id = {item.id}")
        await conn.commit()


async def dropSkill(target: User, skill):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(
            f"DELETE FROM skillsets WHERE skill_id = {skill.id} AND skillset_id = {target.active_character.id}")
        await conn.commit()


async def getItemsOfCharacter(character: Character):
    async with aiosqlite.connect(get_db()) as conn:
        async with conn.execute(
            f"SELECT item_id, item_name, item_desc FROM inventory "
            f"WHERE character_id = {character.id}") as cursor:
                response = await cursor.fetchall()
                return response


async def log(target_char_id, author_id, action:str, log_desc: str):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(
            f"INSERT INTO logs VALUES (NULL, {author_id}, {target_char_id}, '{action}', '{log_desc}', '{str(datetime.now().time())[:-7]}', '{str(datetime.now().date())}')")
        await conn.commit()


async def grantMoney(target: User, value):
    async with aiosqlite.connect(get_db()) as conn:
        await conn.execute(f"UPDATE rp_characters SET money = '{value}' WHERE character_id = {target.active_character.id}")
        await conn.commit()


async def addSkillPoint(target: User, skill: Skill):
    skill.learn_progress += 1
    query = f"UPDATE skillsets SET learn_progress = {skill.learn_progress} WHERE skill_id = {skill.id}"
    async with aiosqlite.connect(get_db()) as conn:
        if skill.need_to_learn <= skill.learn_progress:
            skill.learned = "Да"
            query = f"UPDATE skillsets SET learned = 'Да' WHERE skill_id = {skill.id}"

        await conn.execute(query)
        await conn.commit()


async def setWorldTimeline(timeline: str) -> None:
    query = f"UPDATE environment SET value = '{timeline}' WHERE variable_id = 'world_time'"
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(query)
        await connection.commit()


async def webhookChange(target: User, webhook) -> None:
    query = f"""
    UPDATE webhooks 
    SET name = '%s',
        avatar_url = '%s',
        status = '%s'
    WHERE character_id = {target.active_character.id}
    """ % (webhook.name, webhook.avatar_url, webhook.status)
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(query)
        await connection.commit()


async def webhookGet(target_char_id: int):
    query = f"""
    SELECT * FROM webhooks 
    WHERE character_id = {target_char_id}
    """
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(query) as cursor:
            raw_data = await cursor.fetchone()
            return raw_data


async def createWebhook(webhook_id: int, channel_id: int):
    query = f"INSERT INTO hooks VALUES ({webhook_id}, {channel_id}, 'nobody')"
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(query)
        await connection.commit()


async def useWebhook(webhook_id: int, character_id: int, channel_id: int):
    query_for_check = f"SELECT * from hooks WHERE (hook_id = {webhook_id} and channel_id = {channel_id})"
    query = f"UPDATE hooks SET last_used_char_id = {character_id} WHERE (hook_id = {webhook_id} and channel_id = {channel_id})"
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(query_for_check) as cursor:
            result = await cursor.fetchone()
            if not result:
                await createWebhook(webhook_id, channel_id)
        await connection.execute(query)
        await connection.commit()


async def getLastUsed(webhook_id: int, channel_id: int):
    query = f"SELECT last_used_char_id FROM hooks WHERE (hook_id = {webhook_id} and channel_id = {channel_id})"
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(query) as cursor:
            character_id = (await cursor.fetchone())
            if not character_id: character_id = "nobody"
            else:
                character_id = character_id[0]
            if character_id == "nobody":
                character_id = 1
                last_used = await Character.Character.create(character_id)
                last_used.timeline = await getWorldTimeline()
                last_used.name = "Общий таймлайн"
            else:
                last_used = await Character.Character.create(character_id)
            return last_used


async def webhookMessageRegister(message_id, user_id):
    query = f"INSERT INTO logs VALUES ({message_id}, {user_id})"
    async with aiosqlite.connect(get_logs_db()) as connection:
        await connection.execute(query)
        await connection.commit()


async def webhookMessageCheck(message_id, user_id):
    query = f"SELECT user_id FROM logs WHERE message_id = {message_id}"
    async with aiosqlite.connect(get_logs_db()) as connection:
        async with connection.execute(query) as cursor:
            response = await cursor.fetchone()
            if not response:
                return False
            id = response[0]
            if user_id == id:
                return True
            else:
                return False


async def webhookMessageDelete(message_id):
    query = f"DELETE FROM logs WHERE message_id = {message_id}"
    async with aiosqlite.connect(get_logs_db()) as connection:
        await connection.execute(query)
        await connection.commit()


async def getMulticast(character):
    query = f"SELECT desc FROM logs WHERE (target_character_id = {character.id} and action = 'multicast')"
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(query) as cursor:
            response = await cursor.fetchall()
            return response


async def delMulticast(character):
    query = f"DELETE FROM logs WHERE (target_character_id = {character.id} and action = 'multicast')"
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(query)
        await connection.commit()


async def getSkillIdBySkillName(name):
    query = f"SELECT skill_id FROM skills WHERE title = '%s'" % name
    async with aiosqlite.connect(get_db()) as connection:
        async with connection.execute(query) as cursor:
            response = await cursor.fetchone()
            return response[0]


async def updateSkill(skill: Skill):
    query = f"""
            UPDATE skills SET 
                title = '%s',
                manacost = %i,
                skill_desc = '%s'
                WHERE skill_id = %i
            """ % (skill.title, skill.manacost, skill.desc, skill.id)
    async with aiosqlite.connect(get_db()) as connection:
        await connection.execute(query)
        await connection.commit()
