import configparser
import os
from os import environ, path
from dotenv import load_dotenv

CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'
MEMBARR_VERSION = 1.1

config = configparser.ConfigParser()

# Define all configuration keys, including Emby
CONFIG_KEYS = [
    'username', 'password', 'discord_bot_token', 'owner_id', 'channel_id',
    'auto_remove_user', 'emby_api_key', 'emby_server_url', 'emby_roles', 'emby_libs',
    'emby_enabled', 'emby_external_url'
]

# Settings
Discord_bot_token = ""
EMBY_SERVER_URL = ""
EMBY_API_KEY = ""
emby_libs = ""
emby_roles = None
emby_configured = True  # Emby configuration flag

switch = 0

# Load environment variables if .env file exists
if path.exists('bot.env'):
    try:
        load_dotenv(dotenv_path='bot.env')
        Discord_bot_token = environ.get('discord_bot_token')
        switch = 1
    except Exception as e:
        pass

# Fallback to system environment variables
try:
    Discord_bot_token = str(os.environ['token'])
    switch = 1
except Exception as e:
    pass

# Create config file if it doesn't exist
if not path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w') as fp:
        pass

# Read the config file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Emby Configuration
try:
    EMBY_SERVER_URL = config.get(BOT_SECTION, 'emby_server_url')
    EMBY_API_KEY = config.get(BOT_SECTION, "emby_api_key")
except:
    print("Could not load Emby config")
    emby_configured = False

try:
    EMBY_EXTERNAL_URL = config.get(BOT_SECTION, "emby_external_url")
    if not EMBY_EXTERNAL_URL:
        EMBY_EXTERNAL_URL = EMBY_SERVER_URL
except:
    EMBY_EXTERNAL_URL = EMBY_SERVER_URL
    print("Could not get Emby external url. Defaulting to server url.")

try:
    emby_roles = config.get(BOT_SECTION, 'emby_roles')
except:
    print("Could not get Emby roles config")
    emby_roles = None
if emby_roles:
    emby_roles = list(emby_roles.split(','))
else:
    emby_roles = []

try:
    emby_libs = config.get(BOT_SECTION, 'emby_libs')
except:
    print("Could not get Emby libs config. Defaulting to all libraries.")
    emby_libs = None
if emby_libs is None:
    emby_libs = ["all"]
else:
    emby_libs = list(emby_libs.split(','))

# Enable/Disable Configurations
try:
    USE_EMBY = config.get(BOT_SECTION, 'emby_enabled')
    USE_EMBY = USE_EMBY.lower() == "true"
except:
    print("Could not get Emby enable config. Defaulting to False")
    USE_EMBY = False

def get_config():
    """
    Function to return current config
    """
    try:
        config.read(CONFIG_PATH)
        return config
    except Exception as e:
        print(e)
        print('Error in reading config')
        return None

def change_config(key, value):
    """
    Function to change the key, value pair in config
    """
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
    except Exception as e:
        print(e)
        print("Cannot read config.")

    try:
        config.set(BOT_SECTION, key, str(value))
    except Exception as e:
        config.add_section(BOT_SECTION)
        config.set(BOT_SECTION, key, str(value))

    try:
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
    except Exception as e:
        print(e)
        print("Cannot write to config.")
