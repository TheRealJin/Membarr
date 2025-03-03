from pickle import FALSE
import app.bot.helper.embyhelper as emby  # Updated to use Emby helper
import app.bot.helper.authentikhelper as authentik  # Added Authentik helper
from app.bot.helper.textformat import bcolors
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import app.bot.helper.db as db
import texttable
from app.bot.helper.message import *
from app.bot.helper.confighelper import *

CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'

emby_configured = True  # Updated to Emby
authentik_configured = True  # Added Authentik

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Get Emby config
try:
    EMBY_SERVER_URL = config.get(BOT_SECTION, 'emby_server_url')  # Updated to Emby
    EMBY_API_KEY = config.get(BOT_SECTION, "emby_api_key")  # Updated to Emby
except:
    emby_configured = False  # Updated to Emby

# Get Authentik config
try:
    AUTHENTIK_SERVER_URL = config.get(BOT_SECTION, 'authentik_server_url')
    AUTHENTIK_API_TOKEN = config.get(BOT_SECTION, 'authentik_api_token')
except:
    authentik_configured = False

# Get Emby roles config
try:
    emby_roles = config.get(BOT_SECTION, 'emby_roles')  # Updated to Emby
except:
    emby_roles = None
if emby_roles:
    emby_roles = list(emby_roles.split(','))
else:
    emby_roles = []

# Get Emby libs config
try:
    emby_libs = config.get(BOT_SECTION, 'emby_libs')  # Updated to Emby
except:
    emby_libs = None
if emby_libs is None:
    emby_libs = ["all"]
else:
    emby_libs = list(emby_libs.split(','))

# Get Enable config
try:
    USE_EMBY = config.get(BOT_SECTION, 'emby_enabled')  # Updated to Emby
    USE_EMBY = USE_EMBY.lower() == "true"
except:
    USE_EMBY = False  # Updated to Emby

try:
    EMBY_EXTERNAL_URL = config.get(BOT_SECTION, "emby_external_url")  # Updated to Emby
    if not EMBY_EXTERNAL_URL:
        EMBY_EXTERNAL_URL = EMBY_SERVER_URL
except:
    EMBY_EXTERNAL_URL = EMBY_SERVER_URL
    print("Could not get Emby external url. Defaulting to server url.")


