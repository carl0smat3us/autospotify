import csv

from settings import accounts_filename


def read_users_from_csv():
    users = []
    try:
        with open(accounts_filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(
                    {
                        "username": row["username"],
                        "password": row["password"],
                        "listened": row["listened"],
                    }
                )
    except FileNotFoundError:
        print(f"Error: The file '{accounts_filename}' was not found.")
        raise
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise
    return users


def add_user_to_csv(username, password):
    try:
        file_exists = False
        try:
            with open(accounts_filename, "r") as file:
                file_exists = True
        except FileNotFoundError:
            pass

        with open(accounts_filename, "a", newline="") as file:
            fieldnames = ["username", "password", "listened"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(
                {
                    "username": username,
                    "password": password,
                    "listened": "no",
                }
            )

        print(f"User '{username}' added successfully.")
    except FileNotFoundError:
        print(f"Error: The file '{accounts_filename}' was not found.")
        raise
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        raise
