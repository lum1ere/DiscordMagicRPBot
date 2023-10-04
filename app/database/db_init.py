import aiosqlite
import app.database.db_queries as dq
from app import variables


async def create():
    table_queries = {
        'rp_users':
            """
            CREATE TABLE "rp_users" (
            "user_id" INTEGER NOT NULL,
            "name" TEXT NOT NULL,
            "active_character_id" INTEGER UNIQUE,
            "can_change" TEXT NOT NULL DEFAULT 'F',
            FOREIGN KEY("active_character_id") REFERENCES "rp_characters"("character_id") ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY("user_id")
            );
            """,
        'rp_characters':
            """
            CREATE TABLE "rp_characters" (
            "character_id" INTEGER NOT NULL UNIQUE,
            "user_id" INTEGER NOT NULL,
            "name" TEXT NOT NULL,
            "mana" REAL NOT NULL,
            "manapool" REAL NOT NULL,
            "rank_id" INTEGER NOT NULL,
            "core_progress_need" INTEGER NOT NULL,
            "core_progress_curent" INTEGER NOT NULL,
            "character_timeline" TEXT NOT NULL,
            "profile_edit" TEXT NOT NULL,
            "money" TEXT NOT NULL,
            PRIMARY KEY("character_id" AUTOINCREMENT)
            );
            """,
        'permissions':
            """
            CREATE TABLE "permissions" (
            "permission_id"	INTEGER NOT NULL UNIQUE,
            "permission_name" TEXT NOT NULL,
            "permission_level"	INTEGER NOT NULL,
            PRIMARY KEY("permission_id" AUTOINCREMENT)
            );
            """,
        'rules':
            """
            CREATE TABLE "rules" (
            "user_id" INTEGER NOT NULL UNIQUE,
            "permission_id"	INTEGER NOT NULL,
            PRIMARY KEY("user_id"),
            FOREIGN KEY("permission_id") REFERENCES "permissions"("permission_id") ON UPDATE CASCADE ON DELETE CASCADE
            )
            """,
        'ranks':
            """
            CREATE TABLE "ranks" (
            "rank_id" INTEGER NOT NULL UNIQUE,
            "name" TEXT NOT NULL,
            "standart_manapool"	INTEGER NOT NULL,
            PRIMARY KEY("rank_id" AUTOINCREMENT)
            );
            """,
        'elements':
            """
            CREATE TABLE "elements" (
            "element_id" INTEGER NOT NULL UNIQUE,
            "name" TEXT NOT NULL,
            PRIMARY KEY("element_id" AUTOINCREMENT)
            )
            """,
        'skills':
            """
            CREATE TABLE "skills" (
            "skill_id" INTEGER NOT NULL UNIQUE,
            "title" TEXT,
            "manacost" INTEGER,
            "need_to_learn" INTEGER,
            "element_id" INTEGER,
            "skill_desc" TEXT,
            "required_rank_id" INTEGER,
            FOREIGN KEY("element_id") REFERENCES "elements"("element_id") ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY("required_rank_id") REFERENCES "ranks"("rank_id") ON UPDATE CASCADE ON DELETE CASCADE,
            PRIMARY KEY("skill_id" AUTOINCREMENT)
            );
            """,
        'skillsets':
            """
           CREATE TABLE "skillsets" (
           "id"	INTEGER NOT NULL,
           "skillset_id" INTEGER NOT NULL,
           "skill_id" INTEGER,
           "learned" TEXT NOT NULL DEFAULT 'F',
           "learn_progress"	INTEGER,
           FOREIGN KEY("skillset_id") REFERENCES "characters_lists"("skillset_id") ON UPDATE CASCADE ON DELETE CASCADE,
           FOREIGN KEY("skill_id") REFERENCES "skills"("skill_id") ON DELETE CASCADE ON UPDATE CASCADE,
           PRIMARY KEY("id" AUTOINCREMENT)
           )
            """,
        'character_list':
            """
            CREATE TABLE "characters_lists" (
            "character_id" INTEGER NOT NULL,
            "skillset_id" INTEGER NOT NULL,
            "core_id" INTEGER NOT NULL,
            FOREIGN KEY("character_id") REFERENCES "rp_characters"("character_id") ON UPDATE CASCADE ON DELETE CASCADE,
            PRIMARY KEY("character_id")
            );
            """,
        'core_types':
            """
            CREATE TABLE "core_types" (
               "core_id" INTEGER NOT NULL,
               "type" TEXT NOT NULL,
               FOREIGN KEY("core_id") REFERENCES "characters_lists"("core_id") ON UPDATE CASCADE ON DELETE CASCADE,
               PRIMARY KEY("core_id")
               );
            """,
        'core_affinities':
            """
            CREATE TABLE "core_affinities" (
            "id" INTEGER NOT NULL,
            "core_id" INTEGER NOT NULL,
            "element_id" INTEGER NOT NULL,
            "affinity_level" TEXT NOT NULL,
            FOREIGN KEY("element_id") REFERENCES "elements"("element_id") ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY("core_id") REFERENCES "characters_lists"("core_id") ON DELETE CASCADE ON UPDATE CASCADE,
            PRIMARY KEY("id" AUTOINCREMENT)
            );
            """,
        'discord_settings':
            """
            CREATE TABLE "discord_settings" (
            "status" TEXT NOT NULL,
            "text_status" TEXT
            )
            """,
        'environment':
            """
            CREATE TABLE "environment" (
            "variable_id" TEXT NOT NULL,
            "value"	TEXT NOT NULL,
            PRIMARY KEY("variable_id")
            );
            """,
        'logs':
            """
            CREATE TABLE "logs" (
            "action_id"	INTEGER NOT NULL,
            "author_id"	INTEGER NOT NULL,
            "target_character_id" INTEGER NOT NULL,
            "action" TEXT NOT NULL,
            "desc" TEXT,
            "action_date" TEXT NOT NULL,
            "action_time" TEXT NOT NULL,
            PRIMARY KEY("action_id" AUTOINCREMENT),
            FOREIGN KEY("target_character_id") REFERENCES "rp_characters"("character_id") ON DELETE CASCADE ON UPDATE CASCADE
            )
            """,
        'profiles':
            """
            CREATE TABLE "profiles" (
               "character_id" INTEGER NOT NULL,
               "short_desc"	TEXT,
               "field_1" TEXT,
               "field_2" TEXT,
               "field_3" TEXT,
               "mutations"	TEXT,
               "extra_field_1" TEXT,
               "extra_field_2" TEXT,
               "extra_field_3" TEXT,
               "extra_field_4" TEXT,
               PRIMARY KEY("character_id"),
               FOREIGN KEY("character_id") REFERENCES "rp_characters"("character_id") ON DELETE CASCADE ON UPDATE CASCADE
                );
            """,
        'inventory':
            """
            CREATE TABLE "inventory" (
            "item_id" INTEGER NOT NULL,
            "character_id" INTEGER NOT NULL,
            "item_name"	TEXT,
            "item_desc"	TEXT,
            FOREIGN KEY("character_id") REFERENCES "rp_characters"("character_id") ON UPDATE CASCADE ON DELETE CASCADE,
            PRIMARY KEY("item_id" AUTOINCREMENT)
            );
            """,
        'webhooks':
            """
            CREATE TABLE "webhooks" (
            "id" INTEGER NOT NULL,
            "character_id" INTEGER NOT NULL,
            "name" TEXT NOT NULL,
            "avatar_url" TEXT,
            "status" TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT),
            FOREIGN KEY("character_id") REFERENCES "rp_characters"("character_id") ON DELETE CASCADE ON UPDATE CASCADE
            );
            """,
        'hooks':
            """
            CREATE TABLE "hooks" (
            "hook_id" INTEGER NOT NULL,
            "channel_id" INTEGER NOT NULL,
            "last_used_char_id"	INTEGER NOT NULL,
            PRIMARY KEY("hook_id", "channel_id")
            );
            """
    }
    async with aiosqlite.connect(variables.get_db()) as connection:
        queries = [dq.customQueryWrite(connection, query=table_queries[key]) for key in table_queries]
        for query in queries:
            await query


