from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import autospotify.settings as settings
from autospotify.utils.base.automation.spotify import SpotifyBase
from autospotify.utils.logs import log
from autospotify.utils.schemas import FindElement, User

SONG_END_PERCENTAGE = 95


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

    def username_step(self):
        self.log_step("taper le username")
        username_input = WebDriverWait(self.driver, 180).until(
            EC.visibility_of_element_located((By.ID, "login-username"))
        )
        self.fill_input(username_input, self.user.username)

    def password_step(self):
        self.log_step("taper le mot de passe")
        password_input = self.driver.find_element(By.ID, "login-password")
        self.fill_input(password_input, self.user.password)

    def login_step(self):
        self.username_step()

        try:
            self.password_step()
        except NoSuchElementException:  # When spotify changes the normal login flow
            self.click(query=FindElement(by=By.ID, value="login-button"))

            try:  # If spotify is asking a code try to connect with password and email
                self.click(
                    query=FindElement(
                        by=By.XPATH, value="//*[@data-encore-id='buttonTertiary']"
                    )
                )  # Connect with password
                self.username_step()
                self.password_step()
            except NoSuchElementException:
                self.password_step()

        self.click(query=FindElement(by=By.ID, value="login-button"))

        log(
            f"✅ L'utilisateur s'est connecté avec succès : compte de {self.user.username} ! 🚀"
        )

        self.check_page_url(keyword="account/overview", step_name="se connecter")

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

                if not progress_transform:
                    raise Exception("La playlist n'a pas commencé à jouer 🎵🚫")

                percentage = float(
                    progress_transform.split("--progress-bar-transform: ")[1].split(
                        "%"
                    )[0]
                )

                if percentage >= SONG_END_PERCENTAGE:
                    sleep(30)

                    log(
                        f"🎧 Le {self.user_index}° bot a terminé d'écouter la playlist. 🎶 Merci pour l'écoute !"
                    )

                    break

            except NoSuchElementException:  # Last song is not playing
                pass

    def listening_step(self):
        self.get_page(self.track_url)

        self.choose_an_artist()  # Chose a favorite artist if asked

        if (
            "/artist" in self.driver.current_url
        ):  # Check if the user was listening to their favorite artist
            self.get_page(self.track_url)

        self.show_track_info()
        self.play(self.user_index)
        self.song_monitor()

    def action(self):
        self.login_step()
        self.listening_step()
        self.logout()
