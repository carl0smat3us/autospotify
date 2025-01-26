import random
import time

# import keyboard
import pytz
from fake_useragent import UserAgent
from pystyle import Colors
from selenium import webdriver

# from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from settings import spotify_login_address, spotify_track_url

# Supported time zones and user agents
supported_timezones = pytz.all_timezones
ua = UserAgent(platforms="desktop")


class SpotifyPlaylist:
    def __init__(self, username: str, password: str, headless=False):
        supported_languages = [
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

        user_agents = [
            # Chrome (Windows)
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            # Additional user agents omitted for brevity
        ]

        self.delay = random.uniform(2, 6)
        self.delay2 = random.uniform(5, 14)

        self.username = username
        self.password = password

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--lang=en-US,en;q=0.9")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        chrome_options.add_argument(f"--lang={random.choice(supported_languages)}")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

    def set_random_timezone(self, driver):
        driver.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": random.choice(supported_timezones)},
        )

    def set_fake_geolocation(self, driver, latitude, longitude):
        params = {"latitude": latitude, "longitude": longitude, "accuracy": 100}
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

    def run(self):
        try:
            self.driver.get(spotify_login_address)

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

            self.driver.get(spotify_track_url)

            # keyboard.press_and_release("esc")
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

        self.set_random_timezone(self.driver)

        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)

        self.set_fake_geolocation(self.driver, latitude, longitude)

        time.sleep(5)

        print(
            Colors.blue,
            "Stream operations are completed. You can stop all transactions by closing the program.",
        )

        while True:
            pass
