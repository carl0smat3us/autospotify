import random
import socket

import pytz
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

from shared.proxies import get_a_working_proxy

# proxy = get_a_working_proxy()

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

supported_timezones = pytz.all_timezones


class Base:
    def __init__(self, username: str, password: str, headless=False, random_lang=True):
        self.delay = random.uniform(2, 6)
        self.delay2 = random.uniform(5, 14)

        self.faker = Faker()

        self.username = username
        self.password = password

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--lang=en-US,en;q=0.9")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        # chrome_options.add_argument(f"--proxy-server={proxy}")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        if random_lang:
            chrome_options.add_argument(f"--lang={random.choice(supported_languages)}")

        if headless:
            chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

        self.set_random_timezone()
        self.set_fake_geolocation()

        # print(f"L'address ip est: {get_user_ip(proxy)}")

    def set_random_timezone(self):
        self.driver.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": random.choice(supported_timezones)},
        )

    def set_fake_geolocation(self):
        params = {
            "latitude": random.uniform(-90, 90),
            "longitude": random.uniform(-180, 180),
            "accuracy": 100,
        }
        self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)
