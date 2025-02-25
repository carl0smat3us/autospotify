from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate

from autospotify.exceptions import IpAddressError
from autospotify.utils.base import Base
from autospotify.utils.logs import log
from autospotify.utils.schemas import FindElement, MailBox, User


class WebmailBase(Base):
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

    def log_mail_list(self, messages: List[MailBox]):
        table_data = [
            {k: v for k, v in mail.model_dump().items() if k != "element"}
            for mail in messages
        ]
        log(f"\n{tabulate(table_data, headers="keys", tablefmt="grid")}")

    def get_mail_list_step(self) -> List[MailBox]:
        self.check_page_url(
            keyword="navigator-lxa.mail.com", step_name="obeternir la liste d'emails"
        )

        self.driver.switch_to.default_content()

        WebDriverWait(self.driver, 15).until(
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
                MailBox(
                    element=mail,
                    sender=sender_element.text,
                    subject=subject_element.text,
                    date=data_element.text,
                )
            )

        if len(messages) >= 1:
            self.log_mail_list(messages)

        return messages

    def accept_cookies(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[src*='lps.navigator-lxa.mail']")
                )
            )
        except:
            pass

        WebDriverWait(self.driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[src*='dl.mail.com']")
            )
        )

        WebDriverWait(self.driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[src*='plus.mail.com']")
            )
        )

        self.click(query=FindElement(by=By.ID, value="onetrust-accept-btn-handler"))

    def check_page_status(self):
        page_text = self.driver.find_element(By.TAG_NAME, "body").text

        if "reject.html" in self.driver.current_url or "Forbidden" in page_text.lower():
            raise IpAddressError(
                "Le site a bloqué votre IP à cause d'une activité suspecte 🚫🔒"
            )
