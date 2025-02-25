import random
import re
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import autospotify.settings as settings
from autospotify.exceptions import IpAddressError, RetryAgain
from autospotify.utils.base.automation.webmail import WebmailBase
from autospotify.utils.schemas import FindElement, User


class MailSignUp(WebmailBase):
    def __init__(self):
        super().__init__(user=None, base_url=settings.webmail_signup_url)

        username = f"""{self.faker.last_name().lower()}{self.faker.last_name().lower()}{self.faker.last_name().lower()}"""

        password = self.faker.password(
            length=15,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )

        self.user = User(username=username, password=password)
        self.domain = None

        self.tab = None
        self.proton_tab = None

    def update_user_object(self):
        self.log_step("rechanger username et mot de passe")

        username = f"""{self.faker.last_name().lower()}{self.faker.last_name().lower()}{self.faker.last_name().lower()}"""

        password = self.faker.password(
            length=15,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )

        self.user = User(username=username, password=password)

    def get_browser_tabs(self):
        handles = self.driver.window_handles

        self.tab = handles[0]

        try:
            self.proton_tab = handles[2]
        except:
            ...

    def username_step(self):
        self.log_step("taper le username")

        username_input = self.driver.find_element(
            By.CSS_SELECTOR, "input[data-test='check-email-availability-email-input']"
        )
        self.fill_input(username_input, self.user.username)

        self.click(
            query=FindElement(
                by=By.CSS_SELECTOR,
                value="button[data-test='check-email-availability-check-button']",
            )
        )  # Check if the email availability

        try:
            self.driver.find_element(
                By.CSS_SELECTOR,
                "[data-test='check-email-availability-failure-message']",
            )
        except NoSuchElementException:
            pass
        else:
            self.update_user_object()
            raise RetryAgain("Les domaines sont indisponibles 🌐 📧.")

        self.domain = "mail.com"

    def personal_details_step(self):
        self.log_step("taper des informations personnelles")

        # Chose gender
        genders = [
            {
                "by": By.CSS_SELECTOR,
                "value": "input[value='MALE']",
            },
            {
                "by": By.CSS_SELECTOR,
                "value": "input[value='FEMALE']",
            },
        ]

        gender = random.choice(genders)

        self.click(
            query=FindElement(by=gender["by"], value=gender["value"]),
            use_javascript=True,
        )

        # Fill first name
        first_name_input = self.driver.find_element(By.ID, "given-name")
        self.fill_input(first_name_input, self.faker.unique.first_name())

        # Fill last name
        last_name_input = self.driver.find_element(By.ID, "family-name")
        self.fill_input(last_name_input, self.faker.unique.last_name())

        # Fill country
        country_select = Select(
            self.driver.find_element(By.CSS_SELECTOR, "[data-test='country-input']")
        )
        country_select.select_by_value("FR")  # LA FRANCE

        # Fill Birthdate
        month_input = self.driver.find_element(By.ID, "bday-month")
        self.fill_input(month_input, str(random.randint(1, 12)))

        day_input = self.driver.find_element(By.ID, "bday-day")
        self.fill_input(day_input, str(random.randint(1, 20)))

        year_input = self.driver.find_element(By.ID, "bday-year")
        self.fill_input(year_input, str(random.randint(1990, 2005)))

    def password_step(self):
        self.log_step("taper le mot de passe")

        password_input = self.driver.find_element(By.ID, "password")
        self.fill_input(password_input, self.user.password)

        repeat_password_input = self.driver.find_element(By.ID, "confirm-password")
        self.fill_input(repeat_password_input, self.user.password)

    def phone_number_step(self):
        self.log_step("taper le numéro de téléphone")
        phone_input = self.driver.find_element(By.ID, "mobilePhone")
        phone_input.clear()
        self.fill_input(phone_input, self.phone_number)

    def recovery_step(self):
        self.log_step("taper des informations de recuperation du compte")
        self.phone_number_step()

    def activate_account_step(self):
        self.check_page_url(
            keyword="interception-lxa.mail.com", step_name="activation du compte mail"
        )

        try:
            self.submit_form(query=FindElement(by=By.ID, value="continueButton"))
        except NoSuchElementException:  # Activate account button din't find
            raise IpAddressError(
                "Le site a vous bloqué à cause d'une activité suspecte 🚫🔒"
            )

    def finalize_creation_step(self):
        self.log_step("finalizer la creation du compte")

        self.click(
            query=FindElement(
                by=By.CSS_SELECTOR,
                value="[data-test='create-mailbox-create-button']",
            ),
        )

        sleep(5)

        while True:
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, "[data-test='form-pending-message']"
                )  # Is account being created?
            except:
                break
            else:
                sleep(self.delay_start_interactions)
                continue

    def click_mail_box(self):
        mail_list = self.get_mail_list_step()
        self.click(mail_list["element"])

    def action(self):
        self.username_step()

        self.personal_details_step()

        self.password_step()

        self.recovery_step()

        self.finalize_creation_step()

        self.activate_account_step()

        self.check_page_url(keyword="navigator-lxa.mail.com", step_name="accueil")

        # upsert_user(
        #     user=User(
        #         username=f"{self.user.username}@{self.domain}",
        #         password=self.user.password,
        #         proxy_url=self.user.proxy_url
        #     ),
        # )
