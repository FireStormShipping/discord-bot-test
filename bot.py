import logging
from typing import List

import discord
from discord.ext import commands

from db import Db
from slash_commands import SlashCommands

logger = logging.getLogger("firestorm_bot")

class FireStormBot(commands.Bot):
    """
    Main Entrypoint for the Discord Bot
    """

    def __init__(self, guilds: List[discord.Object], approved_roles: List[str], db: Db):
        """
        :param guilds: List of guild ids to sync commands to
        :param approved_roles: Roles that are allowed to approve prompts
        :param db: DB to use for the dataset storage
        """
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self._guilds = guilds
        self._approved_roles = approved_roles
        self._db = db

    async def setup_hook(self):
        # Add commands only for specific guilds.
        await self.add_cog(SlashCommands(self, self._approved_roles, self._db),  guilds=self._guilds)
        # Sync commands to guild immediately (if not it will take an hour)
        for guild in self._guilds:
            await self.tree.sync(guild=guild)
        logger.info("App commands loaded and synced!")

    async def on_ready(self):
        logger.info(f"{self.user} is now running!")
