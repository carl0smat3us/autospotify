import asyncio

from automations.spotify_playlist import SpotifyPlaylist
from automations.spotify_signup import SpotifySignup
from shared.files import read_users_from_json


def main():
    try:
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
                        print(f"Veuillez entrer un nombre superior à 0.")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")

            for i in range(num_accounts):
                print(f"Création du compte {i + 1} sur {num_accounts}...")
                spotify_signup = SpotifySignup(headless=headless)
                spotify_signup.run()

            print("\nProcessus de création de compte terminé.")

        elif action == "2":
            print("\nDémarrage de l'interaction avec la playlist Spotify...")
            playlist_url = input("Veuillez entrer l'URL de la playlist : ").strip()

            users = read_users_from_json()

            # Filter users who haven't listened to the playlist
            users_to_listen = [
                user for user in users if playlist_url not in user["listened_playlist"]
            ]

            print(
                f"\nNombre d'utilisateurs qui n'ont pas encore écouté cette playlist : {len(users_to_listen)}"
            )

            for index, user in enumerate(users_to_listen, start=1):
                print(
                    f"Utilisateur {index} sur {len(users_to_listen)} est en train d'écouter la playlist..."
                )
                asyncio.run(
                    SpotifyPlaylist(
                        username=user["username"],
                        password=user["password"],
                        playlist_url=playlist_url,
                        headless=headless,
                    ).run()
                )

            print("\nProcessus d'interaction avec la playlist terminé.")

        else:
            print("\nChoix invalide. Veuillez entrer '1' ou '2'.")

    except Exception as e:
        print(f"\nUne erreur s'est produite : {e}")


if __name__ == "__main__":
    main()
