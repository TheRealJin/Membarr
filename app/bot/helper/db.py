import sqlite3

from app.bot.helper.dbupdater import check_table_version, update_table

DB_URL = 'app/config/app.db'
DB_TABLE = 'clients'

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connected to db")
    except Error as e:
        print("error in connecting to db")
    finally:
        if conn:
            return conn

def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{0}';""".format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True
    dbcur.close()
    return False

conn = create_connection(DB_URL)

# Checking if table exists
if checkTableExists(conn, DB_TABLE):
    print('Table exists.')
else:
    conn.execute(
    '''CREATE TABLE "clients" (
    "id"	INTEGER NOT NULL UNIQUE,
    "discord_username"	TEXT NOT NULL UNIQUE,
    "emby_username" TEXT,  -- Updated to Emby
    "authentik_username" TEXT,  -- Added for Authentik
    PRIMARY KEY("id" AUTOINCREMENT)
    );''')

update_table(conn, DB_TABLE)

def save_user(username):
    if username:
        conn.execute("INSERT INTO clients (discord_username) VALUES ('"+ username +"')")
        conn.commit()
        print("User added to db.")
    else:
        return "Username cannot be empty"
    
def save_user_emby(username, emby_username):  # Updated to Emby
    if username and emby_username:
        conn.execute(f"""
            INSERT OR REPLACE INTO clients(discord_username, emby_username)
            VALUES('{username}', '{emby_username}')
        """)
        conn.commit()
        print("User added to db.")
    else:
        return "Discord and Emby usernames cannot be empty"

def save_user_authentik(username, authentik_username):  # Added for Authentik
    if username and authentik_username:
        conn.execute(f"""
            INSERT OR REPLACE INTO clients(discord_username, authentik_username)
            VALUES('{username}', '{authentik_username}')
        """)
        conn.commit()
        print("User added to db.")
    else:
        return "Discord and Authentik usernames cannot be empty"

def save_user_all(username, emby_username, authentik_username):  # Updated to include Authentik
    if username and emby_username and authentik_username:
        conn.execute(f"""
            INSERT OR REPLACE INTO clients(discord_username, emby_username, authentik_username)
            VALUES('{username}', '{emby_username}', '{authentik_username}')
        """)
        conn.commit()
        print("User added to db.")
    elif username and emby_username:
        save_user_emby(username, emby_username)
    elif username and authentik_username:
        save_user_authentik(username, authentik_username)
    elif username:
        save_user(username)
    else:
        return "Discord username must be provided"

def get_emby_username(username):  # Updated to Emby
    """
    Get Emby username of user based on discord username

    param   username: discord username

    return  Emby username
    """
    if username:
        try:
            cursor = conn.execute('SELECT discord_username, emby_username from clients where discord_username="{}";'.format(username))
            for row in cursor:
                emby_username = row[1]
            if emby_username:
                return emby_username
            else:
                return "No users found"
        except:
            return "error in fetching from db"
    else:
        return "username cannot be empty"

def get_authentik_username(username):  # Added for Authentik
    """
    Get Authentik username of user based on discord username

    param   username: discord username

    return  Authentik username
    """
    if username:
        try:
            cursor = conn.execute('SELECT discord_username, authentik_username from clients where discord_username="{}";'.format(username))
            for row in cursor:
                authentik_username = row[1]
            if authentik_username:
                return authentik_username
            else:
                return "No users found"
        except:
            return "error in fetching from db"
    else:
        return "username cannot be empty"

def remove_emby(username):  # Updated to Emby
    """
    Sets Emby username of discord user to null in database
    """
    if username:
        conn.execute(f"UPDATE clients SET emby_username = null WHERE discord_username = '{username}'")
        conn.commit()
        print(f"Emby username removed from user {username} in database")
        return True
    else:
        print(f"Username cannot be empty.")
        return False

def remove_authentik(username):  # Added for Authentik
    """
    Sets Authentik username of discord user to null in database
    """
    if username:
        conn.execute(f"UPDATE clients SET authentik_username = null WHERE discord_username = '{username}'")
        conn.commit()
        print(f"Authentik username removed from user {username} in database")
        return True
    else:
        print(f"Username cannot be empty.")
        return False

def delete_user(username):
    if username:
        try:
            conn.execute('DELETE from clients where discord_username="{}";'.format(username))
            conn.commit()
            return True
        except:
            return False
    else:
        return "username cannot be empty"

def read_all():
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients")
    rows = cur.fetchall()
    all = []
    for row in rows:
        all.append(row)
    return all
