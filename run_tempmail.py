from automations.tempmail import Tempmail
import asyncio


async def main():
    tempmail = Tempmail(headless=False)
    await tempmail.run()


if __name__ == "__main__":
    asyncio.run(main())
