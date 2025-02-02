import asyncio
import os
import random

from automations.spotify_playlist import SpotifyPlaylist
from automations.spotify_signup import SpotifySignup
from shared.files import read_users_from_json


def clear_terminal():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:
        os.system("clear")


def main():
    try:
        clear_terminal()

        print("Bienvenue dans le CLI d'automatisation Spotify !")

        headless = (
            input(
                "Voulez-vous exécuter en mode sans interface graphique ? (1: Oui, 2: Non) : "
            )
            .strip()
            .lower()
            == "1"
        )

        print("\nQue voulez-vous faire ?")
        print("1 - Créer des comptes Spotify")
        print("2 - Écouter une playlist Spotify")

        action = input("Entrez votre choix (1/2) : ").strip()

        if action == "1":
            print("\nDémarrage de la création de compte Spotify...")

            while True:
                try:
                    num_accounts = int(
                        input(f"Combien de comptes voulez-vous créer ?: ").strip()
                    )
                    if 1 <= num_accounts:
                        break
                    else:
                        print(f"Veuillez entrer un nombre supérieur à 0.")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")

            for i in range(num_accounts):
                print(f"\nCréation du compte {i + 1} sur {num_accounts}...")
                spotify_signup = SpotifySignup(headless=headless)
                spotify_signup.run()

        elif action == "2":
            print("\nDémarrage de l'interaction avec la playlist Spotify...")
            playlist_url = input("Veuillez entrer l'URL de la playlist : ").strip()

            users = read_users_from_json()

            random.shuffle(users)

            while True:
                try:
                    concurrent_executions = int(
                        input(
                            f"Combien d'exécutions simultanées voulez-vous ? (1 à {len(users)}): "
                        ).strip()
                    )
                    if 1 <= concurrent_executions <= len(users):
                        break
                    else:
                        print(f"Veuillez entrer un nombre entre 1 et {len(users)}.")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")

            for index in range(0, len(users), concurrent_executions):
                tasks = []
                for j in range(concurrent_executions):
                    if index + j < len(users):
                        user = users[index + j]

                        print(f"\n({index + j + 1}/{len(users)})")

                        spotify_playlist = SpotifyPlaylist(
                            username=user["username"],
                            password=user["password"],
                            playlist_url=playlist_url,
                            user_index=users.index(user) + 1,
                            headless=headless,
                        )
                        tasks.append(spotify_playlist.run())
                asyncio.gather(*tasks)
        else:
            print("\nChoix invalide. Veuillez entrer '1' ou '2'.")

        print("Processus terminé.")

    except Exception as e:
        print(f"\nUne erreur s'est produite : {e}")


if __name__ == "__main__":
    main()
