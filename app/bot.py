import asyncio
import logging
from typing import List

import discord
from discord.errors import Forbidden, RateLimited
from discord.ext import commands

from .db import Db
from .git import GitWrapper
from .slash_commands import SlashCommands

logger = logging.getLogger("firestorm_bot")

def convert_to_snowflake(item: int) -> discord.Object:
    return discord.Object(item)

class FireStormBot(commands.Bot):
    """
    Main Entrypoint for the Discord Bot
    """

    def __init__(
        self,
        guilds: List[int],
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
        guild_list = list(map(convert_to_snowflake, self._guilds))
        # Add commands only for specific guilds.
        await self.add_cog(
            SlashCommands(self, self._approved_roles, self._db, self._git_wrapper),
            guilds=guild_list
        )
        # Sync commands to guild immediately (if not it will take an hour)
        for guild in guild_list:
            try:
                await self.tree.sync(guild=guild)
            except Forbidden:
                logger.warning(f"[Forbidden] Skipping sync to guild {guild}")
            except RateLimited as e:
                logger.info("Rate limit reached, trying again after sleeping...")
                await asyncio.sleep(e.retry_after)
                await self.tree.sync(guild=guild)
            except Exception as e: # pylint: disable=broad-exception-caught
                logger.warning(f"[Unknown Error] Skipping sync to guild {guild}: {e}")
        logger.info("App commands loaded and synced!")

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"[on_guild_joined] Bot joined {guild.name} ({guild.id})")

        if guild.id in self._guilds:
            await self.tree.sync(guild=convert_to_snowflake(guild.id))
            logger.info(f"[on_guild_joined] App commands synced to {guild.id}")
        else:
            logger.info(f"[on_guild_joined] {guild.id} rejected!")

    async def on_ready(self):
        logger.info(f"{self.user} is now running!")
