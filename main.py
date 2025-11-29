import logging
import os
import sys

import discord
from discord.utils import _ColourFormatter
from dotenv import load_dotenv

from bot import FireStormBot
from db import Db

logger = logging.getLogger("firestorm_bot")
log_handler = logging.StreamHandler()
log_handler.setFormatter(_ColourFormatter())
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

def convert_to_snowflake(item: str) -> discord.Object:
    return discord.Object(int(item))

if __name__ == "__main__":
    # 1. Get all settings
    load_dotenv() # Load env variables from .env if it exists
    approved_roles = os.environ.get('PRIVILEGED_ROLES', "admin")
    guild_ids = os.environ.get('GUILD_IDS', None)
    bot_token = os.environ.get('BOT_TOKEN', 'default_token')
    db_password = os.environ.get('DB_PASSWORD', '1234')
    db_user = os.environ.get('DB_USER', 'user')
    db_host = os.environ.get('DB_HOST', '127.0.0.1')
    db_port = int(os.environ.get('DB_PORT', 3306))
    default_db_name = os.environ.get('DEFAULT_DB', 'bingo-dataset')

    if guild_ids is None:
        logger.fatal("No guilds specified! Quitting!")
        sys.exit(1)

    # 2. Initialize the bot and DB.
    guild_list = list(map(convert_to_snowflake, guild_ids.split(',')))
    approved_roles = approved_roles.split(',')

    db = Db(db_password, db_host, db_user, db_port, default_db_name)
    bot = FireStormBot(guild_list, approved_roles, db)

    bot.run(bot_token)
