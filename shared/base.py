import random
import time

import pytz
from fake_useragent import UserAgent
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import settings
from exceptions import RetryAgainError

ua = UserAgent(os=["Windows", "Linux", "Ubuntu"])


class Base:
    def __init__(self, username: str, password: str, headless=False, random_lang=True):
        self.delay = random.uniform(2, 6)
        self.delay2 = random.uniform(5, 14)

        self.faker = Faker()

        self.retries = 0
        self.max_retries = 5

        self.username = username
        self.password = password

        browser_options = webdriver.ChromeOptions()
        browser_options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

        browser_options.add_argument("--disable-logging")
        browser_options.add_argument("--log-level=3")
        browser_options.add_argument("--disable-infobars")
        browser_options.add_argument("--disable-extensions")
        browser_options.add_argument("--window-size=1366,768")
        browser_options.add_argument("--start-maximized")
        browser_options.add_argument("--lang=en-US,en;q=0.9")
        browser_options.add_argument("--disable-notifications")
        browser_options.add_argument(f"--user-agent={ua.random}")
        browser_options.add_argument("--disable-dev-shm-usage")
        browser_options.add_argument("--incognito")
        browser_options.add_argument("--disable-cookies")
        browser_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        if random_lang:
            browser_options.add_argument(
                f"--lang={random.choice(settings.spotify_supported_languages)}"
            )

        if headless:
            browser_options.add_argument("--headless")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=browser_options
        )

        self.set_random_timezone()
        self.set_fake_geolocation()

    def set_random_timezone(self):
        self.driver.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": random.choice(pytz.all_timezones)},
        )

    def set_fake_geolocation(self):
        params = {
            "latitude": random.uniform(-90, 90),
            "longitude": random.uniform(-180, 180),
            "accuracy": 100,
        }
        self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

    def play(self, user_index=None):
        play_button = self.driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='play-button']"
        )

        # Click works via JavaScript only for new accounts.
        self.driver.execute_script("arguments[0].click();", play_button)

        if user_index is not None:
            print(
                f"🎧 Le {user_index}° utilisateur est en train d'écouter la playlist. 🎶"
            )

    def captcha_solver(self):
        if "challenge.spotify.com" in self.driver.current_url:
            print("CAPTCHA détecté !")
            print("Aucun solveur CAPTCHA implémenté. Arrêt du processus...")

            raise RetryAgainError("Captcha non implémenté !")

    def click_next(self):
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='submit']"
        )
        submit_button.click()

    def choose_an_artist(self):
        try:  # Check if Spotify displays a pop-up asking to choose favorite artists
            self.driver.find_element(
                By.XPATH,
                '//*[@data-testid="popover"]/div[@class="encore-announcement-set" and @role="tooltip"]',
            )

            search_bar = self.driver.find_element(
                By.XPATH,
                "//*[@id='global-nav-bar']/div[2]/div/div/span/div/form/div[2]/input",
            )

            search_bar.send_keys(random.choice(settings.spotify_favorits_artists))

            time.sleep(15)

            artists_table = self.driver.find_element(
                By.XPATH,
                "//span[@role='presentation' and @aria-expanded='true' and @data-open='true']",
            ).find_element(By.XPATH, "..")

            time.sleep(5)

            first_artist = artists_table.find_element(
                By.XPATH, './div[@span="presentation"][1]'
            )

            first_artist.click()

            time.sleep(15)

            self.play()

            time.sleep(50)
        except:
            # No pop-up detected: Proceeding with the process...
            pass

    def accept_cookies(self):
        try:
            cookies_button = self.driver.find_element(
                By.ID, "onetrust-accept-btn-handler"
            )
            cookies_button.click()
        except Exception:
            # Popup de cookie non trouvé, passage à l'étape suivante...
            pass
