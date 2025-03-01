from pickle import FALSE
import app.bot.helper.embyhelper as emby  # Updated to use Emby helper
from app.bot.helper.textformat import bcolors
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import app.bot.helper.db as db
import app.bot.helper.plexhelper as plexhelper
import texttable
from app.bot.helper.message import *
from app.bot.helper.confighelper import *

CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'

plex_configured = True
emby_configured = True  # Updated to Emby

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

plex_token_configured = True
try:
    PLEX_TOKEN = config.get(BOT_SECTION, 'plex_token')
    PLEX_BASE_URL = config.get(BOT_SECTION, 'plex_base_url')
except:
    print("No Plex auth token details found")
    plex_token_configured = False

# Get Plex config
try:
    PLEXUSER = config.get(BOT_SECTION, 'plex_user')
    PLEXPASS = config.get(BOT_SECTION, 'plex_pass')
    PLEX_SERVER_NAME = config.get(BOT_SECTION, 'plex_server_name')
except:
    print("No Plex login info found")
    if not plex_token_configured:
        print("Could not load plex config")
        plex_configured = False

# Get Plex roles config
try:
    plex_roles = config.get(BOT_SECTION, 'plex_roles')
except:
    plex_roles = None
if plex_roles:
    plex_roles = list(plex_roles.split(','))
else:
    plex_roles = []

# Get Plex libs config
try:
    Plex_LIBS = config.get(BOT_SECTION, 'plex_libs')
except:
    Plex_LIBS = None
if Plex_LIBS is None:
    Plex_LIBS = ["all"]
else:
    Plex_LIBS = list(Plex_LIBS.split(','))
    
# Get Emby config
try:
    EMBY_SERVER_URL = config.get(BOT_SECTION, 'emby_server_url')  # Updated to Emby
    EMBY_API_KEY = config.get(BOT_SECTION, "emby_api_key")  # Updated to Emby
except:
    emby_configured = False  # Updated to Emby

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
    USE_PLEX = config.get(BOT_SECTION, "plex_enabled")
    USE_PLEX = USE_PLEX.lower() == "true"
except:
    USE_PLEX = False

try:
    EMBY_EXTERNAL_URL = config.get(BOT_SECTION, "emby_external_url")  # Updated to Emby
    if not EMBY_EXTERNAL_URL:
        EMBY_EXTERNAL_URL = EMBY_SERVER_URL
except:
    EMBY_EXTERNAL_URL = EMBY_SERVER_URL
    print("Could not get Emby external url. Defaulting to server url.")

if USE_PLEX and plex_configured:
    try:
        print("Connecting to Plex......")
        if plex_token_configured and PLEX_TOKEN and PLEX_BASE_URL:
            print("Using Plex auth token")
            plex = PlexServer(PLEX_BASE_URL, PLEX_TOKEN)
        else:
            print("Using Plex login info")
            account = MyPlexAccount(PLEXUSER, PLEXPASS)
            plex = account.resource(PLEX_SERVER_NAME).connect()  # returns a PlexServer instance
        print('Logged into plex!')
    except Exception as e:
        # probably rate limited.
        print('Error with plex login. Please check Plex authentication details. If you have restarted the bot multiple times recently, this is most likely due to being ratelimited on the Plex API. Try again in 10 minutes.')
        print(f'Error: {e}')
else:
    print(f"Plex {'disabled' if not USE_PLEX else 'not configured'}. Skipping Plex login.")


