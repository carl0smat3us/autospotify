from os import path

spotify_accounts_path = "spotify.accounts.json"
webmail_accounts_path = "webmail.accounts.json"

proxies_path = "proxies.txt"

logs_paths = {"root": "logs", "screenshots": path.join("logs", "screenshots")}
logs_file = "app.log"

logging_datefmt = "%Y-%m-%d %H:%M:%S"

venv_dir = ".venv"

webmail_signup_url = "https://signup.mail.com/"

webmail_login_url = "https://www.mail.com/"

spotify_login_url = "https://www.spotify.com/login"

spotify_signup_url = "https://www.spotify.com/signup"

spotify_supported_languages = [
    "en-US",
    "en-GB",
    "en-CA",
    "fr-FR",
    "de-DE",
    "es-ES",
    "it-IT",
    "ja-JP",
    "ko-KR",
    "pt-BR",
    "ru-RU",
    "nl-NL",
    "sv-SE",
    "da-DK",
    "no-NO",
]

spotify_favorits_artists = [
    "Post Malone",
    "Kendrick Lamar",
    "Justin Bieber",
]
