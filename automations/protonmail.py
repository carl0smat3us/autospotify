import websockets
from common.user import User
from exceptions.possible_exceptions import *
from common.base_playwright import BasePlaywrightAsync
import settings
import datetime
import json


class Protonmail(BasePlaywrightAsync):
    def __init__(self, headless=False):
        super().__init__(headless=headless)
        self.url = settings.protonmail_registration_address
        self.protonmail_domain = settings.protonmail_domain
        self.tmp_mail = None
        self.user = User()

    async def set_user_data(self):
        print("Filling out the fields on the registration page")
        (
            await self.page.frame_locator('iframe[title="Email address"]')
            .get_by_test_id("input-input-element")
            .fill(self.user.nickname)
        )
        await self.page.get_by_label("Password", exact=True).fill(self.user.password)
        await self.page.get_by_label("Repeat password").fill(self.user.password)

    async def create_account_button_click(self):
        print("Creating account button pressed")
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
        print("Trying to register using temporary email")
        alert = await self.try_register_using_temp_mail()
        if "Please wait a few minutes" in alert:
            await self.page.get_by_role("button", name="Get verification code").click()
        else:
            while (
                "Email address verification temporarily disabled for this email domain. "
                "Please try another verification method"
            ) in alert:

                self.tmp_mail = await self.switch_temporary_email()
                alert = await self.try_register_using_temp_mail()

    async def switch_temporary_email(self):
        async with websockets.connect(settings.websocket_uri) as websocket:
            await websocket.send(json.dumps({"action":"createEmail"}))
            message = await websocket.recv()

            message_dict = json.loads(message)

            try:
                if message_dict["status"] == "success":
                    self.tmp_mail = message_dict["email"]
                    return
                await self.switch_temporary_email()
            except Exception as e:
                print(e)
                await self.switch_temporary_email()

    async def run_registration(self):
        await self.start_session()
        await self.page.goto(self.url)
        await self.set_user_data()
        await self.create_account_button_click()

        # Get temporary email and register
        await self.switch_temporary_email()
        await self.register_with_temporary_email()

        await self.insert_verification_code()
        await self.finishing_registration()
        await self.close_session()

    async def insert_verification_code(self):
        async with websockets.connect(settings.websocket_uri) as websocket:
            # Request the verification code
            await websocket.send(json.dumps({"action":"fetchVerificationCode"}))

            message = await websocket.recv()

            try:
                if message["status"] == "success":
                    self.page.get_by_test_id("input-input-element").fill(
                        message["verificationCode"]
                    )
                    self.page.get_by_role("button", name="Verify").click()
                await self.insert_verification_code()
            except Exception:
                await self.insert_verification_code()

    async def finishing_registration(self):
        print("Finishing registration...")
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
