import random

from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import settings
from utils.base import Base
from utils.files import save_user

faker = Faker()


class SpotifySignup(Base):
    def __init__(self, headless=False):
        super().__init__(
            username=f"""{faker.unique.first_name().lower()}{faker.unique.last_name().lower()}{
                faker.unique.first_name().lower()}@{random.choice(settings.spotify_supported_domains)}""",
            password=faker.password(
                length=15,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ),
            headless=headless,
        )
        self.url = settings.spotify_signup_url

    def username_step(self):
        username_input = self.driver.find_element(By.ID, "username")
        username_input.send_keys(self.username)

        self.submit(self.click_next)

    def password_step(self):
        self.verify_page_url("taper le mot de passe", "step=1")

        password_input = self.driver.find_element(By.NAME, "new-password")
        password_input.send_keys(self.password)

        self.submit(self.click_next)

    def personal_details_step(self):
        self.verify_page_url("taper le mot de passe", "step=2")

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

    def terms_step(self):
        self.verify_page_url("taper le mot de passe", "step=3")

        def check_terms_box():
            try:
                checkbox = self.driver.find_element(
                    By.XPATH, '//label[@for="terms-conditions-checkbox"]/span[1]'
                )
                self.driver.execute_script("arguments[0].click();", checkbox)
            except Exception:
                pass

        check_terms_box()  # Depends of user's country

    def action(self):
        self.username_step()

        self.password_step()

        self.personal_details_step()

        self.terms_step()

        self.submit(self.click_next, 20)
        save_user(self.username, self.password)