class app(commands.Cog):
    # App command groups
    plex_commands = app_commands.Group(name="plex", description="Membarr Plex commands")
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

        # TODO: Make these debug statements work. roles are currently empty arrays if no roles assigned.
        if plex_roles is None:
            print('Configure Plex roles to enable auto invite to Plex after a role is assigned.')
        if emby_roles is None:  # Updated to Emby
            print('Configure Emby roles to enable auto invite to Emby after a role is assigned.')
    
    async def getemail(self, after):
        email = None
        await embedinfo(after,'Welcome To '+ PLEX_SERVER_NAME +'. Please reply with your email to be added to the Plex server!')
        await embedinfo(after,'If you do not respond within 24 hours, the request will be cancelled, and the server admin will need to add you manually.')
        while(email == None):
            def check(m):
                return m.author == after and not m.guild
            try:
                email = await self.bot.wait_for('message', timeout=86400, check=check)
                if(plexhelper.verifyemail(str(email.content))):
                    return str(email.content)
                else:
                    email = None
                    message = "The email you provided is invalid, please respond only with the email you used to sign up for Plex."
                    await embederror(after, message)
                    continue
            except asyncio.TimeoutError:
                message = "Timed out. Please contact the server admin directly."
                await embederror(after, message)
                return None
    
    async def getusername(self, after):
        username = None
        await embedinfo(after, f"Welcome To Emby! Please reply with your username to be added to the Emby server!")  # Updated to Emby
        await embedinfo(after, f"If you do not respond within 24 hours, the request will be cancelled, and the server admin will need to add you manually.")
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

    async def addtoplex(self, email, response):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexadd(plex,email,Plex_LIBS):
                await embedinfo(response, 'This email address has been added to plex')
                return True
            else:
                await embederror(response, 'There was an error adding this email address. Check logs.')
                return False
        else:
            await embederror(response, 'Invalid email.')
            return False

    async def removefromplex(self, email, response):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexremove(plex,email):
                await embedinfo(response, 'This email address has been removed from plex.')
                return True
            else:
                await embederror(response, 'There was an error removing this email address. Check logs.')
                return False
        else:
            await embederror(response, 'Invalid email.')
            return False
    
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
        if plex_roles is None and emby_roles is None:  # Updated to Emby
            return
        roles_in_guild = after.guild.roles
        role = None

        plex_processed = False
        emby_processed = False  # Updated to Emby

        # Check Plex roles
        if plex_configured and USE_PLEX:
            for role_for_app in plex_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Plex role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        email = await self.getemail(after)
                        if email is not None:
                            await embedinfo(after, "Got it we will be adding your email to plex shortly!")
                            if plexhelper.plexadd(plex,email,Plex_LIBS):
                                db.save_user_email(str(after.id), email)
                                await asyncio.sleep(5)
                                await embedinfo(after, 'You have Been Added To Plex! Login to plex and accept the invite!')
                            else:
                                await embedinfo(after, 'There was an error adding this email address. Message Server Admin.')
                        plex_processed = True
                        break

                    # Plex role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        try:
                            user_id = after.id
                            email = db.get_useremail(user_id)
                            plexhelper.plexremove(plex,email)
                            deleted = db.remove_email(user_id)
                            if deleted:
                                print("Removed Plex email {} from db".format(after.name))
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Cannot remove Plex from this user.")
                            await embedinfo(after, "You have been removed from Plex")
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from plex.".format(email))
                        plex_processed = True
                        break
                if plex_processed:
                    break

        role = None
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
                            # Send a DM to the user asking for their Emby username
                            await embedinfo(after, "Welcome to the server! Please reply with your Emby username to be added to the Emby server.")
                            await embedinfo(after, "If you do not respond within 24 hours, the request will be cancelled, and the server admin will need to add you manually.")

                            # Wait for the user's response
                            username = await self.getusername(after)
                            if username is not None:
                                await embedinfo(after, "Got it! We will be creating your Emby account shortly!")
                                password = emby.generate_password(16)  # Generate a random password
                                if emby.add_user(EMBY_SERVER_URL, EMBY_API_KEY, username, password, emby_libs):
                                    db.save_user_emby(str(after.id), username)
                                    await asyncio.sleep(5)
                                    await embedcustom(after, "You have been added to Emby!", {'Username': username, 'Password': f"||{password}||"})
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
                            emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, username)  # Updated to Emby
                            deleted = db.remove_emby(user_id)  # Updated to Emby
                            if deleted:
                                print("Removed Emby from {}".format(after.name))  # Updated to Emby
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Cannot remove Emby from this user")  # Updated to Emby
                            await embedinfo(after, "You have been removed from Emby")  # Updated to Emby
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from Emby.".format(username))  # Updated to Emby
                        emby_processed = True  # Updated to Emby
                        break
                if emby_processed:  # Updated to Emby
                    break

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if USE_PLEX and plex_configured:
            email = db.get_useremail(member.id)
            plexhelper.plexremove(plex,email)
        
        if USE_EMBY and emby_configured:  # Updated to Emby
            emby_username = db.get_emby_username(member.id)  # Updated to Emby
            emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, emby_username)  # Updated to Emby
            
        deleted = db.delete_user(member.id)
        if deleted:
            print("Removed {} from db because user left discord server.".format(email))

    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="invite", description="Invite a user to Plex")
    async def plexinvite(self, interaction: discord.Interaction, email: str):
        await self.addtoplex(email, interaction.response)
    
    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="remove", description="Remove a user from Plex")
    async def plexremove(self, interaction: discord.Interaction, email: str):
        await self.removefromplex(email, interaction.response)
    
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
    async def dbadd(self, interaction: discord.Interaction, member: discord.Member, email: str = "", emby_username: str = ""):  # Updated to Emby
        email = email.strip()
        emby_username = emby_username.strip()  # Updated to Emby
        
        # Check email if provided
        if email and not plexhelper.verifyemail(email):
            await embederror(interaction.response, "Invalid email.")
            return

        try:
            db.save_user_all(str(member.id), email, emby_username)  # Updated to Emby
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
