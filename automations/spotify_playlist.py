import time

from faker import Faker

import settings
from common.base_playwright import BasePlaywrightAsync
from common.user import User

fake = Faker()


class SpotifyPlalist(BasePlaywrightAsync):
    def __init__(self, email: str, password: str, playlist_url: str, headless=False):
        self.headless = headless
        self.user = User()

        self.url = settings.spotify_login_address

        self.email = email
        self.password = password

        self.playlist_url = playlist_url

        self.faker = Faker()
        self.page = None

    async def accept_cookies(self):
        try:
            await self.page.locator("#onetrust-accept-btn-handler").click()
        except Exception as e:
            print(f"Error accepting cookies: {e}")

    async def fill_login_page(self):
        await self.page.get_by_test_id("login-username").fill(self.email)
        await self.page.wait_for_timeout(1000)
        await self.page.get_by_test_id("login-password").fill(self.password)
        await self.page.wait_for_timeout(1000)
        await self.page.get_by_test_id("login-button").click()

    async def run(self):
        await self.start_session()
        await self.page.goto(self.url)
        await self.fill_login_page()

        await self.page.wait_for_timeout(30)

        await self.accept_cookies()
        await self.page.goto(self.playlist_url)
        await self.page.wait_for_timeout(1500000)
        await self.close_session()
