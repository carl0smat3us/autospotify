import asyncio
import os

from automations.spotify_playlist import SpotifyPlaylist
from automations.spotify_signup import SpotifySignup
from settings import accounts_filename
from shared.files import read_users_from_csv


def main():
    try:
        print("Bienvenue dans le CLI d'automatisation Spotify !")
        action = (
            input(
                "Voulez-vous créer un compte ou écouter une playlist ? (creer/ecouter) : "
            )
            .strip()
            .lower()
        )

        if action == "creer":
            print("\nDémarrage de la création de compte Spotify...")
            headless = (
                input(
                    "Voulez-vous exécuter en mode sans interface graphique ? (oui/non) : "
                )
                .strip()
                .lower()
                == "oui"
            )

            max_accounts = 10
            while True:
                try:
                    num_accounts = int(
                        input(
                            f"Combien de comptes voulez-vous créer ? (1-{max_accounts}) : "
                        ).strip()
                    )
                    if 1 <= num_accounts <= max_accounts:
                        break
                    else:
                        print(f"Veuillez entrer un nombre entre 1 et {max_accounts}.")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")

            for i in range(num_accounts):
                print(f"Création du compte {i + 1} sur {num_accounts}...")
                spotify_signup = SpotifySignup(headless=headless)
                spotify_signup.run()

            print("\nProcessus de création de compte terminé.")

        elif action == "ecouter":
            print("\nDémarrage de l'interaction avec la playlist Spotify...")
            users = read_users_from_csv(os.path.join(os.getcwd(), accounts_filename))

            for user in users:
                if user.get("listened", "non").lower() == "non":
                    print(
                        f"L'utilisateur {user['username']} n'a pas encore écouté la playlist. Actions en cours sur la playlist."
                    )

                    asyncio.run(
                        SpotifyPlaylist(user["username"], user["password"]).run()
                    )
                else:
                    print(
                        f"L'utilisateur {user['username']} a déjà écouté la playlist. Interaction avec la playlist ignorée."
                    )

            print("\nProcessus d'interaction avec la playlist terminé.")

        else:
            print("\nChoix invalide. Veuillez entrer 'creer' ou 'ecouter'.")

    except Exception as e:
        print(f"\nUne erreur s'est produite : {e}")


if __name__ == "__main__":
    main()
