import random
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import autospotify.settings as settings
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
        use_user_profile=False,
        browser_type="chrome",
    ):
        super().__init__(
            user=user,
            base_url=base_url,
            extensions=extensions,
            captcha_solver_enabled=captcha_solver_enabled,
            use_user_profile=use_user_profile,
            browser_type=browser_type,
        )

    def listen_to_random_artist(self, force=False):
        self.log_step("sélection d'un artiste préféré 🎨✨")

        if not force:
            # Chose an random artist by searching it
            random_artist = random.choice(settings.spotify_favorits_artists)

            search_bar = WebDriverWait(self.driver, 180).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[@data-testid='search-input']")
                )
            )
            self.fill_input(search_bar, random_artist)

            if search_bar.get_attribute("value").strip() != random_artist.strip():
                raise ValueError(
                    f"❌ Erreur : la saisie ne correspond pas à {random_artist} ! 🔄🎵"
                )

            sleep(self.delay_page_loading)

            self.submit_form(
                element=FindElement(
                    by=By.XPATH,
                    value="//div[@data-testid='infinite-scroll-list']//span[@role='presentation']",
                ),
                use_javascript=False,
            )  # open artist page

            self.check_page_url(keyword="artist")
        else:
            # Listen to a random artist/album/whatever of home page

            self.submit_form(
                element=FindElement(
                    by=By.XPATH,
                    value='//*[@aria-labelledby][contains(@aria-labelledby, "card-title-spotify")]',
                ),
                use_javascript=False,
            )

        self.play()

    def choose_an_artist(self, force=False):
        """
        Check if Spotify displays a pop-up asking to choose favorite artists
        if Spotify is asking listen to them

        force: Choose a random artist even though spotify isnt asking it
        """
        self.log_step("choisir un artist aléatoire")

        try:
            self.driver.find_element(
                By.XPATH,
                '//*[@data-testid="popover"]//div[contains(@class, "encore-announcement-set")]',
            )

            log("L'application a demandé au bot de choisir son chanteur préféré 🤖🎤")
        except NoSuchElementException:
            return

        self.listen_to_random_artist()

    def play(self, user_index=None):
        self.log_step("jouer une chanson")

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

        if (
            "upstream request timeout" in page_text.lower()
            or "upstream connect" in page_text.lower()
        ):
            raise RetryAgain(
                "La page indique un délai d'attente de la requête en amont. Arrêt du processus..."
            )

        if "challenge.spotify.com" in self.driver.current_url:
            if self.captcha_solver_enabled:
                self.activate_captcha_solver()
                self.submit_form(query=FindElement(by=By.TAG_NAME, value="button"))
            else:
                raise RetryAgain("Le résolveur de captcha n'a pas été activé")

    def logout(self):
        self.log_step("se déconnecter")
        self.click(
            query=FindElement(
                by=By.XPATH, value='//*[@data-testid="user-widget-link"]'
            ),
            use_javascript=True,
        )

        self.submit_form(
            query=FindElement(
                by=By.XPATH, value='//*[@data-testid="user-widget-dropdown-logout"]'
            ),
            use_javascript=True,
        )
