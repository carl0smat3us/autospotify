from os import path
from tempfile import gettempdir

app_folder = path.join(path.expanduser("~"), "Documents", "AutoSpotify")

accounts_path = path.join(app_folder, "accounts.json")

proxies_path = path.join(app_folder, "proxies.txt")

extensions_path = gettempdir()

logs_folder = path.join(app_folder, "logs")

logs_screenshots_folder = path.join(logs_folder, "screenshots")

log_filename = "app.log"

logging_datefmt = "%Y-%m-%d %H:%M:%S"

venv_dir = ".venv"

webmail_signup_url = "https://signup.mail.com/"

webmail_login_url = "https://www.mail.com/"

spotify_login_url = "https://www.spotify.com/login"

spotify_signup_url = "https://www.spotify.com/signup"

proton_signup_url = (
    "https://account.proton.me/mail/signup?plan=free&ref=mail_plus_intro-mailpricing-2"
)

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
