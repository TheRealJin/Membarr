from pydoc import describe
import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
from discord.ui import Button, View, Select
from discord import app_commands
import asyncio
import sys
from app.bot.helper.confighelper import (
    MEMBARR_VERSION, switch, Discord_bot_token, plex_roles, jellyfin_roles, emby_roles
)
import app.bot.helper.confighelper as confighelper
import app.bot.helper.jellyfinhelper as jelly
import app.bot.helper.embyhelper as emby  # New module for Emby
from app.bot.helper.message import *
from requests import ConnectTimeout
from plexapi.myplex import MyPlexAccount

maxroles = 10

if switch == 0:
    print("Missing Config.")
    sys.exit()


class Bot(commands.Bot):
    def __init__(self) -> None:
        print("Initializing Discord bot")
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=".", intents=intents)

    async def on_ready(self):
        print("Bot is online.")
        for guild in self.guilds:
            print("Syncing commands to " + guild.name)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_guild_join(self, guild):
        print(f"Joined guild {guild.name}")
        print(f"Syncing commands to {guild.name}")
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def setup_hook(self):
        print("Loading media server connectors")
        await self.load_extension(f'app.bot.cogs.app')


bot = Bot()


async def reload():
    await bot.reload_extension(f'app.bot.cogs.app')


async def getuser(interaction, server, type):
    value = None
    await interaction.user.send("Please reply with your {} {}:".format(server, type))
    while (value == None):
        def check(m):
            return m.author == interaction.user and not m.guild

        try:
            value = await bot.wait_for('message', timeout=200, check=check)
            return value.content
        except asyncio.TimeoutError:
            message = "Timed Out. Try again."
            return None


plex_commands = app_commands.Group(name="plexsettings", description="Membarr Plex commands")
jellyfin_commands = app_commands.Group(name="jellyfinsettings", description="Membarr Jellyfin commands")
emby_commands = app_commands.Group(name="embysettings", description="Membarr Emby commands")  # New group for Emby


@plex_commands.command(name="addrole", description="Add a role to automatically add users to Plex")
@app_commands.checks.has_permissions(administrator=True)
async def plexroleadd(interaction: discord.Interaction, role: discord.Role):
    if len(plex_roles) <= maxroles:
        # Do not add roles multiple times.
        if role.name in plex_roles:
            await embederror(interaction.response, f"Plex role \"{role.name}\" already added.")
            return

        plex_roles.append(role.name)
        saveroles = ",".join(plex_roles)
        confighelper.change_config("plex_roles", saveroles)
        await interaction.response.send_message("Updated Plex roles. Bot is restarting. Please wait.", ephemeral=True)
        print("Plex roles updated. Restarting bot, Give it a few seconds.")
        await reload()
        print("Bot has been restarted. Give it a few seconds.")


@jellyfin_commands.command(name="addrole", description="Add a role to automatically add users to Jellyfin")
@app_commands.checks.has_permissions(administrator=True)
async def jellyroleadd(interaction: discord.Interaction, role: discord.Role):
    if len(jellyfin_roles) <= maxroles:
        # Do not add roles multiple times.
        if role.name in jellyfin_roles:
            await embederror(interaction.response, f"Jellyfin role \"{role.name}\" already added.")
            return

        jellyfin_roles.append(role.name)
        saveroles = ",".join(jellyfin_roles)
        confighelper.change_config("jellyfin_roles", saveroles)
        await interaction.response.send_message("Updated Jellyfin roles. Bot is restarting. Please wait a few seconds.",
                                                ephemeral=True)
        print("Jellyfin roles updated. Restarting bot.")
        await reload()
        print("Bot has been restarted. Give it a few seconds.")


@emby_commands.command(name="addrole", description="Add a role to automatically add users to Emby")  # New command for Emby
@app_commands.checks.has_permissions(administrator=True)
async def embyroleadd(interaction: discord.Interaction, role: discord.Role):
    if len(emby_roles) <= maxroles:
        # Do not add roles multiple times.
        if role.name in emby_roles:
            await embederror(interaction.response, f"Emby role \"{role.name}\" already added.")
            return

        emby_roles.append(role.name)
        saveroles = ",".join(emby_roles)
        confighelper.change_config("emby_roles", saveroles)
        await interaction.response.send_message("Updated Emby roles. Bot is restarting. Please wait a few seconds.",
                                                ephemeral=True)
        print("Emby roles updated. Restarting bot.")
        await reload()
        print("Bot has been restarted. Give it a few seconds.")


