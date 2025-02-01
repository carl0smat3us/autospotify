import time

import keyboard
from faker import Faker
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import settings
from shared.base import Base

faker = Faker()


class SpotifyPlaylist(Base):
    def __init__(
        self,
        username: str,
        password: str,
        playlist_url: str,
        user_index: int,
        headless=False,
    ):
        super().__init__(
            username=username, password=password, headless=headless, random_lang=False
        )
        self.url = settings.spotify_login_address
        self.playlist_url = playlist_url
        self.user_index = user_index

    def run(self):
        try:
            self.driver.get(self.url)

            # Login
            username_input = self.driver.find_element(By.ID, "login-username")
            username_input.send_keys(self.username)

            password_input = self.driver.find_element(By.ID, "login-password")
            password_input.send_keys(self.password)

            self.driver.find_element(By.ID, "login-button").click()  # Click the button

            time.sleep(15)

            self.captcha_solver()

            self.accept_cookies()

            time.sleep(self.delay)

            self.driver.get(self.playlist_url)

            time.sleep(self.delay2)

            keyboard.send("esc")

            time.sleep(5)
            self.play(self.user_index)
            time.sleep(5)

            self.monitor_last_song()

        except NoSuchElementException as e:
            raise e

        except Exception as e:
            raise e

    def monitor_last_song(self):
        """Continuously monitor the last song's progress and play state."""
        try:
            while True:
                playlist_songs = self.driver.find_element(
                    "xpath",
                    "//div[@role='row' and (@aria-selected='true' or @aria-selected='false')]",
                ).find_element("xpath", "..")

                try:
                    last_song = playlist_songs.find_element(
                        By.XPATH, './div[@role="row"][last()]'
                    )
                except:  # The Spotify playlist is too large to find the last song.
                    time.sleep(5)
                    continue

                try:
                    # Check if the last song is playing
                    last_song.find_element(By.XPATH, './/button[@aria-label="Pause"]')

                    # Check the progress bar
                    try:
                        progress_bar = self.driver.find_element(
                            By.XPATH, '//*[@data-testid="progress-bar"]'
                        )
                        progress_transform = progress_bar.get_attribute("style")

                        # Extract the percentage value from the style attribute
                        percentage = float(
                            progress_transform.split("--progress-bar-transform: ")[
                                1
                            ].split("%")[0]
                        )

                        if percentage > 90:
                            print(
                                f"🎧 Le {self.user_index}° utilisateur a terminé d'écouter la playlist. 🎶 Merci pour l'écoute !"
                            )

                            self.driver.quit()

                    except NoSuchElementException:
                        pass

                except NoSuchElementException:
                    pass

                time.sleep(1)

        except KeyboardInterrupt:
            self.driver.quit()
