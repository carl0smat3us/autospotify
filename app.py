import os
import random
from logging import ERROR
from time import sleep

from art import text2art
from dotenv import load_dotenv

import settings
from automations.spotify_playlist import SpotifyPlaylist
from automations.spotify_signup import SpotifySignup
from automations.webmail_login import MailLogin
from automations.webmail_signup import MailSignUp
from utils.files import read_users_from_json
from utils.logs import log
from utils.schemas import AccountFilter, User

logo = text2art("SPOTIFY")
load_dotenv()


def clean_terminal_timer():
    action = input("\nVoulez-vous effacer le terminal? (O/N): ")

    if action == "N":
        return

    print("Le terminal va être effacé en", end=" -> ")

    for c in range(9, -2, -1):
        print(c + 1, end=" ", flush=True)
        sleep(1)

    clear_terminal()


def clear_terminal():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:
        os.system("clear")


def main():
    while True:
        try:
            clear_terminal()

            print(logo)

            print(
                """
            \nQue voulez-vous faire ?
            \n1 - Créer des comptes Webmail
            \n2 - Créer des comptes Spotify
            \n3 - Activer des comptes Spotify
            \n4 - Écouter une playlist Spotify
            \n5 - Sortir de l'application
            """
            )

            action = input("Entrez votre choix: ").strip()

            if action == "1":
                print("\nDémarrage de la création de compte Webmail...")

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
                    log(f"Création du compte {i + 1} sur {num_accounts}...")
                    webmail_signup = MailSignUp()
                    webmail_signup.run()

                clean_terminal_timer()

            elif action == "2":
                print("\nDémarrage de la création de compte Spotify...")

                users = read_users_from_json(
                    settings.webmail_accounts_path,
                    AccountFilter(mail_account_used="no"),
                )

                # Verifica se há usuários disponíveis
                if not users:
                    print(
                        "Aucun utilisateur trouvé dans le fichier JSON. Opération annulée."
                    )
                else:
                    for i in range(users):
                        log(f"Activation du compte {i + 1} sur {len(users)}...")

                        user = users[i]

                        mail_login = MailLogin(user)
                        mail_login.run()

                clean_terminal_timer()

            elif action == "3":
                print("\nDémarrage de la activation de compte Spotify...")

                users = read_users_from_json(
                    settings.spotify_accounts_path,
                    AccountFilter(spotify_account_confirmed="no"),
                )

                # Verifica se há usuários disponíveis
                if not users:
                    print(
                        "Aucun utilisateur trouvé dans le fichier JSON. Opération annulée."
                    )
                else:
                    while True:
                        try:
                            num_accounts = int(
                                input(
                                    f"Combien de comptes voulez-vous créer ? (1/{len(users)}) : "
                                ).strip()
                            )
                            if 1 <= num_accounts <= len(users):
                                break
                            else:
                                print(
                                    f"Veuillez entrer un nombre entre 1 et {len(users)}."
                                )
                        except ValueError:
                            print("Veuillez entrer un nombre valide.")

                    for i in range(num_accounts):
                        log(f"Création du compte {i + 1} sur {num_accounts}...")

                        user = users[i]

                        spotify_signup = SpotifySignup(user)
                        spotify_signup.run()

                clean_terminal_timer()

            elif action == "3":
                print("\nDémarrage de l'interaction avec la playlist Spotify...")
                track_url = input("Veuillez entrer l'URL de la playlist : ").strip()

                users = read_users_from_json(settings.spotify_accounts_path)

                compte_nombre = 0

                log(f"🌟 URL de la playlist choisie : {track_url} 🎵")

                sleep(3)

                print("La lecture de la playlist va être faite infiniment ♾️\n")

                if len(users) >= 1:
                    while True:
                        users_index = random.randint(0, len(users) - 1)
                        user = users[users_index]

                        log(
                            f"Lecture de la playlist pour la {compte_nombre + 1}ᵉ fois."
                        )

                        spotify_playlist = SpotifyPlaylist(
                            user=User(
                                username=user.username,
                                password=user.password,
                            ),
                            track_url=track_url,
                            user_index=users_index + 1,
                        )
                        spotify_playlist.run()
                        compte_nombre += 1

                clean_terminal_timer()

            elif action == "4":
                break
            else:
                print("\nChoix invalide.")
                sleep(2)

        except KeyboardInterrupt:
            log("🛑 Le script a été arrêté manuellement. ⏹️", ERROR)
            break

    print("\nProcessus terminé.")


if __name__ == "__main__":
    main()
