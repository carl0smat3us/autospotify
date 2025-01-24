import websockets
from common.base_playwright import BasePlaywrightAsync
from settings import websocket_uri
import json
import time


class Tempmail(BasePlaywrightAsync):
    def __init__(self, headless=False):
        super().__init__(headless=headless)
        self.url = "https://tempmail.so/"
        self.email = None

    async def run(self):
        await self.copy_email_address()
        await self.get_verification_code()

    def get_code(self):
        # Get the verification code of html file
        return 4853

    async def get_verification_code(self):
        async with websockets.connect(websocket_uri) as websocket:
            response = await websocket.recv()

            response_dict = json.loads(response)

            if response_dict["action"] == "get-verification-code":
                await self.page.locator(
                    'xpath=//*[@id="home-guide-modal"]/div/div[5]'
                ).click()  # Close the ads popup

                await self.page.locator(
                    "xpath=/html/body/section[2]/temp-mail-inbox/div[2]/div/div[2]/div"
                ).click() # Open the message

                # Save the page
                
                print("Code: ",code)

                message = {
                    "action": "send-verification-code",
                    "value": code,
                }

                await websocket.send(json.dumps(message))
            else:
                await self.get_verification_code(websocket)

    async def send_email_address(self):
        async with websockets.connect(websocket_uri) as websocket:
            message = {"action": "send-tmp-mail", "value": self.email}
            print(f"Email: {self.email}")

            await websocket.send(json.dumps(message))

    async def copy_email_address(self):
        await self.start_session()
        await self.go_to(self.url)

        self.email = await self.page.locator(
            "xpath=/html/body/section[2]/temp-mail-inbox/div[1]/div[2]/span"
        ).text_content()

        if self.email:
            await self.send_email_address()
