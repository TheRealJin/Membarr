import requests
import random
import string
import json

def add_user(emby_url, emby_api_key, username, password, emby_libs):
    try:
        # Create new Emby user
        url = f"{emby_url}/Users/New"
        querystring = {"api_key": emby_api_key}
        payload = {
            "Name": username,
            "Password": password
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, params=querystring)

        # Log the raw response for debugging
        print(f"Emby API Response: {response.text}")

        if response.status_code != 200:
            print(f"Error creating new Emby user: {response.text}")
            return False

        userId = response.json()["Id"]

        # Grant access to User
        url = f"{emby_url}/Users/{userId}/Policy"
        querystring = {"api_key": emby_api_key}

        enabled_folders = []
        server_libs = get_libraries(emby_url, emby_api_key)
        
        if emby_libs[0] != "all":
            for lib in emby_libs:
                found = False
                for server_lib in server_libs:
                    if lib == server_lib['Name']:
                        enabled_folders.append(server_lib['ItemId'])
                        found = True
                if not found:
                    print(f"Couldn't find Emby Library: {lib}")

        payload = {
            "IsAdministrator": False,
            "IsHidden": True,
            "IsDisabled": False,
            "BlockedTags": [],
            "EnableUserPreferenceAccess": True,
            "AccessSchedules": [],
            "BlockUnratedItems": [],
            "EnableRemoteControlOfOtherUsers": False,
            "EnableSharedDeviceControl": True,
            "EnableRemoteAccess": True,
            "EnableLiveTvManagement": True,
            "EnableLiveTvAccess": True,
            "EnableMediaPlayback": True,
            "EnableAudioPlaybackTranscoding": True,
            "EnableVideoPlaybackTranscoding": True,
            "EnablePlaybackRemuxing": True,
            "ForceRemoteSourceTranscoding": False,
            "EnableContentDeletion": False,
            "EnableContentDeletionFromFolders": [],
            "EnableContentDownloading": True,
            "EnableSyncTranscoding": True,
            "EnableMediaConversion": True,
            "EnabledDevices": [],
            "EnableAllDevices": True,
            "EnabledChannels": [],
            "EnableAllChannels": False,
            "EnabledFolders": enabled_folders,
            "EnableAllFolders": emby_libs[0] == "all",
            "InvalidLoginAttemptCount": 0,
            "LoginAttemptsBeforeLockout": -1,
            "MaxActiveSessions": 0,
            "EnablePublicSharing": True,
            "BlockedMediaFolders": [],
            "BlockedChannels": [],
            "RemoteClientBitrateLimit": 0,
            "AuthenticationProviderId": "Emby.Server.Implementations.Users.DefaultAuthenticationProvider",
            "PasswordResetProviderId": "Emby.Server.Implementations.Users.DefaultPasswordResetProvider",
            "SyncPlayAccess": "CreateAndJoinGroups"
        }
        headers = {"content-type": "application/json"}

        response = requests.post(url, json=payload, headers=headers, params=querystring)

        # Log the raw response for debugging
        print(f"Emby API Response: {response.text}")

        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            print(f"Error setting user permissions: {response.text}")
            return False

    except Exception as e:
        print(f"Exception in add_user: {e}")
        return False

def get_libraries(emby_url, emby_api_key):
    try:
        url = f"{emby_url}/Library/VirtualFolders"
        querystring = {"api_key": emby_api_key}
        response = requests.get(url, params=querystring)

        # Log the raw response for debugging
        print(f"Emby API Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching libraries: {response.text}")
            return []
    except Exception as e:
        print(f"Exception in get_libraries: {e}")
        return []

def verify_username(emby_url, emby_api_key, username):
    try:
        users = get_users(emby_url, emby_api_key)
        for user in users:
            if user['Name'] == username:
                return False
        return True
    except Exception as e:
        print(f"Exception in verify_username: {e}")
        return False

def remove_user(emby_url, emby_api_key, emby_username):
    try:
        # Get User ID
        users = get_users(emby_url, emby_api_key)
        userId = None
        for user in users:
            if user['Name'].lower() == emby_username.lower():
                userId = user['Id']
        
        if userId is None:
            # User not found
            print(f"Error removing user {emby_username} from Emby: Could not find user.")
            return False
        
        # Delete User
        url = f"{emby_url}/Users/{userId}"
        querystring = {"api_key": emby_api_key}
        response = requests.delete(url, params=querystring)

        # Log the raw response for debugging
        print(f"Emby API Response: {response.text}")

        if response.status_code == 204 or response.status_code == 200:
            return True
        else:
            print(f"Error deleting Emby user: {response.text}")
            return False
    except Exception as e:
        print(f"Exception in remove_user: {e}")
        return False

def get_users(emby_url, emby_api_key):
    try:
        url = f"{emby_url}/Users"
        querystring = {"api_key": emby_api_key}
        response = requests.get(url, params=querystring)

        # Log the raw response for debugging
        print(f"Emby API Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching users: {response.text}")
            return []
    except Exception as e:
        print(f"Exception in get_users: {e}")
        return []

def generate_password(length, lower=True, upper=True, numbers=True, symbols=True):
    character_list = []
    if not (lower or upper or numbers or symbols):
        raise ValueError("At least one character type must be provided")
        
    if lower:
        character_list += string.ascii_lowercase
    if upper:
        character_list += string.ascii_uppercase
    if numbers:
        character_list += string.digits
    if symbols:
        character_list += string.punctuation

    return "".join(random.choice(character_list) for i in range(length))

def get_config(emby_url, emby_api_key):
    try:
        url = f"{emby_url}/System/Configuration"
        querystring = {"api_key": emby_api_key}
        response = requests.get(url, params=querystring, timeout=5)

        # Log the raw response for debugging
        print(f"Emby API Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching config: {response.text}")
            return {}
    except Exception as e:
        print(f"Exception in get_config: {e}")
        return {}

def get_status(emby_url, emby_api_key):
    try:
        url = f"{emby_url}/System/Configuration"
        querystring = {"api_key": emby_api_key}
        response = requests.get(url, params=querystring, timeout=5)

        # Log the raw response for debugging
        print(f"Emby API Response: {response.text}")

        return response.status_code
    except Exception as e:
        print(f"Exception in get_status: {e}")
        return 500
