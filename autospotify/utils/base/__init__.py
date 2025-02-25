import datetime
import random
from logging import ERROR
from os import path
from time import sleep
from typing import List

import keyboard
import undetected as uc
from chrome_extension import Extension
from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        InvalidSessionIdException,
                                        NoAlertPresentException,
                                        NoSuchWindowException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import autospotify.settings as settings
from autospotify.constants import USER_AGENTS
from autospotify.exceptions import RetryAgain
from autospotify.utils.base.form import Form
from autospotify.utils.base.time import Time
from autospotify.utils.browser import get_chrome_version
from autospotify.utils.captcha_solver import CaptchaSolver
from autospotify.utils.chrome_proxy import ChromeProxy
from autospotify.utils.files import read_proxies_from_txt, read_users_from_json
from autospotify.utils.logs import log
from autospotify.utils.proxies import (get_user_ip,
                                       proxy_transformed_url_to_dict)
from autospotify.utils.schemas import FindElement, User


class Base(Form, Time):
    def __init__(
        self,
        user: User,
        base_url: str,
        captcha_solver_enabled: bool,
        extensions: List[str] = [],
    ):
        self.faker = Faker()

        self.base_url = base_url

        self.retries = 0
        self.max_retries = 5

        self.user = user

        self.captcha_solver_enabled = captcha_solver_enabled
        self.captcha_solver_activated = False

        self.user_agent = random.choice(USER_AGENTS)
        self.proxies = read_proxies_from_txt()
        self.ip = get_user_ip()

        self.browser_options = webdriver.ChromeOptions()
        self.browser_options.add_argument("--disable-logging")
        self.browser_options.add_argument("--log-level=3")
        self.browser_options.add_argument("--disable-infobars")
        self.browser_options.add_argument("--window-size=1366,768")
        self.browser_options.add_argument("--start-maximized")
        self.browser_options.add_argument("--disable-notifications")
        self.browser_options.add_argument(f"--user-agent={self.user_agent}")
        self.browser_options.add_argument("--disable-dev-shm-usage")
        self.browser_options.add_argument("--disable-cookies")

        if self.captcha_solver_enabled:
            self.browser_options.add_experimental_option(
                "excludeSwitches", ["enable-automation", "enable-logging"]
            )
            self.browser_options.add_experimental_option(
                "prefs", {"profile.default_content_setting_values.notifications": 2}
            )
            self.browser_options.add_argument(
                CaptchaSolver(
                    api_key="59edebcdb934c8e84078e0f6ff325ae6",
                    download_dir=settings.extensions_path,
                ).load()
            )

        if len(self.proxies) == 0 and not self.user.proxy_url:
            log("🚨 Aucun proxy ! Utilisation de votre IP. 🌐🔍")

        if len(self.proxies) >= 1 or self.user.proxy_url:
            users = read_users_from_json()

            if not self.user.proxy_url:
                for proxy in self.proxies:
                    proxy_used = any(user.proxy_url == proxy for user in users)
                    if not proxy_used:
                        self.user.proxy_url = proxy

            proxy = proxy_transformed_url_to_dict(self.user.proxy_url)

            chrome_proxy = ChromeProxy(
                host=proxy.host,
                port=proxy.port,
                username=proxy.username,
                password=proxy.password,
            )

            extension_path = chrome_proxy.create_extension()
            self.browser_options.add_argument(f"--load-extension={extension_path}")

        for extension in extensions:
            self.browser_options.add_argument(
                Extension(
                    extension_link=extension,
                    chrome_version=get_chrome_version(),
                    download_dir=settings.extensions_path,
                ).load()
            )

        if self.captcha_solver_enabled:
            self.driver = webdriver.Chrome(
                options=self.browser_options,
            )
        else:
            self.driver = uc.Chrome(
                options=self.browser_options,
            )

        self.actions = ActionChains(self.driver)

        try:  # prevent error when the driver is minimized
            self.driver.maximize_window()
        except:
            ...

        Form.__init__(self, self.driver)
        Time.__init__(self)

    @property
    def phone_number(self):
        prefix = random.choice(["06", "07"])
        digits = "".join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{digits[:2]}{digits[2:4]}{digits[4:6]}{digits[6:8]}"

    def switch_back_to_main(self):
        self.log_step("retourner à la page principale")
        main_tab = self.driver.window_handles[0]
        self.driver.switch_to.window(main_tab)
        sleep(self.delay_start_interactions)

    def activate_captcha_solver(self):
        if not self.captcha_solver_activated:
            if len(self.driver.window_handles) == 1:
                # if the extension tab was'nt opened automatically open it
                self.driver.switch_to.new_window("tab")
                sleep(self.delay_start_interactions)
                self.get_page(
                    url="chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html",
                    is_first_request=False,
                )

            tabs = self.driver.window_handles
            main_tab = tabs[0]
            extension_tab = tabs[1]

            try:
                self.log_step("activation de l'extension")

                self.driver.switch_to.window(main_tab)
                sleep(2)

                self.driver.switch_to.window(extension_tab)
                self.check_page_url(keyword="chrome-extension")

                self.click(query=FindElement(by=By.ID, value="isPluginEnabled"))
                self.click(query=FindElement(by=By.ID, value="connect"))

                # Wait for alert to be present and handle it
                try:
                    WebDriverWait(self.driver, 15).until(EC.alert_is_present())

                    self.captcha_solver_activated = True
                    alert = self.driver.switch_to.alert
                    alert.accept()

                    log(
                        "✅ Connexion réussie à l'extension ! L'alerte a été détectée et fermée. 🚀"
                    )
                except NoAlertPresentException:
                    self.captcha_solver_activated = False
                    log("❌ Aucun message d'alerte trouvé.")

            except Exception as e:
                self.captcha_solver_activated = False
                log(f"Erreur lors de l'activation de l'extension: {str(e)}")

            self.switch_back_to_main()
            self.driver.refresh()
            sleep(self.delay_page_loading)

    def get_page(self, url: str, is_first_request=False):
        sleep(self.delay_start_interactions)

        self.driver.get(url)

        if is_first_request:
            self.ip = get_user_ip(self.user.proxy_url)
            log(f"🤖 Le bot est en train d'utiliser l'IP : {self.ip} 🌍")

            tabs = self.driver.window_handles
            if len(tabs) > 1:  # Assure that the main tab is active
                self.switch_back_to_main()

        self.verify_page()

    def action(self):
        """Run the automation step by step"""
        pass

    def check_page_status(self):
        """Check page errors, captchas and cookies not accepted"""
        pass

    def verify_page(self):
        """Check page status"""
        log("🔍 Vérification des erreurs, captchas et cookies 🚫🛑")
        sleep(self.delay_page_loading)  # Wait till the page full load

        self.close_browser_popup()
        self.check_page_status()
        self.handle_cookies()

    def check_page_url(self, keyword: str, step_name: str = None):
        log(f'🔍 Vérification du mot-clé "{keyword}"')

        sleep(self.delay_start_interactions)

        if keyword not in self.driver.current_url:
            raise RetryAgain(f"❌ Échec à l'étape {step_name} (mot-clé: {keyword})")

        if step_name:
            self.log_step(step_name)

    def run(self):
        def wrapper():
            self.get_page(url=self.base_url, is_first_request=True)
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
        """Accpet page cookies"""
        ...

    def handle_cookies(self):
        self.log_step("confirmer les cookies 🍪")
        try:
            sleep(self.delay_start_interactions)
            self.accept_cookies()
            sleep(self.delay_start_interactions)
            self.driver.switch_to.default_content()  # just in case
        except:
            pass
        else:
            log("Les cookies ont été acceptés 🍪")

    def close_browser_popup(self):
        self.log_step("fermer le popup (app link prompt)")

        for _ in range(10):  # Ensure that the App Link Prompt is being closed
            keyboard.send("esc")
            sleep(2)
        sleep(self.delay_start_interactions)

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

                except InvalidSessionIdException:
                    log("⚠️ Session invalide.", ERROR)
                    break

                except ElementNotInteractableException:
                    log("⚠️ L'élément n'est pas interactif.", ERROR)
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

            try:
                self.driver.quit()
            except:
                ...

        return inner_function