async def primary_insert():
    standart_ranks = [
        ("'Неофит'", 8),
        ("'Ученик'", 30),
        ("'Маг'", 120),
        ("'Почетный маг'", 300),
        ("'Магистр'", 1000),
        ("'Архимаг'", 3840),
        ("'Полубог'", 20000)
    ]
    standart_permissons = [
        ("'superadmin'", 0),
        ("'admin'", 1),
        ("'gm'", 2),
        ("'player'", 3),
        ("'noname'", 4)
    ]

    standart_elements = [
        ("'огонь'",), ("'вода'",),
        ("'лёд'",), ("'воздух'",), ("'земля'",),
        ("'металл'",), ("'молния'",),
        ("'свет'",), ("'тьма'",),
        ("'смерть'",),
        ("'жизнь'",),
        ("'хаос'",),
        ("'разум'",),
        ("'астрал'",),
        ("'артефакторика'",), ("'рунология'",), ("'магия проклятий'",),
        ("'магия усиления'",), ("'трансмутация'",),
        ("'големантия'",), ("'химерология'",), ("'алхимия'",),
        ("'время'",), ("'судьба'",), ("'пространство'",),
        ("'аркана'",), ("'гравитация'",), ("'кинетика'",),
        ("'онейромантия'",), ("'базовый'",), ("'кошмар'",)
    ]

    triggers = [
        """
        CREATE TRIGGER restore_mana_trigger
        AFTER UPDATE ON rp_characters
        FOR EACH ROW
        WHEN NEW.mana > NEW.manapool
        BEGIN
            UPDATE rp_characters
            SET mana = NEW.manapool
            WHERE character_id = NEW.character_id;
        END;
        """,
        """
               CREATE TRIGGER money_change_trigger
               AFTER UPDATE ON rp_characters
               FOR EACH ROW
               WHEN NEW.money < 0
               BEGIN
                   UPDATE rp_characters
                   SET money = 0
                   WHERE character_id = NEW.character_id;
               END;
               """
    ]

    async with aiosqlite.connect(variables.get_db()) as connection:
        queries_list = [
            [dq.customQueryWrite(connection, f'''INSERT INTO elements VALUES (NULL, {element[0]})''') for element in
             standart_elements],

            [dq.customQueryWrite(connection, f'''INSERT INTO permissions VALUES (NULL, {permission[0]}, {permission[1]})''')
             for permission in standart_permissons],

            [dq.customQueryWrite(connection, f'''INSERT INTO ranks VALUES (NULL, {rank[0]}, {rank[1]})''') for rank in
             standart_ranks],

            [dq.customQueryWrite(connection, f"INSERT INTO rp_users VALUES (391660784041852929, 'mentalism', NULL, 'Да')")],
            [dq.customQueryWrite(connection, f"INSERT INTO rules VALUES (391660784041852929, 1)")],

            [dq.customQueryWrite(connection, f"INSERT INTO environment VALUES ('world_time', '0d 00:00:00')")],
            [dq.customQueryWrite(connection, f"INSERT INTO discord_settings VALUES (%s, %s)" % variables.get_settings())],
            [dq.customQueryWrite(connection, trigger) for trigger in triggers],
        ]
        for queries in queries_list:
            for query in queries:
                await query
        await connection.commit()


async def create_messages():
    async with aiosqlite.connect(variables.get_logs_db()) as conn:
        queries = [
            """
                CREATE TABLE "logs" (
                "message_id" INTEGER NOT NULL,
                "user_id" INTEGER NOT NULL
                );
            """
            ]

        [await conn.execute(query) for query in queries]
        await conn.commit()

