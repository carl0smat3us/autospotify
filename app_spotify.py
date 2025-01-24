import asyncio

from automations.spotify import Spotify


async def main():
    spotify = Spotify(headless=False)
    await spotify.run()


if __name__ == "__main__":
    asyncio.run(main())
