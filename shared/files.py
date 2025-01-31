import json

from settings import accounts_filename


def read_users_from_json(ignore_not_found=False):
    """Read users from the JSON file."""
    try:
        with open(accounts_filename, "r") as file:
            users = json.load(file)
            return users
    except FileNotFoundError:
        if ignore_not_found == False:
            print(f"Error: The file '{accounts_filename}' was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file '{accounts_filename}' is not a valid JSON.")
        raise
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        raise


def write_users_to_json(users):
    """Write the updated users list back to the JSON file."""
    try:
        with open(accounts_filename, "w") as file:
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
        users = read_users_from_json(ignore_not_found=True)

        for user in users:
            if user["username"] == username:
                return

        new_user = {
            "username": username,
            "password": password,
        }
        users.append(new_user)

        write_users_to_json(users)

    except Exception as e:
        print(f"Error inserting user: {e}")
        raise
