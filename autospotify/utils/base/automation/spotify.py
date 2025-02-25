from time import sleep

from selenium.webdriver.common.by import By

from autospotify.exceptions import RetryAgain
from autospotify.utils.base import Base
from autospotify.utils.logs import log
from autospotify.utils.schemas import FindElement, User


class SpotifyBase(Base):
    def __init__(
        self,
        user: User,
        base_url: str,
        extensions=[],
        captcha_solver_enabled=False,
    ):
        super().__init__(
            user=user,
            base_url=base_url,
            extensions=extensions,
            captcha_solver_enabled=captcha_solver_enabled,
        )

    def play(self, user_index=None):
        playlist_songs = self.driver.find_element(
            By.XPATH,
            "//div[@role='row' and (@aria-selected='true' or @aria-selected='false')]",
        ).find_element(By.XPATH, "..")

        first_song = playlist_songs.find_element(By.XPATH, './div[@role="row"][1]')

        self.actions.double_click(
            first_song
        ).perform()  # Listen to the first song of the playlist
        sleep(self.delay_page_loading)

        if user_index is not None:
            log(f"🎧 Le {user_index}° bot est en train d'écouter la playlist. 🎶")

        # if user is listening to a random artist this will keep the user on the page for a bit
        sleep(self.delay_page_loading)

    @property
    def button_next(self):
        find_element = FindElement(by=By.CSS_SELECTOR, value="[data-testid='submit']")

        return find_element

    def accept_cookies(self):
        self.click(
            query=FindElement(by=By.ID, value="onetrust-accept-btn-handler"),
            use_javascript=True,
        )

    def check_page_status(self):
        page_text = self.driver.find_element(By.TAG_NAME, "body").text

        if "upstream request timeout" in page_text.lower():
            raise RetryAgain(
                "La page indique un délai d'attente de la requête en amont. Arrêt du processus..."
            )

        if "challenge.spotify.com" in self.driver.current_url:
            if self.captcha_solver_enabled:
                self.activate_captcha_solver()
                self.submit_form(query=FindElement(by=By.TAG_NAME, value="button"))
            else:
                raise RetryAgain("Le résolveur de captcha n'a pas été activé")
