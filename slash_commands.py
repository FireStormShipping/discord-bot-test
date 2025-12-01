from typing import List, Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands

from db import Db

SENSITIVITY = Literal['S', 'E', 'Q']

class SlashCommands(commands.Cog):
    """
    Commands that can be called as `/<command>`.
    """

    def __init__(self, bot: commands.Bot, approved_roles: List[str], db: Db):
        """
        :param bot: discord bot
        :param approved_roles: Roles that are allowed to approve prompts
        """
        self.bot = bot
        self.approved_roles = approved_roles
        self.db = db

    ###################################################################################
    @app_commands.command(
        name="add-prompt",
        description="Submit a prompt for approval",
    )
    @app_commands.describe(
        pool="The pool to add the prompt to",
        prompt="The prompt to add to the pool",
        sensitivity="S/E/Q",
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
            error_msg = "DB failed to add prompt."

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
            await interaction.response.send_message(embed=embed)

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
            await interaction.response.send_message(f"❌ Failed to delete Prompt ID #{prompt_id}!")
        except PermissionError:
            await interaction.response.send_message(f"❌ Role is not allowed to delete approved prompt ID #{prompt_id}.")

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
                await interaction.response.send_message(f"❌ Failed to approve Prompt ID #{prompt_id}!")
            return
        await interaction.response.send_message(f"❌ Role is not allowed to approve prompt ID #{prompt_id}.")

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
                await interaction.response.send_message(f"✅ Prompt ID #{prompt_id} rejected!")
            else:
                await interaction.response.send_message(f"❌ Failed to reject Prompt ID #{prompt_id}!")
            return
        await interaction.response.send_message(f"❌ Role is not allowed to reject prompt ID #{prompt_id}.")

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
        output = f'[Pool: {pool}]\n'
        for entry in entries:
            output += f"#{entry.uid}, Pool: {entry.pool}, Prompt: {entry.prompt}, "
            output += f"Weight: {entry.weight}, {entry.sensitivity}"
            if entry.flags:
                output += f", Flags: {entry.flags}\n"
            else:
                output += "\n"
        # TODO: Return it as Pagination instead, as the pool might be very huge and exceed msg limit.
        await interaction.response.send_message(output)

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
