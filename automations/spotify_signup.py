import random
import time

from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import settings
from shared.base import Base
from shared.files import insert_user_to_json

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
            username=f"""{faker.unique.first_name().lower()}{faker.unique.last_name().lower()}{
                faker.unique.first_name().lower()}@{random.choice(email_domains)}""",
            password=faker.password(),
            headless=headless,
        )
        self.url = settings.spotify_registration_address

    def fill_username(self):
        try:
            username_input = self.driver.find_element(By.ID, "username")
            username_input.send_keys(self.username)
            time.sleep(1)
            self.click_next()
        except Exception as e:
            print(f"Error filling username: {e}")
            self.driver.quit()

    def fill_password(self):
        try:
            password_input = self.driver.find_element(By.NAME, "new-password")
            password_input.send_keys(self.password)
            time.sleep(self.delay2)
            self.click_next()
        except Exception as e:
            print(f"Error filling password: {e}")
            self.driver.quit()

    def fill_personal_details(self):
        try:
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

        except Exception as e:
            print(f"Error filling personal details: {e}")
            self.driver.quit()

    def choose_an_artist(self):
        try:
            # Check if Spotify displays a pop-up asking to choose favorite artists
            self.driver.find_element(
                By.XPATH,
                '//*[@data-testid="popover"]/div[@class="encore-announcement-set" and @role="tooltip"]',
            )
            print("Pop-up detected: Spotify is asking to choose favorite artists.")
        except Exception:
            print("No pop-up detected: Proceeding with the process...")
            return

        artists = [
            "Post Malone",
            "Gims",
            "Portugal Man",
            "Kendrick Lamar",
            "Eminem",
            "Justin Bieber",
        ]

        try:
            search_bar = self.driver.find_element(
                By.XPATH,
                "//*[@id='global-nav-bar']/div[2]/div/div/span/div/form/div[2]/input",
            )

            search_bar.send_keys(random.choice(artists))

            time.sleep(15)

            artists_table = self.driver.find_element(
                "xpath",
                "//span[@role='presentation' and @aria-expanded='true' and @data-open='true']",
            ).find_element("xpath", "..")

            time.sleep(5)

            first_artist = artists_table.find_element(
                By.XPATH, './div[@span="presentation"][1]'
            )

            first_artist.click()

            time.sleep(15)

            self.play()

            time.sleep(50)

            self.driver.quit()

        except Exception as e:
            print(f"Error while choosing an artist: {e}")
            self.driver.quit()

    def create_account(self):
        try:
            time.sleep(5)

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
            self.choose_an_artist()

            print("Le compte spotify a etait generé.")
            insert_user_to_json(self.username, self.password)

        except Exception as e:
            print(f"Error during account creation: {e}")
            self.driver.quit()

    def run(self):
        try:
            self.driver.get(self.url)
            self.create_account()
        except:
            self.driver.quit()
