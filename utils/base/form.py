import random
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from utils.base.time import Time
from utils.base.typer import Typer
from utils.schemas import FindElement


class Form(Time):
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def click(self, query: FindElement, use_javascript=False):
        element = self.driver.find_element(by=query.by, value=query.value)

        sleep(self.delay_start_interactions)

        if use_javascript:
            self.driver.execute_script("arguments[0].click();", element)
        else:
            element.click()

        sleep(self.delay_start_interactions)

    def select_random_option(self, select_element: Select):
        sleep(self.delay_start_interactions)

        options = select_element.options

        random_index = random.randint(1, len(options) - 1) if len(options) > 1 else 0
        select_element.select_by_index(random_index)

        sleep(self.delay_start_interactions)

    def select_random_email_domain(self, select_element: WebElement):
        sleep(self.delay_start_interactions)

        options = select_element.find_elements(By.TAG_NAME, "option")

        if not options:
            raise Exception("Aucune option trouvée dans la liste déroulante.")

        valid_options = [
            option for option in options if option.get_attribute("value").strip()
        ]

        if not valid_options:
            raise Exception("Aucune option valide disponible à sélectionner.")

        random_choice = random.choice(valid_options)
        self.driver.execute_script("arguments[0].selected = true;", random_choice)
        select_element.click()

        sleep(self.delay_start_interactions)
        return random_choice.get_attribute("value")

    def fill_input(self, element: WebElement, value: str):
        sleep(self.delay_start_interactions)

        element.clear()
        ty = Typer(
            accuracy=0.90, correction_chance=0.50, typing_delay=(0.04, 0.08), distance=2
        )
        ty.send(element, value)

        sleep(self.delay_start_interactions)
