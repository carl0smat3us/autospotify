import random
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import settings
from utils.base.automation.spotify import SpotifyBase
from utils.logs import log
from utils.schemas import FindElement, User


class SpotifyPlaylist(SpotifyBase):
    def __init__(
        self,
        user: User,
        track_url: str,
        user_index: int,
    ):
        super().__init__(user=user, base_url=settings.spotify_login_url)
        self.track_url = track_url
        self.user_index = user_index

    def login_step(self):
        username_input = WebDriverWait(self.driver, 180).until(
            EC.visibility_of_element_located((By.ID, "login-username"))
        )
        self.fill_input(username_input, self.user.username)

        password_input = self.driver.find_element(By.ID, "login-password")
        self.fill_input(password_input, self.user.password)

        self.click(query=FindElement(by=By.ID, value="login-button"))

        self.check_page_url(keyword="account/overview", step_name="se connecter")

        log(
            f"✅ L'utilisateur s'est connecté avec succès : compte de {self.user.username} ! 🚀"
        )

    def show_track_info(self):
        self.title = self.driver.find_element(
            By.XPATH, '//*[@data-testid="entityTitle"]/h1'
        )

        log(f"🎶 Les bots écoutent la playlist : {self.title.text} 🎧")

    def song_monitor(self):
        """Continuously monitor the last song's progress and play state."""
        log("🎵 Surveillance de la playlist en cours de lecture 🎧")

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
                sleep(5)
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

                if percentage >= 5:
                    sleep(30)

                    log(
                        f"🎧 Le {self.user_index}° bot a terminé d'écouter la playlist. 🎶 Merci pour l'écoute !"
                    )

                    break

            except NoSuchElementException:  # Last song is not playing
                pass

    def listen_to_random_artist(self):
        self.log_step("sélection d'un artiste préféré 🎨✨")

        random_artist = random.choice(settings.spotify_favorits_artists)

        search_bar = WebDriverWait(self.driver, 180).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@data-testid='search-input']")
            )
        )
        self.fill_input(search_bar, random_artist)

        if search_bar.get_attribute("value").strip() != random_artist.strip():
            raise ValueError(
                f"❌ Erreur : la saisie ne correspond pas à {random_artist} ! 🔄🎵"
            )

        sleep(self.delay_page_loading)

        self.submit_form(
            element=FindElement(
                by=By.XPATH,
                value="//div[@data-testid='infinite-scroll-list']//span[@role='presentation']",
            ),
            use_javascript=False,
        )

        self.check_page_url(keyword="artist")

        self.play()

    def choose_an_artist(self):
        try:  # Check if Spotify displays a pop-up asking to choose favorite artists
            self.driver.find_element(
                By.XPATH,
                '//*[@data-testid="popover"]//div[contains(@class, "encore-announcement-set")]',
            )

            log("L'application a demandé au bot de choisir son chanteur préféré 🤖🎤")
        except NoSuchElementException:
            return

        self.listen_to_random_artist()

    def open_playlist(self):
        self.get_page(self.track_url)

        for _ in range(5):  # Ensure that the App Link Prompt is being closed
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            sleep(2)

        sleep(5)

    def listening_step(self):
        self.open_playlist()

        self.choose_an_artist()  # Chose a favorite artist if asked

        if (
            "/artist" in self.driver.current_url
        ):  # Check if the user was listening to their favorite artist
            self.open_playlist()

        self.show_track_info()
        self.play(self.user_index)
        self.song_monitor()

    def action(self):
        self.login_step()
        self.listening_step()
