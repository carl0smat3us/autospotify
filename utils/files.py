import json
from logging import ERROR
from typing import List, Literal

import settings
from utils.logs import log
from utils.proxies import transform_proxy
from utils.schemas import AccountFilter, User


def read_proxies_from_txt():
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


def read_users_from_json(path: str, filters: AccountFilter = {}) -> List[User]:
    try:
        final_users = []

        with open(path, "r", encoding="utf-8") as file:
            users = json.load(file)

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


def write_users_to_json(users: List[User], path: str):
    with open(path, "w") as file:
        json.dump([user.to_dict() for user in users], file, indent=4)


def upsert_user(user: User, path: str, user_type: Literal["spotify", "webmail"]):
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
        raise
