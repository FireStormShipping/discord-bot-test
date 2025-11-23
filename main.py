import logging
import os

from discord.utils import _ColourFormatter
from dotenv import load_dotenv

from bot import FireStormBot

logger = logging.getLogger("firestorm_bot")
log_handler = logging.StreamHandler()
log_handler.setFormatter(_ColourFormatter())
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    load_dotenv() # Load env variables from .env if it exists
    approved_roles = ["admin"]
    guild_id = int(os.environ.get('GUILD_ID', '1234'))
    bot_token = os.environ.get('BOT_TOKEN', 'default_token')
    bot = FireStormBot(guild_id, approved_roles)
    bot.run(bot_token)
