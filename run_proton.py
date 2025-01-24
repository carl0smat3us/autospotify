from automations.protonmail import Protonmail
import asyncio


async def main():
    tempmail = Protonmail(headless=False)
    await tempmail.create_account()


if __name__ == "__main__":
    asyncio.run(main())
