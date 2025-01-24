import random
import time

from faker import Faker
from playwright.async_api import async_playwright

import settings
from common.user import User

fake = Faker()


class SpotifySignup:
    def __init__(self, headless=False):
        self.headless = headless
        self.user = User()

        self.email_addresses = ["bbuzppszi9@qacmjeq.com"]  # Just for tests
        self.password_input = "UserPassword2025"

        self.faker = Faker()
        self.page = None

    async def start_session(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            self.page = await context.new_page()
            await self.page.goto(settings.spotify_registration_address)

    async def accept_cookies(self):
        try:
            await self.page.locator("#onetrust-accept-btn-handler").click()
        except Exception as e:
            print(f"Error accepting cookies: {e}")

    async def fill_email(self):
        email = random.choice(self.email_addresses)
        await self.page.locator("input[name='username']").fill(email)
        await self.page.locator("button[data-testid='submit']").click()

    async def fill_password(self):
        await self.page.locator("input[name='new-password']").fill(self.password_input)
        await self.page.locator("button[data-testid='submit']").click()

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

        # Click next
        await self.page.locator("button[data-testid='submit']").click()

    async def create_account(self):
        await self.start_session()
        await self.accept_cookies()

        # Step 1: Fill email
        await self.fill_email()
        await self.page.wait_for_timeout(5000)

        # Step 2: Fill password
        await self.fill_password()
        await self.page.wait_for_timeout(5000)

        # Step 3: Fill personal details
        await self.fill_personal_details()
        await self.page.wait_for_timeout(5000)

        # Final step: Create account button click
        await self.page.locator("button[data-testid='submit']").click()

        # Sleep for a while to simulate user behavior (this is a placeholder)
        time.sleep(30)

    async def close_session(self):
        if self.page:
            await self.page.context.close()

    async def run(self):
        await self.spotify_signup.create_account()
        await self.spotify_signup.close_session()
