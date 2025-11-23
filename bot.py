import logging
from typing import List

import discord
from discord.ext import commands

from slash_commands import SlashCommands

logger = logging.getLogger("firestorm_bot")

class FireStormBot(commands.Bot):
    """
    Main Entrypoint for the Discord Bot
    """

    def __init__(self, guild_id: int, approved_roles: List[str]):
        """
        :param guild_id: guild id to sync commands to
        :param approved_roles: Roles that are allowed to approve prompts
        """
        intents2 = discord.Intents.default()
        intents2.message_content = True
        super().__init__(command_prefix="!", intents=intents2)
        self._guild_id = discord.Object(guild_id)
        self._approved_roles = approved_roles

    async def setup_hook(self):
        await self.add_cog(SlashCommands(self, self._approved_roles),  guild=self._guild_id)
        # Note: if guild_id not specified, may take up to an hour to sync.
        await self.tree.sync(guild=self._guild_id)
        logger.info("App commands loaded and synced!")

    async def on_ready(self):
        logger.info(f"{self.user} is now running!")
