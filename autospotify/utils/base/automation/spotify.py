from time import sleep

from selenium.webdriver.common.by import By

from autospotify.utils.base import Base
from autospotify.utils.logs import log
from autospotify.utils.schemas import FindElement, User


class SpotifyBase(Base):
    def __init__(
        self,
        user: User,
        base_url: str,
        extensions=[],
    ):
        super().__init__(
            user=user,
            base_url=base_url,
            extensions=extensions,
        )

    def play(self, user_index=None):
        self.click(
            query=FindElement(
                by=By.CSS_SELECTOR, value="button[data-testid='play-button']"
            ),
            use_javascript=True,
        )  # Click on the button play

        if user_index is not None:
            log(f"🎧 Le {user_index}° bot est en train d'écouter la playlist. 🎶")

        sleep(10)  # Waiting till the playlist changes

    @property
    def button_next(self):
        find_element = FindElement(by=By.CSS_SELECTOR, value="[data-testid='submit']")

        return find_element
