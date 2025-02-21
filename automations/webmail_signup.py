import random
import re
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import settings
from exceptions import IpAddressError, RetryAgain
from utils.base import Base
from utils.schemas import FindElement, User


class MailSignUp(Base):
    def __init__(self):
        super().__init__(
            user=None, base_url=settings.webmail_signup_url, enable_captcha_solver=True
        )

        username = f"""{self.faker.last_name().lower()}{self.faker.last_name().lower()}{self.faker.last_name().lower()}"""

        password = self.faker.password(
            length=15,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )

        self.user = User(username=username, password=password)
        self.webmail_domain = None

        self.webmail_tab = None
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

        self.webmail_tab = handles[0]

        try:
            self.proton_tab = handles[2]
        except:
            ...

    def webmail_username_step(self):
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

        self.webmail_domain = "mail.com"

    def webmail_personal_details_step(self):
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

    def webmail_password_step(self):
        self.log_step("taper le mot de passe")

        password_input = self.driver.find_element(By.ID, "password")
        self.fill_input(password_input, self.user.password)

        repeat_password_input = self.driver.find_element(By.ID, "confirm-password")
        self.fill_input(repeat_password_input, self.user.password)

    def webmail_phone_number_step(self):
        self.log_step("taper le numéro de téléphone")
        phone_input = self.driver.find_element(By.ID, "mobilePhone")
        phone_input.clear()
        self.fill_input(phone_input, self.phone_number)

    def webmail_recovery_step(self):
        self.log_step("taper des informations de recuperation du compte")
        self.webmail_phone_number_step()

    def webmail_activate_account_step(self):
        self.check_page_url(
            keyword="interception-lxa.mail.com", step_name="activation du compte mail"
        )

        try:
            self.submit_form(query=FindElement(by=By.ID, value="continueButton"))
        except NoSuchElementException:  # Activate account button din't find
            raise IpAddressError(
                "Le site a vous bloqué à cause d'une activité suspecte 🚫🔒"
            )

    def webmail_finalize_creation_step(self):
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

    def webmail_click_mail_box(self):
        mail_list = self.get_mail_list_step()
        self.click(mail_list["element"])

    def proton_personal_details_step(self):
        self.log_step("remplissage des champs sur l'inscription (proton)")

        self.driver.switch_to.frame(1)

        email = self.driver.find_element(By.ID, "email")
        self.fill_input(email, self.user.username)

        self.driver.switch_to.default_content()

        password = self.driver.find_element(By.ID, "password")
        self.fill_input(password, self.user.password)

        repeat_password = self.driver.find_element(By.ID, "repeat-password")
        self.fill_input(repeat_password, self.user.password)

        self.click(query=FindElement(by=By.XPATH, value='//*[@type="submit"]'))

    def proton_finishing_registration(self):
        self.log_step("finalizer la creation du compte (proton)")
        # inbox?welcome=true
        sleep(5)

    def proton_select_free_subscription_step(self):
        self.log_step("continuer avec l'abonnement gratuit (proton)")

        self.click(
            query=FindElement(
                by=By.XPATH, value="//button[contains(text(), 'Continuer avec Free')]"
            )
        )  # Continue with free subscription

        try:
            self.click(
                query=FindElement(
                    by=By.CSS_SELECTOR, value="button[data-testid='modal:close']"
                )
            )  # Close promotion
        except NoSuchElementException:
            pass

    def proton_use_recovery_email_step(self):
        self.log_step("utilizer l'email de recuperation (proton)")

        try:
            self.click(
                query=FindElement(
                    by=By.CSS_SELECTOR, value='[data-testid="tab-header-e-mail-button"]'
                )
            )
        except:
            pass

        email_input = self.driver.find_element(By.ID, "email")
        self.fill_input(email_input, f"{self.user.username}@{self.webmail_domain}")

        self.submit_form(
            query=FindElement(
                by=By.XPATH,
                value="//button[contains(text(), 'un code de')]",
            )
        )

    def proton_verification_code(self, verification_code):
        self.log_step("taper le code verification envoyé par email (proton)")

        self.driver.switch_to.frame(1)

        verification_input = self.driver.find_element(By.ID, "verification")
        self.fill_input(verification_input, verification_code)

        self.submit_form(
            query=FindElement(
                by=By.XPATH, value="//button[contains(text(), 'Vérifier')]"
            )
        )

    def proton_verify_account_step(self):
        self.log_step("verifier le compte (proton)")

        sleep(5)
        self.driver.switch_to.window(self.webmail_tab)
        sleep(5)

        WebDriverWait(self.driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[src*='lxa.mail.com']")
            )
        )

        for _ in range(0, 2):
            refresh_button = self.driver.find_element(
                By.CSS_SELECTOR, ".refresh.navigation-tool-icon-link"
            )
            refresh_button.click()
            sleep(2)

        self.driver.switch_to.default_content()

        mail_list = self.get_mail_list_step()
        mail_found = False

        for mail in mail_list:
            if "Proton" in mail.sender:
                mail_found = True

                sleep(self.delay_start_interactions)
                mail.click()
                sleep(self.delay_start_interactions)
                break

        self.driver.switch_to.default_content()

        if mail_found:
            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[src*='lxa.mail.com']")
                )
            )

            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "mail-detail"))
            )

            code_element = self.driver.find_element(
                By.CSS_SELECTOR, "p.mcnTextContentContainer > span"
            )
            code = re.search(r"\b\d{6}\b", code_element.text)

            sleep(5)
            self.driver.switch_to.window(self.proton_tab)
            sleep(5)

            self.proton_verification_code(code)
        else:
            raise RetryAgain("L'email proton n'a pas etait trouvé")

    def action(self):
        self.webmail_username_step()

        self.webmail_personal_details_step()

        self.webmail_password_step()

        self.handle_captcha()

        self.webmail_recovery_step()

        self.webmail_finalize_creation_step()

        self.webmail_activate_account_step()

        self.check_page_url(keyword="navigator-lxa.mail.com", step_name="accueil")

        sleep(5)

        self.driver.switch_to.new_window("tab")

        self.get_browser_tabs()

        self.get_page(settings.proton_signup_url, show_ip=False)

        self.proton_personal_details_step()
        # self.proton_select_free_subscription_step()
        self.proton_use_recovery_email_step()

        self.proton_verify_account_step()

        # upsert_user(
        #     user=User(
        #         username=f"{self.user.username}@{self.webmail_domain}",
        #         password=self.user.password,
        #         proxy_url=self.user.proxy_url
        #     ),
        # )
