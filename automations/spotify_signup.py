import random
import time

from faker import Faker

import settings
from common.base_playwright import BasePlaywrightAsync
from common.user import User

fake = Faker()


class SpotifySignup(BasePlaywrightAsync):
    def __init__(self, email: str, password: str, headless=False):
        self.headless = headless
        self.user = User()

        self.url = settings.spotify_registration_address

        self.email = email
        self.password = password

        self.faker = Faker()
        self.page = None

    async def accept_cookies(self):
        try:
            await self.page.locator("#onetrust-accept-btn-handler").click()
        except Exception as e:
            print(f"Error accepting cookies: {e}")

    async def fill_email(self):
        await self.page.get_by_placeholder("name@domain.com").fill(self.email)
        await self.page.wait_for_timeout(1000)
        await self.page.get_by_test_id("submit").click()

    async def fill_password(self):
        await self.page.locator("input[name='new-password']").fill(self.password)
        await self.page.wait_for_timeout(1000)
        await self.page.get_by_test_id("submit").click()

    async def fill_personal_details(self):
        # Fill Name
        await self.page.locator("input[name='displayName']").fill(self.faker.name())

        # Fill Birthdate
        await self.page.locator("input[name='day']").fill(str(random.randint(1, 31)))
        await self.page.locator("select[name='month']").select_option(label="April")
        await self.page.locator("input[name='year']").fill(
            str(random.randint(1970, 2000))
        )

        # Select Gender
        await self.page.locator("label[for='gender_option_male']").click()

        await self.page.wait_for_timeout(1000)

        # Click next
        await self.page.get_by_test_id("submit").click()

    async def create_account(self):
        await self.accept_cookies()

        # Step 1: Fill email
        await self.fill_email()
        await self.page.wait_for_timeout(5000)

        # # Step 2: Fill password
        await self.fill_password()
        await self.page.wait_for_timeout(5000)

        # Step 3: Fill personal details
        await self.fill_personal_details()
        await self.page.wait_for_timeout(5000)

        # Final step: Create account button click
        await self.page.get_by_test_id("submit").click()

        # Sleep for a while to simulate user behavior (this is a placeholder)
        time.sleep(10)

        print("--------------------------")
        print("Spotify account created!!!")
        print("--------------------------")

    async def run(self):
        await self.start_session()
        await self.page.goto(self.url)
        await self.create_account()
        await self.close_session()
