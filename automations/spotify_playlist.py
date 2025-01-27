import time

from faker import Faker
from pystyle import Colors
from selenium.webdriver.common.by import By

import settings
from shared.base import Base

faker = Faker()


class SpotifyPlaylist(Base):
    def __init__(self, username: str, password: str, headless=False):
        super().__init__(username=username, password=password, headless=headless)
        self.url = settings.spotify_login_address

    def run(self):
        try:
            self.driver.get(self.url)

            username_input = self.driver.find_element(
                By.CSS_SELECTOR, "input#login-username"
            )
            password_input = self.driver.find_element(
                By.CSS_SELECTOR, "input#login-password"
            )

            username_input.send_keys(self.username)
            password_input.send_keys(self.password)

            self.driver.find_element(
                By.CSS_SELECTOR, "button[data-testid='login-button']"
            ).click()

            time.sleep(15)

            reject_button = self.driver.find_element(
                By.ID, "onetrust-reject-all-handler"
            )
            reject_button.click()

            time.sleep(self.delay2)

            self.driver.get(settings.spotify_track_url)

            time.sleep(10)

            play_button = self.driver.find_element(
                By.XPATH,
                "//*[@id='main']/div/div[2]/div[4]/div/div[2]/div[2]/div/main/section/div[3]/div[2]/div/div/div/button/span",
            )

            play_button.click()
            time.sleep(10)

            print(f"Username: {self.username} - Listening process has started.")

        except Exception as e:
            print(f"An error occurred in the bot system: {str(e)}")

        self.set_random_timezone()
        self.set_fake_geolocation()

        time.sleep(5)

        print(
            Colors.blue,
            "Stream operations are completed. You can stop all transactions by closing the program.",
        )

        while True:
            pass
