import requests
import random
import string
import json

def add_user(authentik_url, authentik_api_token, username, password):
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
            "groups": []  # Add groups if needed
        }
        response = requests.post(url, json=payload, headers=headers)

        # Log the raw response for debugging
        print(f"Authentik API Response (Create User): {response.text}")

        if response.status_code != 201:
            print(f"Error creating new Authentik user: {response.text}")
            return False

        return True

    except Exception as e:
        print(f"Exception in add_user: {e}")
        return False

def remove_user(authentik_url, authentik_api_token, username):
    try:
        # Step 1: Get the user ID from Authentik
        url = f"{authentik_url}/api/v3/core/users/?username={username}"
        headers = {
            "Authorization": f"Bearer {authentik_api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)

        # Log the raw response for debugging
        print(f"Authentik API Response (Get User): {response.text}")

        if response.status_code != 200:
            print(f"Error fetching user details: {response.text}")
            return False

        user_data = response.json()
        if not user_data.get("results"):
            print(f"User {username} not found in Authentik.")
            return False

        user_id = user_data["results"][0]["id"]

        # Step 2: Delete the user from Authentik
        url = f"{authentik_url}/api/v3/core/users/{user_id}/"
        response = requests.delete(url, headers=headers)

        # Log the raw response for debugging
        print(f"Authentik API Response (Delete User): {response.text}")

        if response.status_code == 204:
            return True
        else:
            print(f"Error deleting Authentik user: {response.text}")
            return False

    except Exception as e:
        print(f"Exception in remove_user: {e}")
        return False

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
