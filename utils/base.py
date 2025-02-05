import datetime
import random
import time
from os import path

import pytz
from fake_useragent import UserAgent
from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

import settings
from exceptions import RetryAgainError, UnexpectedUrl
from utils.files import read_proxies_from_txt
from utils.logs import log_message, logger
from utils.proxies import create_proxy_extension, get_user_ip

ua = UserAgent(os=["Windows", "Linux", "Ubuntu"])


class Base:
    def __init__(self, username: str, password: str):
        self.delay_page_loading = 10
        self.delay_after_page_loading = self.delay_before_submit = 5

        self.faker = Faker()

        self.retries = 0
        self.max_retries = 5

        self.username = username
        self.password = password

        self.proxies = read_proxies_from_txt()
        self.proxy_url = None
        self.ip = get_user_ip()

        browser_options = webdriver.ChromeOptions()
        browser_options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

        browser_options.add_argument("--disable-logging")
        browser_options.add_argument("--log-level=3")
        browser_options.add_argument("--disable-infobars")
        browser_options.add_argument("--window-size=1366,768")
        browser_options.add_argument("--start-maximized")
        browser_options.add_argument("--disable-notifications")
        browser_options.add_argument(f"--user-agent={ua.random}")
        browser_options.add_argument("--disable-dev-shm-usage")
        browser_options.add_argument("--disable-cookies")
        browser_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        if len(self.proxies) == 0:
            log_message(
                "🚨 Aucun proxy détecté ! Le script utilisera votre propre IP sans camouflage. 🌐🔍"
            )

        if len(self.proxies) >= 1:
            self.proxy_url = self.proxies[random.randint(0, len(self.proxies) - 1)]
            proxy_extension = create_proxy_extension(self.proxy_url)

            browser_options.add_extension(proxy_extension)

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
            log_message(
                f"🎧 Le {user_index}° bot est en train d'écouter la playlist. 🎶"
            )

    def accept_cookies(self):
        try:
            time.sleep(self.delay_before_submit)
            cookies_button = self.driver.find_element(
                By.ID, "onetrust-accept-btn-handler"
            )
            cookies_button.click()
        except Exception:
            # Popup de cookie non trouvé, passage à l'étape suivante...
            pass

    def verify_page_url(self, step: str, keyword: int):
        if keyword not in self.driver.current_url:
            raise UnexpectedUrl(
                "❌ L'utilisateur n'est pas arrivé à la destination attendue !"
            )

        log_message(
            f"✅ L'utilisateur est à l'étape '{step}' 🎯"
        )

    @property
    def click_next(self):
        submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='submit']"
        )

        return submit_button

    def submit(self, element: WebElement, delay=5, use_javascript=True):
        time.sleep(self.delay_before_submit)

        if use_javascript:
            self.driver.execute_script("arguments[0].click();", element)
        else:
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
            raise RetryAgainError(
                "CAPTCHA détecté! Aucun solveur CAPTCHA implémenté. Arrêt du processus..."
            )

        self.accept_cookies()
        time.sleep(self.delay_after_page_loading)

    def get_page(self, url: str, show_ip=False):
        if show_ip:
            self.ip = get_user_ip(self.proxy_url)
            log_message(f"🤖 Le bot est en train d'utiliser l'IP : {self.ip} 🌍")

        self.driver.get(url)
        self.verify_page()
        time.sleep(self.delay_after_page_loading)

    def action(self):
        # Run the automation
        pass

    def run(self):
        def wrapper():
            self.get_page(self.url, True)
            self.action()

        run = self.run_preveting_errors(wrapper)
        run()

    def logg_error(self, message: str):
        timestamp = (
            datetime.datetime.now()
            .strftime(settings.logging_datefmt)
            .replace(" ", "_")
            .replace(":", "_")
        )
        screenshot_path = path.join(
            settings.logs_paths["screenshots"], f"{timestamp}.png"
        )
        self.driver.save_screenshot(screenshot_path)
        logger.error(message)

    def run_preveting_errors(self, run):
        def inner_function(*args, **kwargs):
            while True:
                try:
                    run(*args, **kwargs)
                    self.driver.quit()
                    break

                except RetryAgainError as e:
                    self.retries += 1
                    log_message(e)
                    if self.retries <= self.max_retries:
                        log_message(
                            f"🔄 ({self.retries}) Nouvelle tentative en cours... Veuillez patienter."
                        )
                        continue

                    log_message("Nombre maximal de tentatives atteint.")
                    self.driver.quit()
                    break

                except NoSuchWindowException:
                    log_message("🚫 La fenêtre a été fermée.")
                    self.driver.quit()
                    break

                except Exception as e:
                    self.logg_error(f"Error pendant l'execution de l'application: {e}")
                    self.driver.quit()
                    break

        return inner_function
