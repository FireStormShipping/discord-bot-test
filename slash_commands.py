from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from db import Db


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
        weight="Weight of the Prompt",
        sensitivity="S/E/Q",
        flags="Categories"
    )
    async def add_prompt(self,
        interaction: discord.Interaction,
        pool: str,
        prompt: str,
        weight: int,
        sensitivity: str,
        flags: str
    ):
        error_msg = None
        uid = -1
        # Perform some pre-checks
        if sensitivity not in ['S', 'E', 'Q']:
            error_msg = "Sensitivity must be one of 'S', 'E' or 'Q'."
        else:
            uid = self.db.add_prompt(pool, prompt, weight, sensitivity, flags)
            if uid < 0:
                error_msg = "DB failed to add prompt."

        embed = None
        if error_msg is not None:
            embed = discord.Embed(
                title = "Error Encountered!",
                description = error_msg,
                color = discord.Color.red()
            )
            embed.set_footer(text="Error encountered.")
        else:
            embed = discord.Embed(
                title=f"#ID: {uid}",
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
    @app_commands.describe(prompt_id="The ID of the prompt to modify.")
    async def modify_prompt(self, interaction: discord.Interaction, prompt_id: int):
        """
        Modify a prompt.
        Approved prompts can only be modified by specific roles.
        Unapproved prompts can be modified by anyone.
        """
        print(f"ID: {prompt_id}")
        # TODO: remove the un-approved prompt from memory or delete from db
        await interaction.response.send_message(f"Prompt deleted, ID: {prompt_id}")

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
        print(f"ID: {prompt_id}")
        # TODO: remove the un-approved prompt from memory or delete from db
        await interaction.response.send_message(f"Prompt deleted, ID: {prompt_id}")

    ###################################################################################
    @app_commands.command(
        name="approve-prompt",
        description="Approve Prompt Command",
    )
    @app_commands.describe(prompt_id="The ID of the unapproved prompt to approve")
    async def approve_prompt(self, interaction: discord.Interaction, prompt_id: int):
        """
        Allow certain roles to approve the prompt.
        """
        user_roles = interaction.user.roles
        for role in user_roles:
            if role.name in self.approved_roles:
                await interaction.response.send_message(f"Prompt ID #{prompt_id} approved!")
                # TODO: when prompt is approved, add it to the database?
                # Or alternatively in DB has a column for APPROVED = y/n, then flip it.
                return
        await interaction.response.send_message("Role is not allowed to approve prompt.")

    ###################################################################################
    @app_commands.command(
        name="show-pool",
        description="Show current entries in a specified pool. Only approved entries will show up.",
    )
    @app_commands.describe(pool="The name of the pool to show.")
    async def show_pool(self, interaction: discord.Interaction, pool: str):
        """
        Given a pool name, show all the current entries in this pool.
        """
        entries = self.db.show_pool(pool)
        if len(entries) == 0:
            await interaction.response.send_message("No such pool!")
        output = f'[Pool: {pool}]\n'
        for entry in entries:
            output += f"#{entry.uid}, Pool: {entry.pool}, Prompt: {entry.prompt}, "
            output += f"Weight: {entry.weight}, {entry.sensitivity}, {entry.flags}\n"
        # TODO: Return it as text file instead, as the pool might be very huge and exceed msg limit.
        await interaction.response.send_message(output)

    ###################################################################################
    @app_commands.command(
        name="list-pools",
        description="Shows all the currently available pools.",
    )
    async def list_pools(self, interaction: discord.Interaction):
        """
        Show all the available pools.
        """
        pools = self.db.get_pools()
        await interaction.response.send_message(','.join(pools))

    ###################################################################################
    @app_commands.command(
        name="pending-prompts",
        description="Show all the current prompts that are pending approval.",
    )
    async def pending_prompts(self, interaction: discord.Interaction):
        """
        Show all the current prompts that are pending approval.
        """
        pending_prompts = self.db.get_pending_prompts()
        output = ''
        for entry in pending_prompts:
            output += f"#{entry.uid}, Pool: {entry.pool}, Prompt: {entry.prompt}, "
            output += f"Weight: {entry.weight}, {entry.sensitivity}, {entry.flags}\n"
        await interaction.response.send_message(output)