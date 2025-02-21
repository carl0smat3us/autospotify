import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import settings
from utils.base.automation.spotify import SpotifyBase
from utils.files import upsert_user
from utils.schemas import FindElement, User


class SpotifySignup(SpotifyBase):
    def __init__(self, user: User):
        super().__init__(user=user, base_url=settings.spotify_signup_url)

    def username_step(self):
        username_input = self.driver.find_element(By.ID, "username")
        self.fill_input(username_input, self.user.username)

        self.click(query=self.button_next)

    def password_step(self):
        self.check_page_url(keyword="step=1", step_name="taper le mot de passe")

        password_input = self.driver.find_element(By.NAME, "new-password")
        self.fill_input(password_input, self.user.password)

        self.click(query=self.button_next)

    def personal_details_step(self):
        self.check_page_url(keyword="step=2", step_name="taper les infos personelles")

        # Fill Name
        name_input = self.driver.find_element(By.NAME, "displayName")
        self.fill_input(name_input, self.faker.unique.first_name())

        # Fill Birthdate
        day_input = self.driver.find_element(By.NAME, "day")
        self.fill_input(day_input, str(random.randint(1, 20)))

        month_select = Select(self.driver.find_element(By.NAME, "month"))
        self.select_random_option(month_select)

        year_input = self.driver.find_element(By.NAME, "year")
        self.fill_input(year_input, str(random.randint(1990, 2005)))

        # Select Gender
        genders_list = ["gender_option_male", "gender_option_female"]
        self.click(
            query=FindElement(
                by=By.CSS_SELECTOR, value=f"label[for='{random.choice(genders_list)}']"
            )
        )

        self.click(query=self.button_next)

    def terms_step(self):
        self.check_page_url(keyword="step=3", step_name="les termes")

        def check_terms_box():
            try:
                self.click(
                    query=FindElement(
                        by=By.XPATH,
                        value='//label[@for="terms-conditions-checkbox"]/span[1]',
                    ),
                    use_javascript=True,
                )  # Check conditions and terms box
            except Exception:
                pass

        check_terms_box()

    def action(self):
        self.username_step()

        self.password_step()

        self.personal_details_step()

        self.terms_step()

        self.click(query=self.button_next)

        self.check_page_url(keyword="download", step_name="accueil")

        upsert_user(
            user=User(
                username=self.user.username,
                password=self.user.password,
                proxy_url=self.user.proxy_url,
                spotify_account_created="yes",
            ),
        )
