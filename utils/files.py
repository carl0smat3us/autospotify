import json
from logging import ERROR
from typing import List, Literal

import settings
from utils.logs import log
from utils.proxies import transform_proxy
from utils.schemas import AccountFilter, User


def read_proxies_from_txt():
    """Read proxies from a TXT file and return them as a list."""
    try:
        with open(settings.proxies_path, "r") as file:
            proxies_result = file.readlines()

        proxies = [
            transform_proxy(line.strip()) for line in proxies_result if line.strip()
        ]

        return proxies

    except FileNotFoundError:
        return []
    except Exception as e:
        log(f"Error reading TXT file: {e}", ERROR)
        return []


def read_users_from_json(path: str, filters: AccountFilter) -> List[User]:
    """Read users from the JSON file."""
    try:
        final_users = []
        users = json.load(path)

        if filters and isinstance(filters, dict):
            for user in users:
                if all(user.get(k) == v for k, v in filters.items()):
                    final_users.append(User(**user))
        else:
            final_users = [User(**user) for user in users]

            return final_users
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        log(f"Error: The file '{path}' is not a valid JSON.", ERROR)
        raise
    except Exception as e:
        log(f"Error reading JSON file: {e}", ERROR)
        raise


def write_users_to_json(users: list, path: str):
    """Write the updated users list back to the JSON file."""
    try:
        with open(path, "w") as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        log(f"Error writing to JSON file: {e}", ERROR)
        raise


import json
from typing import List, Literal


class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email  # Add more fields as needed

    def to_dict(self):
        return {"username": self.username, "email": self.email}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


def read_users_from_json(path: str) -> List[User]:
    try:
        with open(path, "r") as file:
            data = json.load(file)
            return [User.from_dict(user) for user in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_users_to_json(users: List[User], path: str):
    with open(path, "w") as file:
        json.dump([user.to_dict() for user in users], file, indent=4)


def upsert_user(user: User, path: str, user_type: Literal["spotify", "webmail"]):
    """
    Insert a new user into the JSON file.
    If the user already exists, update their information.
    """
    try:
        users = read_users_from_json(path)
        user_found = False

        for i, existing_user in enumerate(users):
            if existing_user.username == user.username:
                users[i] = user
                user_found = True
                break

        if not user_found:
            users.append(user)

        write_users_to_json(users, path)
        action = "mis à jour" if user_found else "généré"
        log(f"Le compte {user.username} {user_type} a été {action}.")

    except Exception as e:
        log(f"Error inserting/updating user: {e}", ERROR)
        raise e