@jellyfin_commands.command(name="setup", description="Setup Jellyfin integration")
@app_commands.checks.has_permissions(administrator=True)
async def setupjelly(interaction: discord.Interaction, server_url: str, api_key: str, external_url: str = None):
    await interaction.response.defer()
    # get rid of training slashes
    server_url = server_url.rstrip('/')

    try:
        server_status = jelly.get_status(server_url, api_key)
        if server_status == 200:
            pass
        elif server_status == 401:
            # Unauthorized
            await embederror(interaction.followup, "API key provided is invalid")
            return
        elif server_status == 403:
            # Forbidden
            await embederror(interaction.followup, "API key provided does not have permissions")
            return
        elif server_status == 404:
            # page not found
            await embederror(interaction.followup, "Server endpoint provided was not found")
            return
        else:
            await embederror(interaction.followup,
                             "Unknown error occurred while connecting to Jellyfin. Check Membarr logs.")
    except ConnectTimeout as e:
        await embederror(interaction.followup,
                         "Connection to server timed out. Check that Jellyfin is online and reachable.")
        return
    except Exception as e:
        print("Exception while testing Jellyfin connection")
        print(type(e).__name__)
        print(e)
        await embederror(interaction.followup, "Unknown exception while connecting to Jellyfin. Check Membarr logs")
        return

    confighelper.change_config("jellyfin_server_url", str(server_url))
    confighelper.change_config("jellyfin_api_key", str(api_key))
    if external_url is not None:
        confighelper.change_config("jellyfin_external_url", str(external_url))
    else:
        confighelper.change_config("jellyfin_external_url", "")
    print("Jellyfin server URL and API key updated. Restarting bot.")
    await interaction.followup.send("Jellyfin server URL and API key updated. Restarting bot.", ephemeral=True)
    await reload()
    print("Bot has been restarted. Give it a few seconds.")


@emby_commands.command(name="setup", description="Setup Emby integration")  # New command for Emby
@app_commands.checks.has_permissions(administrator=True)
async def setupemby(interaction: discord.Interaction, server_url: str, api_key: str, external_url: str = None):
    await interaction.response.defer()
    # get rid of training slashes
    server_url = server_url.rstrip('/')

    try:
        server_status = emby.get_status(server_url, api_key)  # Use embyhelper for Emby
        if server_status == 200:
            pass
        elif server_status == 401:
            # Unauthorized
            await embederror(interaction.followup, "API key provided is invalid")
            return
        elif server_status == 403:
            # Forbidden
            await embederror(interaction.followup, "API key provided does not have permissions")
            return
        elif server_status == 404:
            # page not found
            await embederror(interaction.followup, "Server endpoint provided was not found")
            return
        else:
            await embederror(interaction.followup,
                             "Unknown error occurred while connecting to Emby. Check Membarr logs.")
    except ConnectTimeout as e:
        await embederror(interaction.followup,
                         "Connection to server timed out. Check that Emby is online and reachable.")
        return
    except Exception as e:
        print("Exception while testing Emby connection")
        print(type(e).__name__)
        print(e)
        await embederror(interaction.followup, "Unknown exception while connecting to Emby. Check Membarr logs")
        return

    confighelper.change_config("emby_server_url", str(server_url))
    confighelper.change_config("emby_api_key", str(api_key))
    if external_url is not None:
        confighelper.change_config("emby_external_url", str(external_url))
    else:
        confighelper.change_config("emby_external_url", "")
    print("Emby server URL and API key updated. Restarting bot.")
    await interaction.followup.send("Emby server URL and API key updated. Restarting bot.", ephemeral=True)
    await reload()
    print("Bot has been restarted. Give it a few seconds.")


# Add commands to the bot
bot.tree.add_command(plex_commands)
bot.tree.add_command(jellyfin_commands)
bot.tree.add_command(emby_commands)  # Add Emby commands

bot.run(Discord_bot_token)
