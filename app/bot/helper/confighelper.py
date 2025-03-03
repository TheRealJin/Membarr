import configparser
import os
from os import environ, path
from dotenv import load_dotenv
import sqlite3

CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'
MEMBARR_VERSION = 1.1

config = configparser.ConfigParser()

# Define all configuration keys, including Emby and Authentik
CONFIG_KEYS = [
    'username', 'password', 'discord_bot_token', 'owner_id', 'channel_id',
    'auto_remove_user', 'emby_api_key', 'emby_server_url', 'emby_roles', 'emby_libs',
    'emby_enabled', 'emby_external_url', 'authentik_server_url', 'authentik_api_token'
]

# Settings
Discord_bot_token = ""
EMBY_SERVER_URL = ""
EMBY_API_KEY = ""
AUTHENTIK_SERVER_URL = ""
AUTHENTIK_API_TOKEN = ""
emby_libs = ""
emby_roles = None
emby_configured = True  # Emby configuration flag
authentik_configured = True  # Authentik configuration flag

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

# Authentik Configuration
try:
    AUTHENTIK_SERVER_URL = config.get(BOT_SECTION, 'authentik_server_url')
    AUTHENTIK_API_TOKEN = config.get(BOT_SECTION, 'authentik_api_token')
except:
    print("Could not load Authentik config")
    authentik_configured = False

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

# Database setup
DB_PATH = 'app/data/membarr.db'

def initialize_db():
    """
    Initialize the database with the required tables.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT UNIQUE,
            email TEXT,
            emby_username TEXT,
            authentik_username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_all(discord_id, email, emby_username, authentik_username):
    """
    Save a user's details to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (discord_id, email, emby_username, authentik_username)
        VALUES (?, ?, ?, ?)
    ''', (discord_id, email, emby_username, authentik_username))
    conn.commit()
    conn.close()

def save_user_emby(discord_id, emby_username):
    """
    Save a user's Emby username to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (discord_id, emby_username)
        VALUES (?, ?)
    ''', (discord_id, emby_username))
    conn.commit()
    conn.close()

def save_user_authentik(discord_id, authentik_username):
    """
    Save a user's Authentik username to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (discord_id, authentik_username)
        VALUES (?, ?)
    ''', (discord_id, authentik_username))
    conn.commit()
    conn.close()

def get_emby_username(discord_id):
    """
    Retrieve a user's Emby username from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT emby_username FROM users WHERE discord_id = ?', (discord_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_authentik_username(discord_id):
    """
    Retrieve a user's Authentik username from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT authentik_username FROM users WHERE discord_id = ?', (discord_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def remove_emby(discord_id):
    """
    Remove a user's Emby username from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET emby_username = NULL WHERE discord_id = ?', (discord_id,))
    conn.commit()
    conn.close()

def remove_authentik(discord_id):
    """
    Remove a user's Authentik username from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET authentik_username = NULL WHERE discord_id = ?', (discord_id,))
    conn.commit()
    conn.close()

def delete_user(discord_id):
    """
    Delete a user from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE discord_id = ?', (discord_id,))
    conn.commit()
    conn.close()

def read_all():
    """
    Retrieve all users from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()
    conn.close()
    return result

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

# Initialize the database when this module is imported
initialize_db()
