from pydoc import describe
import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
from discord.ui import Button, View, Select
from discord import app_commands
import asyncio
import sys
from app.bot.helper.confighelper import MEMBARR_VERSION, switch, Discord_bot_token, emby_roles
import app.bot.helper.confighelper as confighelper
import app.bot.helper.embyhelper as emby
from app.bot.helper.message import *
from requests import ConnectTimeout

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


emby_commands = app_commands.Group(name="embysettings", description="Membarr Emby commands")


@emby_commands.command(name="addrole", description="Add a role to automatically add users to Emby")
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


@emby_commands.command(name="removerole", description="Stop adding users with a role to Emby")
@app_commands.checks.has_permissions(administrator=True)
async def embyroleremove(interaction: discord.Interaction, role: discord.Role):
    if role.name not in emby_roles:
        await embederror(interaction.response, f"\"{role.name}\" is currently not a Emby role.")
        return
    emby_roles.remove(role.name)
    confighelper.change_config("emby_roles", ",".join(emby_roles))
    await interaction.response.send_message(f"Membarr will stop auto-adding \"{role.name}\" to Emby",
                                            ephemeral=True)


@emby_commands.command(name="listroles",
                           description="List all roles whose members will be automatically added to Emby")
@app_commands.checks.has_permissions(administrator=True)
async def embyrolels(interaction: discord.Interaction):
    await interaction.response.send_message(
        "The following roles are being automatically added to Emby:\n" +
        ", ".join(emby_roles), ephemeral=True
    )


@emby_commands.command(name="setup", description="Setup Emby integration")
@app_commands.checks.has_permissions(administrator=True)
async def setupemby(interaction: discord.Interaction, server_url: str, api_key: str, external_url: str = None):
    await interaction.response.defer()
    # get rid of training slashes
    server_url = server_url.rstrip('/')

    try:
        server_status = emby.get_status(server_url, api_key)
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


@emby_commands.command(name="setuplibs", description="Setup libraries that new users can access")
@app_commands.checks.has_permissions(administrator=True)
async def setupembylibs(interaction: discord.Interaction, libraries: str):
    if not libraries:
        await embederror(interaction.response, "libraries string is empty.")
        return
    else:
        # Do some fancy python to remove spaces from libraries string, but only where wanted.
        libraries = ",".join(list(map(lambda lib: lib.strip(), libraries.split(","))))
        confighelper.change_config("emby_libs", str(libraries))
        print("Emby libraries updated. Restarting bot. Please wait.")
        await interaction.response.send_message(
            "Emby libraries updated. Please wait a few seconds for bot to restart.", ephemeral=True)
        await reload()
        print("Bot has been restarted. Give it a few seconds.")


# Enable / Disable Emby integration
@emby_commands.command(name="enable", description="Enable adding users to Emby")
@app_commands.checks.has_permissions(administrator=True)
async def enableemby(interaction: discord.Interaction):
    if confighelper.USE_EMBY:
        await interaction.response.send_message("Emby already enabled.", ephemeral=True)
        return
    confighelper.change_config("emby_enabled", True)
    print("Emby enabled, reloading server")
    confighelper.USE_EMBY = True
    await reload()
    await interaction.response.send_message("Emby enabled. Restarting server. Give it a few seconds.",
                                            ephemeral=True)
    print("Bot has restarted. Give it a few seconds.")


@emby_commands.command(name="disable", description="Disable adding users to Emby")
@app_commands.checks.has_permissions(administrator=True)
async def disableemby(interaction: discord.Interaction):
    if not confighelper.USE_EMBY:
        await interaction.response.send_message("Emby already disabled.", ephemeral=True)
        return
    confighelper.change_config("emby_enabled", False)
    print("Emby disabled, reloading server")
    await reload()
    confighelper.USE_EMBY = False
    await interaction.response.send_message("Emby disabled. Restarting server. Give it a few seconds.",
                                            ephemeral=True)
    print("Bot has restarted. Give it a few seconds.")


bot.tree.add_command(emby_commands)

bot.run(Discord_bot_token)
