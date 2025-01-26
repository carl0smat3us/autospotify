import random

import pytz
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

from common.proxies import get_proxies

ua = UserAgent(platforms="desktop")

proxy = get_proxies()

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

supported_timezones = pytz.all_timezones


class BasePlaywrightAsync:
    def __init__(self, headless=False):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.headless = headless

    async def start_session(self):
        self.playwright = await async_playwright().start()

        """
        "proxy": {
            "server": random.choice(proxy),
        },
        """

        self.browser = await self.playwright.chromium.launch(
            **{
                "headless": self.headless,
            },
            args=["--disable-blink-features=AutomationControlled", "--disable-logging"]
        )
        self.context = await self.browser.new_context(
            geolocation=self.generate_fake_location(),
            permissions=["geolocation"],
            user_agent=ua["Chrome"],
            locale=random.choice(supported_languages),
            timezone_id=random.choice(supported_timezones),
        )
        self.page = await self.context.new_page()

    def generate_fake_location(self):
        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)
        return {"latitude": latitude, "longitude": longitude}

    async def go_to(self, url: str):
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")

    async def close_session(self):
        await self.page.close()
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
