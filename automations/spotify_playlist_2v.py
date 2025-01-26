import random
import time

import keyboard
import pytz
from pystyle import Colors
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from settings import spotify_login_address, spotify_track_url

supported_timezones = pytz.all_timezones


def set_random_timezone(driver):
    random_timezone = random.choice(supported_timezones)
    driver.execute_cdp_cmd(
        "Emulation.setTimezoneOverride", {"timezoneId": random_timezone}
    )


def set_fake_geolocation(driver, latitude, longitude):
    params = {"latitude": latitude, "longitude": longitude, "accuracy": 100}
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)


def main(username, password):
    user_agents = [
        # Chrome (Windows)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        # Additional user agents omitted for brevity
    ]

    supported_languages = [
        "en-US",
        "en-GB",
        "en-CA",
        "fr-FR",
        "de-DE",
        "es-ES",
        "it-IT",
        "ja-JP",
        "ko-KR",
        "pt-BR",
        "ru-RU",
        "nl-NL",
        "sv-SE",
        "da-DK",
        "no-NO",
    ]

    random_user_agent = random.choice(user_agents)
    drivers = []

    delay = random.uniform(2, 6)
    delay2 = random.uniform(5, 14)
    random_language = random.choice(supported_languages)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument("--lang=en-US,en;q=0.9")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument(f"--user-agent={random_user_agent}")
    chrome_options.add_argument(f"--lang={random_language}")
    # chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 2}
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    try:
        driver.get(spotify_login_address)

        username_input = driver.find_element(By.CSS_SELECTOR, "input#login-username")
        password_input = driver.find_element(By.CSS_SELECTOR, "input#login-password")

        username_input.send_keys(username)
        password_input.send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='login-button']"
        ).click()
        time.sleep(delay)

        driver.get(spotify_track_url)
        driver.maximize_window()

        keyboard.press_and_release("esc")
        time.sleep(10)

        try:
            cookie = driver.find_element(By.XPATH, "//button[text()='Accept Cookies']")
            cookie.click()
        except NoSuchElementException:
            try:
                button = driver.find_element(
                    By.ID,
                    "onetrust-accept-btn-handler",
                )
                button.click()
            except NoSuchElementException:
                time.sleep(delay2)

        time.sleep(10)

        # playmusic_xpath = "(//button[@data-testid='play-button']//span)[3]"
        playmusic = driver.find_element(
            By.XPATH,
            "//*[@id='main']/div/div[2]/div[4]/div/div[2]/div[2]/div/main/section/div[3]/div[2]/div/div/div/button/span",
        )
        playmusic.click()

        time.sleep(10)

        print(
            Colors.green,
            "Username: {} - Listening process has started.".format(username),
        )

    except Exception as e:
        print(Colors.red, "An error occurred in the bot system:", str(e))

    set_random_timezone(driver)

    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    set_fake_geolocation(driver, latitude, longitude)

    drivers.append(driver)
    time.sleep(5)

    print(
        Colors.blue,
        "Stream operations are completed. You can stop all transactions by closing the program.",
    )

    while True:
        pass
