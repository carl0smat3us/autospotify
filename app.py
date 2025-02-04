import os
import random

from automations.spotify_playlist import SpotifyPlaylist
from automations.spotify_signup import SpotifySignup
from utils.files import read_users_from_json
from utils.logs import logger


def clear_terminal():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:
        os.system("clear")


def main():
    try:
        clear_terminal()

        print("Bienvenue dans le CLI d'automatisation Spotify !")

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
                spotify_signup = SpotifySignup()
                spotify_signup.run()

        elif action == "2":
            print("\nDémarrage de l'interaction avec la playlist Spotify...")
            track_url = input("Veuillez entrer l'URL de la playlist : ").strip()

            users = read_users_from_json()

            compte_nombre = 0

            print("\nLa lecture de la playlist va être faite infiniment ♾️\n")

            if len(users) >= 1:
                while True:
                    users_index = random.randint(0, len(users) - 1)
                    user = users[users_index]

                    print(
                        f"\nLecture de la playlist pour la {compte_nombre + 1}ᵉ fois."
                    )

                    spotify_playlist = SpotifyPlaylist(
                        username=user["username"],
                        password=user["password"],
                        track_url=track_url,
                        user_index=users_index + 1,
                    )
                    spotify_playlist.run()
                    compte_nombre += 1
        else:
            print("\nChoix invalide. Veuillez entrer '1' ou '2'.")

        print("Processus terminé.")

    except KeyboardInterrupt:
        print("\n🛑 Le script a été arrêté manuellement. ⏹️")

    except Exception as e:
        logger.error(f"Une erreur s'est produite : {e}")


if __name__ == "__main__":
    main()
