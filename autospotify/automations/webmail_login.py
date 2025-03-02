from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import autospotify.settings as settings
from autospotify.exceptions import RetryAgain
from autospotify.utils.base.automation.webmail import WebmailBase
from autospotify.utils.schemas import FindElement, User


class MailLogin(WebmailBase):
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

    def get_mails_step(self):
        mail_list = self.get_mail_list_step()
        self.log_mail_list(mail_list)

    def action(self):
        self.login_step()
        self.activate_account_step()
        self.get_mails_step()
