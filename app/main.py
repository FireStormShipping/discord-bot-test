import logging
import os
import sys

from discord.utils import _ColourFormatter
from dotenv import load_dotenv

from .bot import FireStormBot
from .db import Db
from .git import GitWrapper

logger = logging.getLogger("firestorm_bot")
log_handler = logging.StreamHandler()
log_handler.setFormatter(_ColourFormatter())
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    # 1. Get all settings
    logger.info("Initializing environment...")
    load_dotenv() # Load env variables from .env if it exists
    approved_roles = os.environ.get('PRIVILEGED_ROLES', "admin")
    guild_ids = os.environ.get('GUILD_IDS', None)
    bot_token = os.environ.get('BOT_TOKEN', 'default_token')
    db_password = os.environ.get('DB_PASSWORD', '1234')
    db_user = os.environ.get('DB_USER', 'user')
    db_host = os.environ.get('DB_HOST', '127.0.0.1')
    db_port = int(os.environ.get('DB_PORT', 3306))
    default_db_name = os.environ.get('DEFAULT_DB', 'bingo-dataset')
    # git settings
    upstream_repo = os.environ.get('BINGO_REPO_NAME', 'FireStormShipping/firestorm-bingo')
    forked_repo = os.environ.get('FORKED_REPO_NAME', 'example-user/example-repo')
    git_user = forked_repo.split('/')[0]
    git_token = os.environ.get('GITHUB_TOKEN', 'None')
    local_repo_path = os.environ.get('LOCAL_REPO_PATH', '/tmp/firestorm-bingo')

    if guild_ids is None:
        logger.fatal("No guilds specified! Quitting!")
        sys.exit(1)

    # 2. Initialize git, db and bot.
    guild_list = [ int(id.strip(' ')) for id in guild_ids.split(',') ]
    approved_roles = [ r.strip(' ') for r in approved_roles.split(',') ]

    db = Db(db_password, db_host, db_user, db_port, default_db_name)
    git_wrapper = GitWrapper(git_user, git_token, upstream_repo, forked_repo, local_repo_path)
    bot = FireStormBot(guild_list, approved_roles, db, git_wrapper)

    bot.run(bot_token)
