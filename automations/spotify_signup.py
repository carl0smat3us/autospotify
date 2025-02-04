import random
import time

from faker import Faker
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import settings
from exceptions import RetryAgainError
from shared.base import Base
from shared.files import insert_user_to_json

faker = Faker()


class SpotifySignup(Base):
    def __init__(self, headless=False):
        super().__init__(
            username=f"""{faker.unique.first_name().lower()}{faker.unique.last_name().lower()}{
                faker.unique.first_name().lower()}@{random.choice(settings.spotify_supported_domains)}""",
            password=faker.password(),
            headless=headless,
        )
        self.url = settings.spotify_signup_url

    def fill_username(self):
        username_input = self.driver.find_element(By.ID, "username")
        username_input.send_keys(self.username)

        self.submit(self.click_next)

    def fill_password(self):
        password_input = self.driver.find_element(By.NAME, "new-password")
        password_input.send_keys(self.password)

        self.submit(self.click_next)

    def fill_personal_details(self):
        # Fill Name
        name_input = self.driver.find_element(By.NAME, "displayName")
        name_input.send_keys(self.faker.name())

        # Fill Birthdate
        day_input = self.driver.find_element(By.NAME, "day")
        day_input.send_keys(str(random.randint(1, 20)))

        month_select = Select(self.driver.find_element(By.NAME, "month"))
        month_select.select_by_index(random.randint(1, 12))

        year_input = self.driver.find_element(By.NAME, "year")
        year_input.send_keys(str(random.randint(1990, 2005)))

        # Select Gender
        genders_list = ["gender_option_male", "gender_option_female"]

        gender_option = self.driver.find_element(
            By.CSS_SELECTOR, f"label[for='{random.choice(genders_list)}']"
        )
        gender_option.click()

        self.submit(self.click_next)

    def check_terms_box(self):
        try:
            checkbox = self.driver.find_element(
                By.XPATH, '//label[@for="terms-conditions-checkbox"]/span[1]'
            )
            self.driver.execute_script("arguments[0].click();", checkbox)
        except Exception:
            pass

    def create_account(self):
        self.fill_username()
        self.fill_password()
        self.fill_personal_details()

        self.check_terms_box()  # Checks the terms and conditions box if required

        self.submit(self.click_next)

        insert_user_to_json(self.username, self.password)

    def run(self):
        while True:
            try:
                self.get_page(self.url, True)
                self.create_account()
                break  # Exit loop after successful execution

            except RetryAgainError:
                self.retries += 1

                if self.retries <= self.max_retries:
                    print(
                        f"({self.retries}) Nouvelle tentative en cours... Veuillez patienter."
                    )
                    continue

                print("Nombre maximal de tentatives atteint.")
                break

            except NoSuchWindowException:
                print("🚫 La fenêtre a été fermée.")
                self.driver.quit()
                break

            except Exception as e:
                print(f"Erreur pendant l'exécution du programme : {e}")
                self.driver.quit()
                break
