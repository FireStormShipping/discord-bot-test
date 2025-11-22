import os
from dotenv import load_dotenv

import discord
from discord import app_commands

load_dotenv() # Load env variables from .env if it exists

APPROVED_ROLES = ["admin"]
GUILD_ID = int(os.environ.get('GUILD_ID', '1234'))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Add the guild ids in which the slash command will appear.
# it will take some time (up to an hour) to register the
# command if it's for all guilds.
@tree.command(
    name="delete-prompt",
    description="Delete a prompt that has not been approved yet",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(id="The ID of the unapproved prompt to delete")
async def delete_prompt(interaction: discord.Interaction, id: int):
    print(f"ID: {id}")
    # TODO: remove the un-approved prompt from memory or delete from db
    await interaction.response.send_message(f"Prompt deleted, ID: {id}")

@tree.command(
    name="add-prompt",
    description="Submit a prompt for approval",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(pool="The pool to add the prompt to")
@app_commands.describe(prompt="The prompt to add to the pool")
async def approve_prompt(interaction: discord.Interaction, pool: str, prompt: str):
    print(f"Pool: {pool}, Prompt: {prompt}")
    # TODO: Store the prompt temporarily in memory?
    # Or add to the DB and set approved as N.
    await interaction.response.send_message("Prompt Received, ID: 1234")

@tree.command(
    name="approve-prompt",
    description="Approve Prompt Command",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(id="The ID of the unapproved prompt to approve")
async def approve_prompt(interaction: discord.Interaction, id: int):
    """
    Allow certain roles to approve the prompt.
    """
    user_roles = interaction.user.roles
    for role in user_roles:
        if role.name in APPROVED_ROLES:
            await interaction.response.send_message(f"Prompt ID #{id} approved!")
            # TODO: when prompt is approved, add it to the database?
            # Or alternatively in DB has a column for APPROVED = y/n, then flip it.
            return
    await interaction.response.send_message("Role is not allowed to approve prompt.")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Ready!")

if __name__ == "__main__":
    bot_token = os.environ.get('BOT_TOKEN', 'default_token')
    client.run(bot_token)
