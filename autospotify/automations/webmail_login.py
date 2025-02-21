import re
from logging import ERROR
from time import sleep
from urllib.parse import parse_qs, unquote, urlparse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import autospotify.settings as settings
from autospotify.exceptions import RetryAgain
from autospotify.utils.base import Base
from autospotify.utils.logs import log
from autospotify.utils.schemas import FindElement, User


class MailLogin(Base):
    def __init__(self, user: User):
        super().__init__(
            user=user,
            base_url=settings.webmail_login_url,
            extensions=[
                "https://chromewebstore.google.com/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm"
            ],
        )

    def login_step(self):
        self.log_step("taper les informations de login")

        try:
            self.click(
                query=FindElement(by=By.CSS_SELECTOR, value=".icon-close.js-close"),
                use_javascript=True,
                wait_until_search=True,
            )  # Close blog PopUp
        except:
            ...

        try:
            self.click(
                query=FindElement(by=By.ID, value="login-button"),
                use_javascript=True,
                wait_until_search=True,
            )  # Expand login PopUp
        except NoSuchElementException:
            raise RetryAgain("La page semble ne pas avoir été bien chargée.")

        username_input = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.ID, "login-email"))
        )
        self.fill_input(username_input, self.user.username)

        password_input = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.ID, "login-password"))
        )
        self.fill_input(password_input, self.user.password)

        self.submit_form(
            query=FindElement(
                by=By.XPATH,
                value="//button[contains(@class, 'login-submit') and @type='submit']",
            )
        )

    def activate_account_step(self):
        mail_list = self.get_mail_list_step()
        mail_found = False

        for mail in mail_list:
            if "Spotify" in mail.sender:
                mail_found = True

                sleep(self.delay_start_interactions)
                mail.click()
                sleep(self.delay_start_interactions)
                break

        self.driver.switch_to.default_content()

        if mail_found:
            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.ID, "thirdPartyFrame_mail")
                )
            )

            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "mail-detail"))
            )

            confirmation_link = self.driver.find_element(
                By.XPATH, "//a[contains(@href, 'deref-mail.com')]"
            ).get_attribute("href")
            redirect_url = unquote(
                parse_qs(urlparse(confirmation_link).query).get("redirectUrl", [""])[0]
            )

            self.get_page(redirect_url)
        else:
            log("⚠️ L'email Spotify n'a pas été trouvé ❌", ERROR)

    def action(self):
        self.login_step()
        self.activate_account_step()
