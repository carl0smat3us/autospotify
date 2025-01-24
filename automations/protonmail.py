import datetime
import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from faker import Faker

import settings
from common.base_playwright import BasePlaywrightAsync
from common.user import User
from exceptions import *

load_dotenv()

TEMPMAIL_API_KEY = os.getenv("TEMPMAIL_API_KEY")
TEMPMAIL_AUTHORIZATION = os.getenv("TEMPMAIL_AUTHORIZATION")

fake = Faker()


class Protonmail(BasePlaywrightAsync):
    def __init__(self, headless=False):
        super().__init__(headless=headless)
        self.url = settings.protonmail_registration_address
        self.protonmail_domain = settings.protonmail_domain
        self.tmp_mail = None
        self.temp_mail_id = None
        self.user = User()

    async def set_user_data(self):
        await self.page.frame_locator('iframe[title="Email address"]').get_by_test_id(
            "input-input-element"
        ).fill(self.user.nickname)
        await self.page.get_by_label("Password", exact=True).fill(self.user.password)
        await self.page.get_by_label("Repeat password").fill(self.user.password)

    async def create_account_button_click(self):
        await self.page.get_by_role("button", name="Create account").click()

    async def try_register_using_temp_mail(self):
        try:
            await self.page.get_by_test_id("tab-header-email-button").click()
        except:
            pass

        try:
            await self.page.get_by_test_id("input-input-element").fill(self.tmp_mail)
        except Exception:
            raise NoEmailVerification(
                "Verification by email is not available now! Please try again later or use VPN."
            )

        await self.page.get_by_role("button", name="Get verification code").click()
        alert = await self.page.get_by_role("alert").inner_text()
        return alert

    async def register_with_temporary_email(self):
        alert = await self.try_register_using_temp_mail()
        if "Please wait a few minutes" in alert:
            await self.page.get_by_role("button", name="Get verification code").click()
        else:
            await self.switch_temporary_email()

    async def switch_temporary_email(self):
        email_domains = [
            "mailshan.com",
            "driftz.net",
        ]

        username = fake.user_name()
        domain = random.choice(email_domains)

        response = requests.post(
            "https://tempmail-so.p.rapidapi.com/inboxes",
            headers={
                "Authorization": TEMPMAIL_AUTHORIZATION,
                "Content-Type": "application/json",
                "x-rapidapi-host": "tempmail-so.p.rapidapi.com",
                "x-rapidapi-key": TEMPMAIL_API_KEY,
            },
            json={"name": username, "domain": domain, "lifespan": 0},
        )

        response.raise_for_status()
        inbox = response.json()

        self.temp_mail_id = inbox["data"]["id"]
        self.tmp_mail = f"{username}@{domain}"

    async def run_registration(self):
        await self.start_session()
        await self.page.goto(self.url)
        await self.set_user_data()
        await self.create_account_button_click()
        await self.switch_temporary_email()
        await self.register_with_temporary_email()
        await self.insert_verification_code()
        await self.finishing_registration()
        await self.close_session()

    async def insert_verification_code(self):
        time.sleep(120)  # Wait till the email arrive
        mail_box = requests.get(
            f"https://tempmail-so.p.rapidapi.com/inboxes/{self.temp_mail_id}/mails",
            headers={
                "Authorization": TEMPMAIL_AUTHORIZATION,
                "Content-Type": "application/json",
                "x-rapidapi-host": "tempmail-so.p.rapidapi.com",
                "x-rapidapi-key": TEMPMAIL_API_KEY,
            },
        )

        mail_box.raise_for_status()
        mail_box = mail_box.json()

        breakpoint()
        mail_id = mail_box["data"][0]["id"]

        mail = requests.get(
            f"https://tempmail-so.p.rapidapi.com/inboxes/{self.temp_mail_id}/mails/{mail_id}",
            headers={
                "Authorization": TEMPMAIL_AUTHORIZATION,
                "Content-Type": "application/json",
                "x-rapidapi-host": "tempmail-so.p.rapidapi.com",
                "x-rapidapi-key": TEMPMAIL_API_KEY,
            },
        )

        mail.raise_for_status()
        mail = mail.json()
        verification_code = self.extract_verification_code(mail["data"]["htmlContent"])

        self.page.get_by_test_id("input-input-element").fill(verification_code)
        self.page.get_by_role("button", name="Verify").click()

    def extract_verification_code(self, html):
        soup = BeautifulSoup(html, "html.parser")
        for span in soup.find_all("span"):
            text = span.get_text(strip=True)
            if re.match(r"^\d{6}$", text):
                return text
        return None

    async def finishing_registration(self):
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("button", name="Maybe later").click()
        self.page.get_by_role("button", name="Confirm").click()

    async def create_account(self):
        self.user.generate_new_user()
        await self.run_registration()
        protonmail_login, protonmail_password = (
            self.user.nickname + self.protonmail_domain,
            self.user.password,
        )
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(protonmail_login, protonmail_password, current_time)
        await self.close_session()
