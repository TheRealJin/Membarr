import requests
import random
import string
import json

def add_user(authentik_url, authentik_api_token, username, password, groups=None):
    try:
        # Step 1: Create new Authentik user
        url = f"{authentik_url}/api/v3/core/users/"
        headers = {
            "Authorization": f"Bearer {authentik_api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "username": username,
            "name": username,
            "email": f"{username}@example.com",  # You can modify this as needed
            "password": password,
            "groups": groups if groups else []
        }
        response = requests.post(url, json=payload, headers=headers)

        # Log the raw response for debugging
        print(f"Authentik API Response (Create User): {response.text}")

        if response.status_code != 201:
            print(f"Error creating new Authentik user: {response.text}")
            return False

        user_id = response.json()["id"]

        # Step 2: Verify the user was created
        url = f"{authentik_url}/api/v3/core/users/{user_id}/"
        response = requests.get(url, headers=headers)

        # Log the raw response for debugging
        print(f"Authentik API Response (Verify User): {response.text}")

        if response.status_code != 200:
            print(f"Error fetching user details: {response.text}")
            return False

        user_details = response.json()
        if user_details.get("username") != username:
            print(f"User {username} was not created correctly.")
            return False

        return True

    except Exception as e:
        print(f"Exception in add_user: {e}")
        return False

def get_users(authentik_url, authentik_api_token):
    try:
        url = f"{authentik_url}/api/v3/core/users/"
        headers = {
            "Authorization": f"Bearer {authentik_api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)

        # Log the raw response for debugging
        print(f"Authentik API Response: {response.text}")

        if response.status_code == 200:
            return response.json()["results"]
        else:
            print(f"Error fetching users: {response.text}")
            return []
    except Exception as e:
        print(f"Exception in get_users: {e}")
        return []

def verify_username(authentik_url, authentik_api_token, username):
    try:
        users = get_users(authentik_url, authentik_api_token)
        for user in users:
            if user['username'] == username:
                return False
        return True
    except Exception as e:
        print(f"Exception in verify_username: {e}")
        return False

def remove_user(authentik_url, authentik_api_token, username):
    try:
        # Get User ID
        users = get_users(authentik_url, authentik_api_token)
        user_id = None
        for user in users:
            if user['username'].lower() == username.lower():
                user_id = user['id']
        
        if user_id is None:
            # User not found
            print(f"Error removing user {username} from Authentik: Could not find user.")
            return False
        
        # Delete User
        url = f"{authentik_url}/api/v3/core/users/{user_id}/"
        headers = {
            "Authorization": f"Bearer {authentik_api_token}",
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers=headers)

        # Log the raw response for debugging
        print(f"Authentik API Response: {response.text}")

        if response.status_code == 204:
            return True
        else:
            print(f"Error deleting Authentik user: {response.text}")
            return False
    except Exception as e:
        print(f"Exception in remove_user: {e}")
        return False

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

def get_config(authentik_url, authentik_api_token):
    try:
        url = f"{authentik_url}/api/v3/core/config/"
        headers = {
            "Authorization": f"Bearer {authentik_api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=5)

        # Log the raw response for debugging
        print(f"Authentik API Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching config: {response.text}")
            return {}
    except Exception as e:
        print(f"Exception in get_config: {e}")
        return {}

def get_status(authentik_url, authentik_api_token):
    try:
        url = f"{authentik_url}/api/v3/core/health/"
        headers = {
            "Authorization": f"Bearer {authentik_api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=5)

        # Log the raw response for debugging
        print(f"Authentik API Response: {response.text}")

        return response.status_code
    except Exception as e:
        print(f"Exception in get_status: {e}")
        return 500
