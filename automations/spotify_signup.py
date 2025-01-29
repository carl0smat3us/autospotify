import random
import time

from faker import Faker
from pystyle import Colors
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import settings
from shared.base import Base
from shared.files import add_user_to_csv

faker = Faker()

email_domains = [
    "proton.me",
    "gmail.com",
    "outlook.com",
    "outlook.be",
    "free.fr",
    "icloud.com",
]


class SpotifySignup(Base):
    def __init__(self, headless=False):
        super().__init__(
            username=f"{faker.unique.first_name().lower()}{faker.unique.last_name().lower()}{
                faker.unique.first_name().lower()}@{random.choice(email_domains)}",
            password=faker.password(),
            headless=headless,
        )
        self.url = settings.spotify_registration_address

    def accept_cookies(self):
        try:
            cookies_button = self.driver.find_element(
                By.ID, "onetrust-accept-btn-handler"
            )
            cookies_button.click()
        except Exception as e:
            print(f"Error accepting cookies: {e}")

    def fill_username(self):
        try:
            username_input = self.driver.find_element(
                By.CSS_SELECTOR, "input[placeholder='name@domain.com']"
            )
            username_input.send_keys(self.username)
            time.sleep(1)
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='submit']"
            )
            submit_button.click()
        except Exception as e:
            print(f"Error filling username: {e}")

    def fill_password(self):
        try:
            password_input = self.driver.find_element(By.NAME, "new-password")
            password_input.send_keys(self.password)
            time.sleep(self.delay2)
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='submit']"
            )
            submit_button.click()
        except Exception as e:
            print(f"Error filling password: {e}")

    def fill_personal_details(self):
        try:
            # Fill Name
            name_input = self.driver.find_element(By.NAME, "displayName")
            name_input.send_keys(self.faker.name())

            # Fill Birthdate
            day_input = self.driver.find_element(By.NAME, "day")
            day_input.send_keys(str(random.randint(1, 31)))

            month_select = Select(self.driver.find_element(By.NAME, "month"))
            month_select.select_by_visible_text("April")

            year_input = self.driver.find_element(By.NAME, "year")
            year_input.send_keys(str(random.randint(1970, 2000)))

            # Select Gender
            gender_option = self.driver.find_element(
                By.CSS_SELECTOR, "label[for='gender_option_male']"
            )
            gender_option.click()

            time.sleep(1)

            # Click next
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='submit']"
            )
            submit_button.click()
        except Exception as e:
            print(f"Error filling personal details: {e}")

    def create_account(self):
        try:
            time.sleep(5)
            self.accept_cookies()
            time.sleep(2)

            # Step 1: Fill username
            self.fill_username()
            time.sleep(self.delay)

            # Step 2: Fill password
            self.fill_password()
            time.sleep(self.delay)

            # Step 3: Fill personal details
            self.fill_personal_details()
            time.sleep(self.delay)

            # Final step: Create account button click
            final_submit = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='submit']"
            )
            final_submit.click()

            time.sleep(self.delay)

            print(Colors.green, "Spotify account created!")
            add_user_to_csv(self.username, self.password)
        except Exception as e:
            print(f"Error during account creation: {e}")

    def run(self):
        try:
            self.driver.get(self.url)
            self.create_account()
        finally:
            self.driver.quit()
