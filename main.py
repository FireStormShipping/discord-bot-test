import logging
import os

from discord.utils import _ColourFormatter
from dotenv import load_dotenv

from bot import FireStormBot
from db import Db

logger = logging.getLogger("firestorm_bot")
log_handler = logging.StreamHandler()
log_handler.setFormatter(_ColourFormatter())
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    # 1. Get all settings
    load_dotenv() # Load env variables from .env if it exists
    approved_roles = ["admin"]
    guild_id = int(os.environ.get('GUILD_ID', '1234'))
    bot_token = os.environ.get('BOT_TOKEN', 'default_token')
    db_password = os.environ.get('DB_PASSWORD', '1234')
    db_user = os.environ.get('DB_USER', 'user')
    db_host = os.environ.get('DB_HOST', '127.0.0.1')
    db_port = int(os.environ.get('DB_PORT', 3306))
    default_db_name = os.environ.get('DEFAULT_DB', 'bingo-dataset')

    db = Db(db_password, db_host, db_user, db_port, default_db_name)

    # 2. Initialize the bot and DB.
    bot = FireStormBot(guild_id, approved_roles, db)

    bot.run(bot_token)
