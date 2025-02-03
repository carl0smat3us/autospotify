import random
import time

import pytz
from fake_useragent import UserAgent
from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import settings
from exceptions import RetryAgainError

ua = UserAgent(os=["Windows", "Linux", "Ubuntu"])


class Base:
    def __init__(self, username: str, password: str, headless=False, random_lang=True):
        self.delay_page_loading = 10
        self.delay_after_page_loading = self.delay_before_submit = 5
        
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
            print(f"🎧 Le {user_index}° bot est en train d'écouter la playlist. 🎶")

    def listen_to_random_artist(self):
        search_bar = self.driver.find_element(
            By.XPATH,
            "//*[@data-testid='search-input']",
        )

        search_bar.send_keys(random.choice(settings.spotify_favorits_artists))

        time.sleep(self.delay_page_loading)

        first_artist = self.driver.find_element(
            By.XPATH, "//span[@role='presentation']/following-sibling::*[1]"
        )

        self.submit(first_artist, 10)
        self.play()

    def choose_an_artist(self):
        try:  # Check if Spotify displays a pop-up asking to choose favorite artists
            self.driver.find_element(
                By.XPATH,
                '//*[@data-testid="popover"]//div[contains(@class, "encore-announcement-set")]',
            )
        except NoSuchElementException:
            print("No pop-up detected!")
            return

        self.listen_to_random_artist()

    def accept_cookies(self):
        try:
            cookies_button = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            )
            cookies_button.click()
        except Exception:
            # Popup de cookie non trouvé, passage à l'étape suivante...
            pass

    @property
    def click_next(self):
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='submit']"
        )

        return submit_button

    def submit(self, element: WebElement, delay=5):
        time.sleep(self.delay_before_submit)
        element.click()
        self.verify_page(delay)

    def verify_page(self, delay=0):
        time.sleep(
            delay if delay != 0 else self.delay_page_loading
        )  # Wait till the page full load

        page_text = self.driver.find_element(By.TAG_NAME, "body").text

        if "upstream request timeout" in page_text.lower():
            raise RetryAgainError(
                "The page indicates an upstream request timeout. Arrêt du processus..."
            )
        elif "challenge.spotify.com" in self.driver.current_url:
            print(
                "CAPTCHA détecté! Aucun solveur CAPTCHA implémenté. Arrêt du processus..."
            )
            raise RetryAgainError("Captcha non implémenté !")

        self.accept_cookies()
        time.sleep(self.delay_after_page_loading)

    def get_page(self, url: str):
        self.driver.get(url)
        self.verify_page()
        time.sleep(self.delay_after_page_loading)
