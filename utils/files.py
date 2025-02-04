import json

import settings
from utils.logs import log_message
from utils.proxies import transform_proxy


def read_proxies_from_txt():
    """Read proxies from a TXT file and return them as a list."""
    try:
        with open(settings.proxies_file_path, "r") as file:
            proxies_result = file.readlines()

        proxies = [
            transform_proxy(line.strip()) for line in proxies_result if line.strip()
        ]

        return proxies

    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return []


def read_users_from_json():
    """Read users from the JSON file."""
    try:
        with open(settings.accounts_file_path, "r") as file:
            users = json.load(file)
            return users
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error: The file '{settings.accounts_file_path}' is not a valid JSON.")
        raise
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        raise


def write_users_to_json(users):
    """Write the updated users list back to the JSON file."""
    try:
        with open(settings.accounts_file_path, "w") as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        raise


def insert_user_to_json(username, password):
    """
    Insert a new user into the JSON file.
    If the user already exists, this function does nothing.
    """
    try:
        users = read_users_from_json()

        for user in users:
            if user["username"] == username:
                return

        new_user = {
            "username": username,
            "password": password,
        }
        users.append(new_user)

        write_users_to_json(users)

        log_message(f"Le compte {username} spotify a etait generé.")

    except Exception as e:
        print(f"Error inserting user: {e}")
        raise
