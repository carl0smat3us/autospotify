from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import settings
from exceptions import RetryAgain
from utils.base import Base
from utils.logs import log
from utils.schemas import FindElement, User


class MailLogin(Base):
    def __init__(self, user: User):
        super().__init__(user=user, base_url=settings.webmail_login_url)

        self.activated = False

    def login_step(self):
        self.log_step("taper les informations de login")

        try:
            self.click(
                query=FindElement(by=By.ID, value="login-button")
            )  # Expand login PopUp
        except NoSuchElementException:
            raise RetryAgain("La page semble ne pas avoir été bien chargée.")

        username_input = self.driver.find_element(By.ID, "login-email")
        self.fill_input(username_input, self.user.username)

        password_input = self.driver.find_element(By.ID, "login-password")
        self.fill_input(password_input, self.user.password)

        self.submit_form(
            query=FindElement(
                by=By.XPATH,
                value="//button[contains(@class, 'login-submit') and @type='submit']",
            )
        )

    def get_mail_list_step(self):
        self.check_page_url(
            keyword="navigator-lxa.mail.com", step_name="obeternir la liste d'emails"
        )

        WebDriverWait(self.driver, 180).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "thirdPartyFrame_mail"))
        )

        mail_box = self.driver.find_elements(By.ID, "mail-list")

        messages = []

        # Scroll through the mail list
        for mail in mail_box:
            subject_element = mail.find_element(By.CLASS_NAME, "subject")
            sender_element = mail.find_element(By.CLASS_NAME, "name")
            data_element = mail.find_element(By.CLASS_NAME, "date")

            messages.append(
                {
                    "sender": sender_element.text,
                    "subject": subject_element.text,
                    "date": data_element.text,
                }
            )

            if "Confirmer" in subject_element.text:  # Search for the activation mail
                self.click(mail)
                self.activate_account_step()
                break

    def activate_account_step(self):
        self.activated = True

    def action(self):
        self.login_step()
        self.get_mail_list_step()

        if not self.activated:
            log("⚠️ Le compte n'a pas été activé !")
