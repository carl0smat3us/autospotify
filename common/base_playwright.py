from playwright.async_api import async_playwright


class BasePlaywrightAsync:
    def __init__(self, headless=False):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.headless = headless

    async def start_session(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def go_to(self, url: str):
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")

    async def close_session(self):
        await self.page.close()
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
