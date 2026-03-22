import json
import logging
import os
from pathlib import Path
from typing import List, Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands

from .app_types import ERROR_ENTRY_EXISTS, ERROR_MARIA_DB
from .dataset_encoder import JsonEncoder, TableEncoder
from .db import Db
from .git import GitWrapper

logger = logging.getLogger("firestorm_bot")

SENSITIVITY = Literal['S', 'E', 'Q']

class SlashCommands(commands.Cog):
    """
    Commands that can be called as `/<command>`.
    """

    def __init__(
        self,
        bot: commands.Bot,
        approved_roles: List[str],
        db: Db,
        git_wrapper: GitWrapper
    ):
        """
        :param bot: discord bot
        :param approved_roles: Roles that are allowed to approve prompts
        :param db: DB instance
        :param git_wrapper: Git wrapper for git operations
        """
        self.bot = bot
        self.approved_roles = approved_roles
        self.db = db
        self.git = git_wrapper

    ###################################################################################
    @app_commands.command(
        name="add-prompt",
        description="Submit a prompt for approval",
    )
    @app_commands.describe(
        pool="The pool to add the prompt to",
        prompt="The prompt to add to the pool",
        sensitivity="Safe/Explicit/Questionable",
        weight="Weight of the Prompt. Default value depends on sensitivity",
        flags="Categories (Comma-separated string)"
    )
    async def add_prompt(self,
        interaction: discord.Interaction,
        pool: str,
        prompt: str,
        sensitivity: SENSITIVITY,
        weight: Optional[int],
        flags: Optional[str]
    ) -> None:
        error_msg = None
        uid = -1
        # Perform some pre-checks
        pool = pool.strip()
        prompt = prompt.strip()
        if weight is None:
            if sensitivity == 'S':
                weight = 1
            if sensitivity == 'E':
                weight = 2
            if sensitivity == 'Q':
                weight = 3
        if flags is None:
            flags = ''
        flags = flags.strip()
        uid = self.db.add_prompt(pool, prompt, weight, sensitivity, flags)
        if uid < 0:
            if uid == ERROR_MARIA_DB:
                error_msg = "DB failed to add prompt."
            elif uid == ERROR_ENTRY_EXISTS:
                error_msg = "Prompt already exists in this pool."
            else:
                error_msg = "Unknown DB error."

        embed = None
        if error_msg is not None:
            embed = discord.Embed(
                title = "Error adding prompt!",
                description = error_msg,
                color = discord.Color.red()
            )
            embed.set_footer(text="Error encountered.")
        else:
            embed = discord.Embed(
                title=f"Prompt ID: #{uid}",
                description="Prompt Received!",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Prompt will be added to pool after approval.")
        embed.add_field(name="Pool", value=pool, inline=True)
        embed.add_field(name="Prompt", value=prompt, inline=True)
        embed.add_field(name="Weight", value=weight, inline=True)
        embed.add_field(name="Sensitivity", value=sensitivity, inline=True)
        embed.add_field(name="Flags", value=flags, inline=False)

        await interaction.response.send_message(embed=embed)

    ###################################################################################
    @app_commands.command(
        name="modify-prompt",
        description="Modify a prompt.",
    )
    @app_commands.describe(
        prompt_id="The ID of the prompt to modify",
        prompt="Modify the prompt string",
        weight="Modify the prompt weight",
        sensitivity="Modify the prompt sensitivity",
        flags="Modify the prompt flags"
    )
    async def modify_prompt(
        self,
        interaction: discord.Interaction,
        prompt_id: int,
        prompt: Optional[str],
        weight: Optional[int],
        sensitivity: Optional[SENSITIVITY],
        flags: Optional[str]
    ) -> None:
        """
        Modify a prompt.
        Approved prompts can only be modified by specific roles.
        Unapproved prompts can be modified by anyone.
        """
        # Construct summary of modifications requested
        modifications = "Modifications: "
        if prompt:
            modifications += f"prompt: {prompt}, "
        if weight:
            modifications += f"weight: {weight}, "
        if sensitivity:
            modifications += f"sensitivity: {sensitivity}, "
        if flags:
            modifications += f"flags: {flags}"
        # strip trailing whitespace and ,
        modifications = modifications.strip(", ")

        try:
            error_msg = None
            # Perform some pre-checks
            if prompt:
                prompt = prompt.strip()
            if flags:
                flags = flags.strip()
            updated_entry = self.db.modify_prompt(
                prompt_id,
                self._is_privileged_role(interaction),
                prompt,
                weight,
                sensitivity,
                flags
            )
            if updated_entry is None:
                error_msg = "DB failed to modify prompt."

            # Construct the embed
            embed = None
            if error_msg is not None:
                embed = discord.Embed(
                    title = f"Failed to update Prompt ID #{prompt_id}!",
                    description = modifications,
                    color = discord.Color.red()
                )
                embed.set_footer(text=error_msg)
            else:
                embed = discord.Embed(
                    title=f"Updated Prompt ID #{prompt_id}",
                    description=modifications,
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Prompt successfully modified.")
                embed.add_field(name="Pool", value=updated_entry.pool, inline=True)
                embed.add_field(name="Prompt", value=updated_entry.prompt, inline=True)
                embed.add_field(name="Weight", value=updated_entry.weight, inline=True)
                embed.add_field(name="Sensitivity", value=updated_entry.sensitivity, inline=True)
                embed.add_field(name="Flags", value=updated_entry.flags, inline=False)
                embed.add_field(name="Approved?", value=updated_entry.approved, inline=False)
            await interaction.response.send_message(embed=embed)
        except PermissionError:
            embed = discord.Embed(
                title = f"Role cannot update Prompt ID #{prompt_id}!",
                description = modifications,
                color = discord.Color.red()
            )
            embed.set_footer(text="❌ Role is not allowed to modify approved prompt.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    ###################################################################################
    @app_commands.command(
        name="delete-prompt",
        description="Delete a prompt (can be approved or unapproved).",
    )
    @app_commands.describe(prompt_id="The ID of the prompt to delete")
    async def delete_prompt(self, interaction: discord.Interaction, prompt_id: int):
        """
        Delete a prompt.
        Approved prompts can only be deleted by specific roles.
        Unapproved prompts can be deleted by anyone.
        """
        try:
            if self.db.delete_prompt(prompt_id, self._is_privileged_role(interaction)):
                await interaction.response.send_message(f"✅ Prompt ID #{prompt_id} deleted!")
                return
            await interaction.response.send_message(
                f"❌ Unknown error, failed to delete Prompt ID #{prompt_id}!"
            )
        except PermissionError:
            await interaction.response.send_message(
                f"❌ Role is not allowed to delete approved prompt ID #{prompt_id}.",
                ephemeral=True
            )

    ###################################################################################
    @app_commands.command(
        name="approve-prompt",
        description="Approve Prompt Command",
    )
    @app_commands.describe(prompt_id="The ID of the unapproved prompt to approve")
    async def approve_prompt(self, interaction: discord.Interaction, prompt_id: int) -> None:
        """
        Allow only certain roles to approve the prompt.
        """
        if self._is_privileged_role(interaction):
            if self.db.approve_prompt(prompt_id):
                await interaction.response.send_message(f"✅ Prompt ID #{prompt_id} approved!")
            else:
                await interaction.response.send_message(f"❌ Unknown error, failed to approve Prompt ID #{prompt_id}!")
            return
        await interaction.response.send_message(
            f"❌ Role is not allowed to approve prompt ID #{prompt_id}.",
            ephemeral=True
        )

    ###################################################################################
    @app_commands.command(
        name="reject-prompt",
        description="Reject Prompt Command",
    )
    @app_commands.describe(
        prompt_id="The ID of the unapproved prompt to reject",
        reason="Reason for rejecting prompt"
    )
    async def reject_prompt(self, interaction: discord.Interaction, prompt_id: int, reason: str) -> None:
        """
        Allow only certain roles to reject the prompt.
        """
        if self._is_privileged_role(interaction):
            if self.db.reject_prompt(prompt_id, reason):
                await interaction.response.send_message(f"✅ Prompt ID #{prompt_id} rejected, Reason: {reason}")
            else:
                await interaction.response.send_message(f"❌ Unknown error, failed to reject Prompt ID #{prompt_id}!")
            return
        await interaction.response.send_message(
            f"❌ Role is not allowed to reject prompt ID #{prompt_id}.",
            ephemeral=True
        )

    ###################################################################################
    @app_commands.command(
        name="show-pool",
        description="Show current entries in a specified pool. Only approved entries will show up.",
    )
    @app_commands.describe(pool="The name of the pool to show")
    async def show_pool(self, interaction: discord.Interaction, pool: str) -> None:
        """
        Given a pool name, show all the current entries in this pool.
        """
        pool = pool.strip()
        entries = self.db.show_pool(pool)
        if len(entries) == 0:
            pools = self.db.get_pools()
            msg = f"❌ Pool `{pool}` does not exist!\n"
            if len(pools) == 0:
                msg += "There are no existing pools.\n"
            else:
                msg += "Existing pools: " + ', '.join(pools)
                msg += "\n"
            msg += "To make a new pool:\n"
            msg += "1) Add a prompt with /add-prompt.\n"
            msg += "2) Someone with the correct role needs to /approve-prompt.\n"
            msg += "3) Now /show-pool will show the new pool with prompts."
            await interaction.response.send_message(msg)
            return
        # Generate a temporary file to store the pool data
        enc = TableEncoder()
        pool_file = f"/tmp/tmp/{pool.replace(" ", "_")}.txt"
        path = Path(pool_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(enc.get_header_pretty())
            for entry in entries:
                f.write(enc.encode(entry))
        # Send the file as response
        await interaction.response.send_message(file=discord.File(pool_file))
        # Delete the temporary file
        os.remove(pool_file)

    ###################################################################################
    @app_commands.command(
        name="list-pools",
        description="Shows all the currently available pools.",
    )
    async def list_pools(self, interaction: discord.Interaction) -> None:
        """
        Show all the available pools.
        """
        pools = self.db.get_pools()
        msg = "Existing pools: "
        if len(pools) == 0:
            msg += "There are no existing pools.\n"
            msg += "To make a new pool:\n"
            msg += "1) Add a prompt with /add-prompt.\n"
            msg += "2) Someone with the correct role needs to /approve-prompt.\n"
            msg += "3) Now /list-pools will show the newly created pool."
        else:
            msg += ', '.join(pools)
        await interaction.response.send_message(msg)

    ###################################################################################
    @app_commands.command(
        name="pending-prompts",
        description="Show all the current prompts that are pending approval.",
    )
    async def pending_prompts(self, interaction: discord.Interaction) -> None:
        """
        Show all the current prompts that are pending approval.
        """
        pending_prompts = self.db.get_pending_prompts()
        output = ''
        for entry in pending_prompts:
            output += f"#{entry.uid}, Pool: {entry.pool}, Prompt: {entry.prompt}, "
            output += f"Weight: {entry.weight}, {entry.sensitivity}"
            if entry.flags:
                output += f", Flags: {entry.flags}\n"
            else:
                output += "\n"
        if output == '':
            await interaction.response.send_message("No pending prompts.")
        else:
            await interaction.response.send_message(output)

    ###################################################################################
    @app_commands.command(
        name="rejected-prompts",
        description="Show all the rejected prompts.",
    )
    async def rejected_prompts(self, interaction: discord.Interaction) -> None:
        """
        Show all the rejected prompts.
        """
        rejected_prompts = self.db.get_rejected_prompts()
        output = ''
        for entry in rejected_prompts:
            output += f"#{entry.uid}, Pool: {entry.pool}, Prompt: {entry.prompt}, "
            output += f"{entry.sensitivity}, Flags: {entry.flags}, "
            output += f"Rejection Reason: {entry.rejection_reason}\n"
        await interaction.response.send_message(output)

    ###################################################################################
    @app_commands.command(
        name="sync-dataset",
        description="Sync the latest dataset from DB to Github.",
    )
    async def sync_dataset(self, interaction: discord.Interaction) -> None:
        """
        Grabs the latest dataset from the DB, convert them to JSON files,
        and make a pull-request to firestorm-bingo.
        """
        if self._is_privileged_role(interaction):
            try:
                pr_url = self._sync_dataset_internal()
                await interaction.response.send_message(
                    f"✅ Dataset successfully synced: {pr_url}"
                )
            except Exception as e: # pylint: disable=broad-exception-caught
                await interaction.response.send_message(
                    f"❌ Error occurred: {e}"
                )
        else:
            await interaction.response.send_message(
                "❌ Role is not allowed to sync the dataset!",
                ephemeral=True
            )

    ###################################################################################
    @app_commands.command(
        name="help",
        description="How to use this bot.",
    )
    async def display_help(self, interaction: discord.Interaction) -> None:
        """
        Display basic info about how to use this bot.
        """
        output = "**How to use this bot**\n"
        output += "1. Use `/list-pools` to view a list of available pools/datasets.\n"
        output += "2. To view current entries in a pool, use `/show-pool`.\n"
        output += "3. Use `/add-prompt` to add a new prompt to a pool.\n"
        output += "4. Wait for allowed roles to `/approve-prompt`.\n"
        output += "5. Tada! That's all!"
        await interaction.response.send_message(output, ephemeral=True)

    ###################################################################################
    # Internal functions
    ###################################################################################
    def _is_privileged_role(self, interaction: discord.Interaction) -> bool:
        """
        Checks if user has an approved role or not.
        """
        user_roles = interaction.user.roles
        for role in user_roles:
            if role.name in self.approved_roles:
                return True
        return False

    def _sync_dataset_internal(self) -> str | Exception:
        """Returns the URL for the PR."""
        try:
            # 1. Sync upstream to forked repo
            logger.info("[sync-dataset-internal] Syncing upstream to fork.")
            self.git.sync_forked_repo_with_upstream()
            # 2. Clone fresh copy of the forked repo for sanity
            logger.info("[sync-dataset-internal] Closing fresh copy of forked repo.")
            repo = self.git.clone_fresh()
            # 3. Get all avail pools
            pools = self.db.get_pools()
            local_folder = f"{self.git.get_local_path()}/app/datasets"
            # 4. For each pool, process their entries.
            logger.info("[sync-dataset-internal] Writing pools to files.")
            for pool in pools:
                entries = self.db.show_pool(pool)
                pool_filename = f"{pool.replace(" ", "_")}.json"
                entries_json = []
                for entry in entries:
                    enc = JsonEncoder()
                    entries_json.append(enc.encode(entry))
                final_json = {
                    "entries": entries_json
                }
                # 5. Write pool to json file where the repo is locally.
                fullpath = f"{local_folder}/{pool_filename}"
                with open(fullpath, "w", encoding="utf-8") as f:
                    f.write(json.dumps(final_json, indent=2))
            # 6. Commit the changes
            logger.info("[sync-dataset-internal] Committing changes.")
            self.git.commit_changes(repo)
            # 7. Update the fork on remote
            logger.info("[sync-dataset-internal] Pushing to fork.")
            self.git.push_to_remote(repo)
            # 8. Make Pull Request, return PR URL.
            return self.git.make_pull_request()
        except Exception as e: # pylint: disable=broad-exception-caught
            raise e
