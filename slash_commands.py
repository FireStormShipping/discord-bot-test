from typing import List

import discord
from discord import app_commands
from discord.ext import commands


class SlashCommands(commands.Cog):
    """
    Commands that can be called as `/<command>`.
    """

    def __init__(self, bot: commands.Bot, approved_roles: List[str]):
        """
        :param bot: discord bot
        :param approved_roles: Roles that are allowed to approve prompts
        """
        self.bot = bot
        self.approved_roles = approved_roles

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
        # TODO: Store the prompt temporarily in memory?
        # Or add to the DB and set approved as N.
        embed = discord.Embed(
            title="#ID: 1234",
            description="Prompt Received!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Pool", value=pool, inline=True)
        embed.add_field(name="Prompt", value=prompt, inline=True)
        embed.add_field(name="Weight", value=weight, inline=True)
        embed.add_field(name="Sensitivity", value=sensitivity, inline=True)
        embed.add_field(name="Flags", value=flags, inline=False)
        embed.set_footer(text="Prompt will be added to pool after approval.")
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
        name="add-pool",
        description="Create a new pool/dataset.",
    )
    @app_commands.describe(
        pool="Name of the pool to create.",
    )
    async def add_pool(self, interaction: discord.Interaction, pool: str):
        """
        Create a new pool/dataset.
        Only users of specific roles can create a new pool.
        """
        print("TODO: add-pool")

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
        print("Show Pool: Unimplemented!")

    ###################################################################################
    @app_commands.command(
        name="list-pools",
        description="Shows all the currently available pools.",
    )
    async def list_pools(self, interaction: discord.Interaction):
        """
        Show all the available pools.
        """
        print("List Pools: Unimplemented!")

    ###################################################################################
    @app_commands.command(
        name="pending-prompts",
        description="Show all the current prompts that are pending approval.",
    )
    async def pending_prompts(self, interaction: discord.Interaction):
        """
        Show all the current prompts that are pending approval.
        """
        print("Pending Prompts: Unimplemented!")