class app(commands.Cog):
    # App command groups
    emby_commands = app_commands.Group(name="emby", description="Membarr Emby commands")  # Updated to Emby
    membarr_commands = app_commands.Group(name="membarr", description="Membarr general commands")

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('------')
        print("{:^41}".format(f"MEMBARR V {MEMBARR_VERSION}"))
        print(f'Made by Yoruio https://github.com/Yoruio/\n')
        print(f'Forked from Invitarr https://github.com/Sleepingpirates/Invitarr')
        print(f'Named by lordfransie')
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print('------')

        if emby_roles is None:  # Updated to Emby
            print('Configure Emby roles to enable auto invite to Emby after a role is assigned.')
    
    async def getusername(self, after):
        username = None
        while (username is None):
            def check(m):
                return m.author == after and not m.guild
            try:
                username = await self.bot.wait_for('message', timeout=86400, check=check)
                if(emby.verify_username(EMBY_SERVER_URL, EMBY_API_KEY, str(username.content))):  # Updated to Emby
                    return str(username.content)
                else:
                    username = None
                    message = "This username is already chosen. Please select another username."
                    await embederror(after, message)
                    continue
            except asyncio.TimeoutError:
                message = "Timed out. Please contact the server admin directly."
                print("Emby user prompt timed out")
                await embederror(after, message)
                return None
            except Exception as e:
                await embederror(after, "Something went wrong. Please try again with another username.")
                print (e)
                username = None

    async def addtoemby(self, username, password, response):  # Updated to Emby
        if not emby.verify_username(EMBY_SERVER_URL, EMBY_API_KEY, username):  # Updated to Emby
            await embederror(response, f'An account with username {username} already exists.')
            return False

        if emby.add_user(EMBY_SERVER_URL, EMBY_API_KEY, username, password, emby_libs):  # Updated to Emby
            return True
        else:
            await embederror(response, 'There was an error adding this user to Emby. Check logs for more info.')
            return False

    async def removefromemby(self, username, response):  # Updated to Emby
        if emby.verify_username(EMBY_SERVER_URL, EMBY_API_KEY, username):  # Updated to Emby
            await embederror(response, f'Could not find account with username {username}.')
            return
        
        if emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, username):  # Updated to Emby
            await embedinfo(response, f'Successfully removed user {username} from Emby.')
            return True
        else:
            await embederror(response, f'There was an error removing this user from Emby. Check logs for more info.')
            return False

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if emby_roles is None:  # Updated to Emby
            return
        roles_in_guild = after.guild.roles
        role = None

        emby_processed = False  # Updated to Emby

        # Check Emby roles
        if emby_configured and USE_EMBY:  # Updated to Emby
            for role_for_app in emby_roles:  # Updated to Emby
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Emby role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        print("Emby role added")  # Updated to Emby
                        try:
                            # Send a single DM to the user asking for their Emby username
                            await embedinfo(after, 
                                "Welcome to Emby! Please reply with your Emby username to be added to the Emby server.\n"
                                "If you do not respond within 24 hours, the request will be cancelled, and the server admin will need to add you manually."
                            )

                            # Wait for the user's response
                            username = await self.getusername(after)
                            if username is not None:
                                await embedinfo(after, "Got it! We will be creating your Emby account shortly!")
                                password = emby.generate_password(10)  # Generate a random password

                                # Step 1: Create Authentik user
                                if authentik_configured:
                                    if authentik.add_user(AUTHENTIK_SERVER_URL, AUTHENTIK_API_TOKEN, username, password):
                                        await embedcustom(after, "Authentik user created successfully!", {
                                            'Username': username,
                                            'Password': f"||{password}||"
                                        })
                                        db.save_user_authentik(str(after.id), username)  # Save Authentik username to database
                                    else:
                                        await embederror(after, "Failed to create Authentik user. Contact the server admin.")
                                        return

                                # Step 2: Create Emby user
                                if emby.add_user(EMBY_SERVER_URL, EMBY_API_KEY, username, password, emby_libs):
                                    db.save_user_emby(str(after.id), username)
                                    await asyncio.sleep(5)
                                    await embedcustom(after, "You have been added to Emby!", {
                                        'Username': username,
                                        'Password': f"||{password}||"
                                    })
                                    await embedinfo(after, f"Go to {EMBY_EXTERNAL_URL} to log in!")
                                else:
                                    await embedinfo(after, 'There was an error adding this user to Emby. Message the server admin.')
                        except Exception as e:
                            print(f"Error sending DM or handling response: {e}")
                        emby_processed = True  # Updated to Emby
                        break

                    # Emby role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        print("Emby role removed")  # Updated to Emby
                        try:
                            user_id = after.id
                            username = db.get_emby_username(user_id)  # Updated to Emby
                            authentik_username = db.get_authentik_username(user_id)  # Get Authentik username

                            # Step 1: Remove Emby user
                            if emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, username):  # Updated to Emby
                                print(f"Removed Emby user {username}")  # Updated to Emby
                            else:
                                print(f"Failed to remove Emby user {username}")  # Updated to Emby

                            # Step 2: Remove Authentik user
                            if authentik_configured and authentik_username:
                                if authentik.remove_user(AUTHENTIK_SERVER_URL, AUTHENTIK_API_TOKEN, authentik_username):
                                    print(f"Removed Authentik user {authentik_username}")
                                else:
                                    print(f"Failed to remove Authentik user {authentik_username}")

                            # Step 3: Remove user from database
                            deleted = db.remove_emby(user_id)  # Updated to Emby
                            db.remove_authentik(user_id)  # Remove Authentik user from database
                            if deleted:
                                print(f"Removed Emby and Authentik from {after.name}")  # Updated to Emby
                            else:
                                print(f"Cannot remove Emby and Authentik from this user")  # Updated to Emby
                            await embedinfo(after, "You have been removed from Emby and Authentik")  # Updated to Emby
                        except Exception as e:
                            print(e)
                            print(f"{username} Cannot remove this user from Emby and Authentik.")  # Updated to Emby
                        emby_processed = True  # Updated to Emby
                        break
                if emby_processed:  # Updated to Emby
                    break

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if USE_EMBY and emby_configured:  # Updated to Emby
            emby_username = db.get_emby_username(member.id)  # Updated to Emby
            authentik_username = db.get_authentik_username(member.id)  # Get Authentik username

            # Step 1: Remove Emby user
            emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, emby_username)  # Updated to Emby

            # Step 2: Remove Authentik user
            if authentik_configured and authentik_username:
                authentik.remove_user(AUTHENTIK_SERVER_URL, AUTHENTIK_API_TOKEN, authentik_username)

            # Step 3: Remove user from database
            deleted = db.delete_user(member.id)
            if deleted:
                print(f"Removed {emby_username} and {authentik_username} from db because user left discord server.")  # Updated to Emby

    @app_commands.checks.has_permissions(administrator=True)
    @emby_commands.command(name="invite", description="Invite a user to Emby")  # Updated to Emby
    async def embyinvite(self, interaction: discord.Interaction, username: str):
        password = emby.generate_password(16)  # Updated to Emby
        if await self.addtoemby(username, password, interaction.response):  # Updated to Emby
            await embedcustom(interaction.response, "Emby user created!", {'Username': username, 'Password': f"||{password}||"})  # Updated to Emby

    @app_commands.checks.has_permissions(administrator=True)
    @emby_commands.command(name="remove", description="Remove a user from Emby")  # Updated to Emby
    async def embyremove(self, interaction: discord.Interaction, username: str):
        await self.removefromemby(username, interaction.response)  # Updated to Emby
    
    @app_commands.checks.has_permissions(administrator=True)
    @membarr_commands.command(name="dbadd", description="Add a user to the Membarr database")
    async def dbadd(self, interaction: discord.Interaction, member: discord.Member, emby_username: str = ""):  # Updated to Emby
        emby_username = emby_username.strip()  # Updated to Emby
        
        try:
            db.save_user_all(str(member.id), "", emby_username)  # Updated to Emby
            await embedinfo(interaction.response,'User was added to the database.')
        except Exception as e:
            await embedinfo(interaction.response, 'There was an error adding this user to database. Check Membarr logs for more info')
            print(e)

    @app_commands.checks.has_permissions(administrator=True)
    @membarr_commands.command(name="dbls", description="View Membarr database")
    async def dbls(self, interaction: discord.Interaction):

        embed = discord.Embed(title='Membarr Database.')
        all = db.read_all()
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t", "t"])
        table.set_cols_align(["c", "c", "c", "c"])
        header = ("#", "Name", "Email", "Emby")  # Updated to Emby
        table.add_row(header)
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbemby = peoples[3] if peoples[3] else "No Emby"  # Updated to Emby
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbemby+'\n', inline=False)  # Updated to Emby
            table.add_row((index, username, dbemail, dbemby))  # Updated to Emby
        
        total = str(len(all))
        if(len(all)>25):
            f = open("db.txt", "w")
            f.write(table.draw())
            f.close()
            await interaction.response.send_message("Database too large! Total: {total}".format(total = total),file=discord.File('db.txt'), ephemeral=True)
        else:
            await interaction.response.send_message(embed = embed, ephemeral=True)
        
            
    @app_commands.checks.has_permissions(administrator=True)
    @membarr_commands.command(name="dbrm", description="Remove user from Membarr database")
    async def dbrm(self, interaction: discord.Interaction, position: int):
        embed = discord.Embed(title='Membarr Database.')
        all = db.read_all()
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbemby = peoples[3] if peoples[3] else "No Emby"  # Updated to Emby
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbemby+'\n', inline=False)  # Updated to Emby

        try:
            position = int(position) - 1
            id = all[position][1]
            discord_user = await self.bot.fetch_user(id)
            username = discord_user.name
            deleted = db.delete_user(id)
            if deleted:
                print("Removed {} from db".format(username))
                await embedinfo(interaction.response,"Removed {} from db".format(username))
            else:
                await embederror(interaction.response,"Cannot remove this user from db.")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(app(bot))
