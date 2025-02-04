import time

import keyboard
from faker import Faker
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

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
        headless=False,
    ):
        super().__init__(username=username, password=password, headless=headless)
        self.url = settings.spotify_login_url
        self.track_url = track_url
        self.user_index = user_index

    def login(self):
        username_input = self.driver.find_element(By.ID, "login-username")
        username_input.send_keys(self.username)

        password_input = self.driver.find_element(By.ID, "login-password")
        password_input.send_keys(self.password)

        login_button = self.driver.find_element(By.ID, "login-button")
        self.submit(login_button, self.delay_page_loading)

        log_message(f"Connexion en cours : compte de {self.username} !")

    def action(self):
        self.login()
        self.get_page(self.track_url)

        keyboard.send("esc")

        time.sleep(5)

        self.choose_an_artist()  # Chose a favorite artist if Spotify asks

        time.sleep(5)

        if (
            "/artist" in self.driver.current_url
        ):  # If user was listening to them favorite artist
            self.get_page(self.track_url)

        self.show_track_info()
        self.play(self.user_index)
        self.monitor()

    def show_track_info(self):
        self.title = self.driver.find_element(
            By.XPATH, '//*[@data-testid="entityTitle"]/h1'
        )

        log_message(f"🎶 Les bots écoutent la playlist : {self.title.text} 🎧")

    def monitor(self):
        """Continuously monitor the last song's progress and play state."""
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

                if percentage > 90:
                    log_message(
                        f"🎧 Le {self.user_index}° bot a terminé d'écouter la playlist. 🎶 Merci pour l'écoute !"
                    )

                    break

            except NoSuchElementException:  # Last song is not playing
                pass
