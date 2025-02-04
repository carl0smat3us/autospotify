from os import path

accounts_file_path = "accounts.json"
proxies_file_path = "proxies.txt"

logs_paths = {"root": "logs", "screenshot": path.join("logs", "screenshot")}
logs_file = "app.log"

logging_datefmt="%Y-%m-%d %H:%M:%S"

venv_dir = ".venv"

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

spotify_supported_domains = [
    "proton.me",
    "gmail.com",
    "outlook.com",
    "outlook.be",
    "free.fr",
    "icloud.com",
]

spotify_favorits_artists = [
    "Post Malone",
    "Gims",
    "Portugal Man",
    "Kendrick Lamar",
    "Eminem",
    "Justin Bieber",
]
