import asyncio
import csv
import os

from automations.spotify_playlist import SpotifyPlaylist
from automations.spotify_signup import SpotifySignup
from settings import accounts_filename, spotify_track_url


def read_users_from_csv(file_path):
    users = []
    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(
                    {
                        "email": row["email"],
                        "password": row["password"],
                        "created": row["created"],
                        "listened_to_playlist": row["listened_to_playlist"],
                    }
                )
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise
    return users


async def main(email, password):
    spotify_signup = SpotifySignup(email=email, password=password, headless=False)
    await spotify_signup.run()

    spotify_playlist = SpotifyPlaylist(email=email, password=password, headless=False)
    await spotify_playlist.run()


if __name__ == "__main__":
    try:
        users = read_users_from_csv(os.path.join(os.getcwd(), accounts_filename))

        for user in users:
            if user["created"].lower() == "no":
                print(f"Creating account for {user['email']}...")
                asyncio.run(main(user["email"], user["password"], spotify_track_url))
            else:
                print(
                    f"Account already created for {user['email']}, skipping account creation."
                )

                if user["listened_to_playlist"].lower() == "no":
                    print(
                        f"User {user['email']} has not listened to the playlist. Performing actions on the playlist."
                    )

                    """
                    SpotifyPlaylist(
                        user["email"], user["password"], spotify_track_url
                    ).run()
                    """
                    asyncio.run(SpotifyPlaylist(user["email"], user["password"]).run())
                else:
                    print(
                        f"User {user['email']} has already listened to the playlist. Skipping playlist interaction."
                    )
    except Exception as e:
        print(f"An error occurred: {e}")
