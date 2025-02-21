import os

from selenium.common.exceptions import InvalidSessionIdException

import autospotify.settings as settings


def create_config_folder():
    if not os.path.exists(settings.app_folder):  # Create root folder
        os.mkdir(settings.app_folder)

    if not os.path.exists(settings.logs_folder):
        os.mkdir(settings.logs_folder)

    if not os.path.exists(settings.logs_screenshots_folder):
        os.mkdir(settings.logs_screenshots_folder)


create_config_folder()

import random
from logging import ERROR
from time import sleep

from art import text2art
from dotenv import load_dotenv

from autospotify.automations.spotify_playlist import SpotifyPlaylist
from autospotify.automations.spotify_signup import SpotifySignup
# from autospotify.automations.webmail_signup import MailSignUp
from autospotify.automations.webmail_login import MailLogin
from autospotify.utils.files import (read_user_from_json, read_users_from_json,
                                     upsert_user)
from autospotify.utils.logs import log
from autospotify.utils.schemas import AccountFilter, User
from faker import Faker

faker = Faker()

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


def add_webmail_accounts():
    while True:
        print()
        username = input("📧 Entrez l'email : ").strip()
        password = input("🔑 Entrez le mot de passe : ").strip()

        if not username:
            break

        if not password:
            password = faker.password(
                length=15,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            )

        action = input("\n✅ Voulez-vous confirmer l'ajout du compte ? (O/N) : ")

        if action.upper() == "N":
            print("❌ Ajout annulé.")
            break

        user = read_user_from_json(username)

        if user:
            print("⚠️ Cet utilisateur existe déjà !")
        else:
            upsert_user(user=User(username=username, password=password))
            print("✅ Utilisateur ajouté avec succès !")

        action = input("\n➕ Voulez-vous ajouter un autre compte ? (O/N) : ")

        if action.upper() == "N":
            print("👋 Fin du processus d'ajout.")
            clean_terminal_timer()
            break

        clean_terminal_timer()


def clear_terminal():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:
        os.system("clear")


def main():
    clear_terminal()

    while True:
        try:
            print(logo)

            print(
                """
            \nQue voulez-vous faire ?
            \n1 - Ajouter des emails
            \n2 - Créer des comptes Spotify
            \n3 - Écouter une playlist Spotify
            \n4 - Sortir de l'application
            """
            )

            action = input("Entrez votre choix: ").strip()

            if action == "1":
                add_webmail_accounts()
                # print("\nDémarrage de la création de compte Webmail...")

                # while True:
                #     try:
                #         num_accounts = int(
                #             input(f"Combien de comptes voulez-vous créer ?: ").strip()
                #         )
                #         if 1 <= num_accounts:
                #             break
                #         else:
                #             print(f"Veuillez entrer un nombre supérieur à 0.")
                #     except ValueError:
                #         print("Veuillez entrer un nombre valide.")

                # for i in range(num_accounts):
                #     log(f"Création du compte {i + 1} sur {num_accounts}...")
                #     webmail_signup = MailSignUp()
                #     webmail_signup.run()

                # clean_terminal_timer()

            elif action == "2":
                print("\nDémarrage de la création de compte Spotify...")

                users = read_users_from_json(
                    filters=AccountFilter(spotify_account_created="no"),
                )

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
                users = read_users_from_json(
                    filters=AccountFilter(spotify_account_created="yes"),
                )

                if not users:
                    print(
                        "Aucun utilisateur trouvé dans le fichier JSON. Opération annulée."
                    )
                else:
                    track_url = input("Veuillez entrer l'URL de la playlist : ").strip()

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
                                user=user,
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

        except InvalidSessionIdException:
            log("⚠️ Session invalide.", ERROR)
            break

        except KeyboardInterrupt:
            log("🛑 Le script a été arrêté manuellement. ⏹️", ERROR)
            break

    print("\nProcessus terminé.")


if __name__ == "__main__":
    main()