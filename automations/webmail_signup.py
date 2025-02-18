import random
from time import sleep

# import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import settings
from exceptions import RetryAgain
from utils.base import Base
from utils.files import upsert_user
from utils.schemas import FindElement, User


class MailSignUp(Base):
    def __init__(self):
        super().__init__(
            user=None, base_url=settings.webmail_signup_url, enable_captcha_solver=True
        )

        username = f"""{self.faker.unique.first_name().lower()}{self.faker.unique.last_name().lower()}{
                self.faker.unique.first_name().lower()}"""

        password = self.faker.password(
            length=15,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )

        self.user = User(username=username, password=password)
        self.mail_domain = None

    def username_step(self):
        self.log_step("taper le username")

        username_input = self.driver.find_element(
            By.CSS_SELECTOR, "input[data-test='check-email-availability-email-input']"
        )
        self.fill_input(username_input, self.user.username)

        domain_select_element = self.driver.find_element(
            By.CSS_SELECTOR,
            "select[data-test='check-email-availability-email-domain-input']",
        )
        self.mail_domain = self.select_random_email_domain(domain_select_element)

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
            raise RetryAgain("Les domaines sont indisponibles 🌐 📧.")

        self.user.username = f"{self.user.username}@{self.mail_domain}"

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
        day_input = self.driver.find_element(By.ID, "bday-day")
        self.fill_input(day_input, str(random.randint(1, 20)))

        month_select = self.driver.find_element(By.ID, "bday-month")
        self.fill_input(month_select, str(random.randint(1, 12)))

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
        # mobile_prefix = Select(
        #     self.driver.find_element(
        #         By.CSS_SELECTOR, "[data-test='mobile-phone-prefix-input']"
        #     )
        # )

        # match = re.match(r"([A-Z]{2})", mobile_prefix.first_selected_option.text)
        # iso_code = match.group(1)
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
        self.submit_form(query=FindElement(by=By.ID, value="continueButton"))

    def create_account(self):
        while True:
            self.click(
                query=FindElement(
                    by=By.CSS_SELECTOR,
                    value="[data-test='create-mailbox-create-button']",
                ),
            )

            sleep(5)

            try:  # Fix phone number bug
                self.driver.find_element(
                    By.CLASS_NAME,
                    "mobile-phone-message",
                )
            except NoSuchElementException:
                break
            else:
                print("found error")
                self.phone_number_step()
                continue

    def action(self):
        self.username_step()

        self.personal_details_step()

        self.password_step()

        self.recovery_step()

        self.handle_captcha(self.create_account)

        self.activate_account_step()

        self.check_page_url(keyword="navigator-lxa.mail.com", step_name="accueil")

        upsert_user(
            user=User(
                username=self.user.username,
                password=self.user.password,
            ),
        )
