import time

from faker import Faker
from pystyle import Colors
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import settings
from shared.base import Base
from shared.files import update_user_in_json

faker = Faker()


class SpotifyPlaylist(Base):
    def __init__(self, username: str, password: str, playlist_url: str, headless=False):
        super().__init__(
            username=username, password=password, headless=headless, random_lang=False
        )
        self.url = settings.spotify_login_address
        self.playlist_url = playlist_url

    def run(self):
        try:
            self.driver.get(self.url)

            # Locate username and password inputs
            username_input = self.driver.find_element(By.ID, "login-username")
            password_input = self.driver.find_element(By.ID, "login-password")

            # Enter credentials
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)

            # Click the login button
            self.driver.find_element(By.ID, "login-button").click()

            time.sleep(15)

            # Reject cookies if the button exists
            try:
                reject_button = self.driver.find_element(
                    By.ID, "onetrust-reject-all-handler"
                )
                reject_button.click()
            except NoSuchElementException:
                print("Reject cookies button not found. Continuing.")

            time.sleep(self.delay2)

            # Navigate to the playlist or track URL
            self.driver.get(self.playlist_url)
            time.sleep(10)

            # Click the play button
            play_button = self.driver.find_element(
                By.XPATH,
                "/html/body/div[4]/div/div[2]/div[4]/div/div[2]/div[2]/div/main/section/div[2]/div[2]/div[2]/div/div/div[1]/button/span",
            )
            play_button.click()
            time.sleep(10)

        except Exception as e:
            print(f"An error occurred in the bot system: {str(e)}")

        time.sleep(5)

        self.monitor_last_song()

    def monitor_last_song(self):
        """Continuously monitor the last song's progress and play state."""
        try:
            while True:
                playlist_songs = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="main"]/div/div[2]/div[4]/div/div[2]/div[2]/div/main/section/div[2]/div[3]/div/div[1]/div[2]/div[2]',
                )
                last_song = playlist_songs.find_element(
                    By.XPATH, './div[@role="row"][last()]'
                )

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
                                Colors.blue,
                                f"L'utilisateur {self.username} a fini d'écouter la playlist...",
                            )

                            update_user_in_json(self.username, self.playlist_url)

                    except NoSuchElementException as e:
                        print(e)

                except NoSuchElementException as e:
                    pass

                time.sleep(2)

        except KeyboardInterrupt:
            self.driver.quit()
