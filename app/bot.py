import logging
from typing import List

import discord
from discord.errors import Forbidden
from discord.ext import commands

from .db import Db
from .git import GitWrapper
from .slash_commands import SlashCommands

logger = logging.getLogger("firestorm_bot")

class FireStormBot(commands.Bot):
    """
    Main Entrypoint for the Discord Bot
    """

    def __init__(
        self,
        guilds: List[discord.Object],
        approved_roles: List[str],
        db: Db,
        git_wrapper: GitWrapper
    ):
        """
        :param guilds: List of guild ids to sync commands to
        :param approved_roles: Roles that are allowed to approve prompts
        :param db: DB to use for the dataset storage
        :param git_wrapper: Git wrapper for git operations
        """
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self._guilds = guilds
        self._approved_roles = approved_roles
        self._db = db
        self._git_wrapper = git_wrapper

    async def setup_hook(self):
        # Add commands only for specific guilds.
        await self.add_cog(
            SlashCommands(self, self._approved_roles, self._db, self._git_wrapper),
            guilds=self._guilds
        )
        # Sync commands to guild immediately (if not it will take an hour)
        for guild in self._guilds:
            try:
                await self.tree.sync(guild=guild)
            except Forbidden:
                logger.warning(f"[Forbidden] Skipping sync to guild {guild}")
            except Exception as e: # pylint: disable=broad-exception-caught
                logger.warning(f"[Unknown Error] Skipping sync to guild {guild}: {e}")
        logger.info("App commands loaded and synced!")

    async def on_ready(self):
        logger.info(f"{self.user} is now running!")
