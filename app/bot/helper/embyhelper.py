import requests
import random
import string

def add_user(emby_url, emby_api_key, username, password, emby_libs):
    try:
        # Create a new user
        url = f"{emby_url}/Users/New"
        querystring = {"api_key": emby_api_key}
        payload = {
            "Name": username,
            "Password": password
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, params=querystring)

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

        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            print(f"Error setting user permissions: {response.text}")
            return False

    except Exception as e:
        print(f"Error in add_user: {e}")
        return False


def get_libraries(emby_url, emby_api_key):
    url = f"{emby_url}/Library/VirtualFolders"
    querystring = {"api_key": emby_api_key}
    response = requests.get(url, params=querystring)

    return response.json()


def verify_username(emby_url, emby_api_key, username):
    users = get_users(emby_url, emby_api_key)
    valid = True
    for user in users:
        if user['Name'] == username:
            valid = False
            break

    return valid


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

        if response.status_code == 204 or response.status_code == 200:
            return True
        else:
            print(f"Error deleting Emby user: {response.text}")
            return False

    except Exception as e:
        print(f"Error in remove_user: {e}")
        return False


def get_users(emby_url, emby_api_key):
    url = f"{emby_url}/Users"
    querystring = {"api_key": emby_api_key}
    response = requests.get(url, params=querystring)

    return response.json()


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

    return "".join(random.choice(character_list) for _ in range(length))


def get_config(emby_url, emby_api_key):
    url = f"{emby_url}/System/Configuration"
    querystring = {"api_key": emby_api_key}
    response = requests.get(url, params=querystring, timeout=5)
    return response.json()


def get_status(emby_url, emby_api_key):
    url = f"{emby_url}/System/Configuration"
    querystring = {"api_key": emby_api_key}
    response = requests.get(url, params=querystring, timeout=5)
    return response.status_code
