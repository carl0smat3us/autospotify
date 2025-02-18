import datetime
import random
from logging import ERROR
from os import getenv, path
from time import sleep

import pytz
from fake_useragent import UserAgent
from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_authenticated_proxy import SeleniumAuthenticatedProxy
from twocaptcha_extension_python import TwoCaptcha

import settings
from exceptions import RetryAgain
from utils.base.form import Form
from utils.base.time import Time
from utils.files import read_proxies_from_txt
from utils.logs import log
from utils.proxies import get_user_ip, transform_proxy
from utils.schemas import FindElement, User

ua = UserAgent(os=["Windows", "Linux", "Ubuntu"])


class Base(Form, Time):
    def __init__(
        self, user: User, base_url: str, extensions=[], enable_captcha_solver=False
    ):
        self.faker = Faker()

        self.base_url = base_url

        self.retries = 0
        self.max_retries = 5
        self.enable_captcha_solver = enable_captcha_solver

        self.user = user

        self.proxy_url = None
        self.user_agent = ua.random
        self.proxies = read_proxies_from_txt()
        self.ip = get_user_ip()

        self.solved_captchas = 0

        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

        self.browser_options.add_argument("--disable-logging")
        self.browser_options.add_argument("--log-level=3")
        self.browser_options.add_argument("--disable-infobars")
        self.browser_options.add_argument("--window-size=1366,768")
        self.browser_options.add_argument("--start-maximized")
        self.browser_options.add_argument("--disable-notifications")
        self.browser_options.add_argument(f"--user-agent={self.user_agent}")
        self.browser_options.add_argument("--disable-dev-shm-usage")
        self.browser_options.add_argument("--disable-cookies")
        self.browser_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        # if "ublock" in extensions:
        #     self.browser_options.add_argument(
        #         Extension(
        #             extension_id="cjpalhdlnbpafiamejdnhcphjbkeiagm",
        #             extension_name="ublock",
        #             chrome_version=self.browser_options.browser_version,
        #         ).load()
        #     )

        if enable_captcha_solver:
            self.browser_options.add_argument(
                TwoCaptcha(api_key=getenv("TWO_CAPTCHA_API_KEY")).load()
            )

        if len(self.proxies) == 0:
            log("🚨 Aucun proxy ! Utilisation de votre IP. 🌐🔍")

        if len(self.proxies) >= 1:
            self.proxy_url = self.proxies[random.randint(0, len(self.proxies) - 1)]

            proxy_data = transform_proxy(self.proxy_url)

            proxy_helper = SeleniumAuthenticatedProxy(proxy_url=proxy_data)
            proxy_helper.enrich_chrome_options(self.browser_options)

        for extension in extensions:
            self.browser_options.add_extension(extension)

        self.driver = webdriver.Chrome(
            options=self.browser_options,
        )

        self.driver.maximize_window()

        self.set_random_timezone()
        self.set_fake_geolocation()

        Form.__init__(self, self.driver)
        Time.__init__(self)

    def set_random_timezone(self):
        self.driver.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": random.choice(pytz.all_timezones)},
        )

    def set_fake_geolocation(self):
        params = {
            "latitude": random.uniform(-90, 90),
            "longitude": random.uniform(-180, 180),
            "accuracy": 100,
        }
        self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

    @property
    def phone_number(self):
        prefix = random.choice(["06", "07"])
        digits = "".join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix} {digits[:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]}"

    def activate_captcha_solver(self):
        handles = self.driver.window_handles

        main_tab = handles[0]
        extension_tab = handles[1]

        try:
            self.log_step("activation de l'extension")

            self.driver.switch_to.window(main_tab)
            sleep(2)
            self.driver.switch_to.window(extension_tab)

            self.check_page_url(keyword="chrome-extension")

            self.click(query=FindElement(by=By.ID, value="connect"))

            # Wait for alert to be present and handle it
            try:
                WebDriverWait(self.driver, 15).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert.accept()
                log(
                    "✅ Connexion réussie à l'extension ! L'alerte a été détectée et fermée. 🚀"
                )
            except NoAlertPresentException:
                log("❌ Aucun message d'alerte trouvé.")

        except Exception as e:
            log(f"Erreur lors de l'activation de l'extension: {str(e)}")

        sleep(self.delay_start_interactions)
        self.driver.switch_to.window(main_tab)

    @property
    def solve_captcha_button(self):
        button = FindElement(
            by=By.CSS_SELECTOR, value=".captcha-solver.captcha-solver_inner"
        )

        return button

    def handle_captcha(self, callback):
        self.click(query=self.solve_captcha_button, use_javascript=True)

        while True:
            captcha_status = self.driver.find_element(
                by=self.solve_captcha_button.by, value=self.solve_captcha_button.value
            )
            state = captcha_status.get_attribute("data-state")

            if state == "solving":
                sleep(3)
                continue
            elif state == "solved":
                self.solved_captchas += 1
                callback()
                break
            else:
                raise RetryAgain("❌ Captcha non résolu.")

    def get_page(self, url: str, show_ip=False):
        if show_ip:
            self.ip = get_user_ip(self.proxy_url)
            log(f"🤖 Le bot est en train d'utiliser l'IP : {self.ip} 🌍")

        self.driver.get(url)
        self.verify_page()

    def action(self):
        """Run the automation step by step"""
        pass

    def verify_page(self):
        """Check page errors, captchas and cookies not accepted"""
        log("🔍 Vérification des erreurs, captchas et cookies 🚫🛑")

        sleep(self.delay_page_loading)  # Wait till the page full load

        page_text = self.driver.find_element(By.TAG_NAME, "body").text

        if "upstream request timeout" in page_text.lower():
            raise RetryAgain(
                "La page indique un délai d'attente de la requête en amont. Arrêt du processus..."
            )

        elif "challenge.spotify.com" in self.driver.current_url:
            raise RetryAgain(
                "CAPTCHA détecté! Aucun solveur CAPTCHA implémenté. Arrêt du processus..."
            )

        self.accept_cookies()
        sleep(self.delay_start_interactions)

    def check_page_url(self, keyword: str, step_name: str = None):
        log(f'🔍 Vérification du mot-clé "{keyword}"')

        sleep(self.delay_start_interactions)

        if keyword not in self.driver.current_url:
            raise RetryAgain(f"❌ Échec à l'étape {step_name} (mot-clé: {keyword})")

        if step_name:
            self.log_step(step_name)

    def run(self):
        def wrapper():
            self.get_page(self.base_url, True)
            if self.enable_captcha_solver:
                self.activate_captcha_solver()
            self.action()

        run = self.run_preveting_errors(wrapper)
        run()

    def log_step(self, step: str):
        log(f"✅ Le bot {self.user.username} est à l'étape '{step}' 🎯")

    def screenshot_error(self, message: str = None):
        timestamp = (
            datetime.datetime.now()
            .strftime(settings.logging_datefmt)
            .replace(" ", "_")
            .replace(":", "_")
        )

        screenshot_path = path.join(
            settings.logs_screenshots_folder, f"{timestamp}.png"
        )

        if message:
            log(message, ERROR)
        self.driver.save_screenshot(screenshot_path)

    def submit_form(self, query: FindElement, use_javascript=False):
        self.click(query, use_javascript)
        self.verify_page()

    def accept_cookies(self):
        try:
            sleep(self.delay_start_interactions)

            if (
                "mail.com" in self.driver.current_url
                or "navigator-lxa.mail.com" in self.driver.current_url
            ):
                WebDriverWait(self.driver, 15).until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.CSS_SELECTOR, "iframe[src*='dl.mail.com']")
                    )
                )

                WebDriverWait(self.driver, 15).until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.CSS_SELECTOR, "iframe[src*='plus.mail.com']")
                    )
                )

            self.click(query=FindElement(by=By.ID, value="onetrust-accept-btn-handler"))
            sleep(self.delay_start_interactions)
            self.driver.switch_to.default_content()
        except:
            pass
        else:
            log("Les cookies ont été acceptés 🍪")

    def run_preveting_errors(self, run):
        def inner_function(*args, **kwargs):
            while True:
                try:
                    run(*args, **kwargs)
                    break

                except RetryAgain:
                    self.retries += 1
                    if self.retries <= self.max_retries:
                        self.screenshot_error()
                        log(
                            f"🔄 ({self.retries}) Nouvelle tentative en cours... Veuillez patienter."
                        )
                        self.driver.refresh()
                        continue

                    log("Nombre maximal de tentatives atteint.", ERROR)
                    break

                except NoSuchWindowException:
                    log("🚫 La fenêtre a été fermée.", ERROR)
                    break

                except KeyboardInterrupt:
                    log("🛑 Le script a été arrêté manuellement. ⏹️", ERROR)
                    break

                except Exception as e:
                    self.screenshot_error(
                        f"Error pendant l'execution de l'application: {e}"
                    )
                    break

            self.driver.quit()

        return inner_function
