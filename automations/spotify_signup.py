import random
import time

from faker import Faker
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
        self.url = settings.spotify_registration_address

    def fill_username(self):
        username_input = self.driver.find_element(By.ID, "username")
        username_input.send_keys(self.username)
        time.sleep(1)
        self.click_next()

    def fill_password(self):
        password_input = self.driver.find_element(By.NAME, "new-password")
        password_input.send_keys(self.password)
        time.sleep(self.delay2)
        self.click_next()

    def fill_personal_details(self):
        # Fill Name
        name_input = self.driver.find_element(By.NAME, "displayName")
        name_input.send_keys(self.faker.name())

        # Fill Birthdate
        day_input = self.driver.find_element(By.NAME, "day")
        day_input.send_keys(str(random.randint(1, 31)))

        month_select = Select(self.driver.find_element(By.NAME, "month"))
        month_select.select_by_index(random.randint(1, 12))

        year_input = self.driver.find_element(By.NAME, "year")
        year_input.send_keys(str(random.randint(1970, 2000)))

        # Select Gender
        genders_list = ["gender_option_male", "gender_option_female"]

        gender_option = self.driver.find_element(
            By.CSS_SELECTOR, f"label[for='{random.choice(genders_list)}']"
        )
        gender_option.click()

        time.sleep(1)

        self.click_next()

    def create_account(self):
        self.accept_cookies()
        time.sleep(2)

        # Create the account
        self.fill_username()
        time.sleep(self.delay)

        self.fill_password()
        time.sleep(self.delay)

        self.fill_personal_details()
        time.sleep(self.delay)

        self.click_next()  # Confirm

        time.sleep(20)

        self.captcha_solver()

        print(f"Le compte {self.username} spotify a etait generé.")

        insert_user_to_json(self.username, self.password)

    def run(self):
        while True:
            try:
                self.driver.get(self.url)
                time.sleep(5)
                self.create_account()
                break  # Exit loop after successful execution
            except RetryAgainError:
                self.retries += 1

                if self.retries <= self.max_retries:
                    print(f"({self.retries}) Nouvelle tentative en cours...")
                    continue

                print("Nombre maximal de tentatives atteint.")
                break
            except Exception as e:
                print(f"Erreur pendant l'exécution du programme : {e}")
                self.driver.quit()
                break
