import random
import time

import keyboard
from faker import Faker
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import settings
from utils.base import Base
from utils.logs import log_message

faker = Faker()


class SpotifyPlaylist(Base):
    def __init__(
        self,
        username: str,
        password: str,
        track_url: str,
        user_index: int,
    ):
        super().__init__(username=username, password=password)
        self.url = settings.spotify_login_url
        self.track_url = track_url
        self.user_index = user_index

    def login_step(self):
        username_input = WebDriverWait(self.driver, 180).until(
            EC.visibility_of_element_located((By.ID, "login-username"))
        )
        username_input.send_keys(self.username)

        password_input = self.driver.find_element(By.ID, "login-password")
        password_input.send_keys(self.password)

        login_button = self.driver.find_element(By.ID, "login-button")
        self.submit(login_button, self.delay_page_loading)

        self.verify_page_url("se connecter", "account/overview")
        log_message(
            f"✅ L'utilisateur s'est connecté avec succès : compte de {self.username} ! 🚀"
        )

    def show_track_info(self):
        self.title = self.driver.find_element(
            By.XPATH, '//*[@data-testid="entityTitle"]/h1'
        )

        log_message(f"🎶 Les bots écoutent la playlist : {self.title.text} 🎧")

    def song_monitor(self):
        """Continuously monitor the last song's progress and play state."""
        log_message("🎵 Surveillance de la playlist en cours de lecture 🎧")

        playlist_songs = self.driver.find_element(
            By.XPATH,
            "//div[@role='row' and (@aria-selected='true' or @aria-selected='false')]",
        ).find_element(By.XPATH, "..")

        progress_bar = self.driver.find_element(
            By.XPATH, '//*[@data-testid="progress-bar"]'
        )

        while True:
            try:
                last_song = playlist_songs.find_element(
                    By.XPATH, './div[@role="row"][last()]'
                )
            except:  # Playlist is too large to find the last song.
                time.sleep(5)
                continue

            try:
                # Check if the last song is playing
                last_song.find_element(By.XPATH, './/button[@aria-label="Pause"]')

                progress_transform = progress_bar.get_attribute("style")

                percentage = float(
                    progress_transform.split("--progress-bar-transform: ")[1].split(
                        "%"
                    )[0]
                )

                if percentage > 95:
                    log_message(
                        f"🎧 Le {self.user_index}° bot a terminé d'écouter la playlist. 🎶 Merci pour l'écoute !"
                    )

                    break

            except NoSuchElementException:  # Last song is not playing
                pass

    def listen_to_random_artist(self):
        search_bar = self.driver.find_element(
            By.XPATH,
            "//*[@data-testid='search-input']",
        )

        random_artist = random.choice(settings.spotify_favorits_artists)

        search_bar.send_keys(random_artist)

        time.sleep(self.delay_page_loading)

        # time.sleep(500)

        first_artist = self.driver.find_element(
            By.XPATH,
            "//div[@data-testid='infinite-scroll-list']//span[@role='presentation']",
        )

        self.submit(element=first_artist, delay=10, use_javascript=False)

        self.verify_page_url("recherche d'un chanteur aléatoire", "artist")

        self.play()

        time.sleep(10)

    def choose_an_artist(self):
        try:  # Check if Spotify displays a pop-up asking to choose favorite artists
            self.driver.find_element(
                By.XPATH,
                '//*[@data-testid="popover"]//div[contains(@class, "encore-announcement-set")]',
            )

            log_message("Spotify a demandé au bot de choisir son chanteur préféré 🤖🎤")
        except NoSuchElementException:
            return

        self.listen_to_random_artist()

    def open_playlist(self):
        self.get_page(self.track_url)
        keyboard.send("esc")
        time.sleep(5)

    def listening_step(self):
        self.open_playlist()

        self.choose_an_artist()  # Chose a favorite artist if Spotify asks

        if (
            "/artist" in self.driver.current_url
        ):  # If user was listening to them favorite artist
            self.open_playlist()

        self.show_track_info()
        self.play(self.user_index)
        self.song_monitor()

    def action(self):
        self.login_step()
        self.listening_step()
