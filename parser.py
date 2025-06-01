import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from __init__ import logger


def get_evaluations_screenshot(login, password):
    BMSTU_LOGIN = login or os.getenv("BMSTU_LOGIN")
    BMSTU_PASSWORD = password or os.getenv("BMSTU_PASSWORD")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=800,800")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.implicitly_wait(10)

        logger.info(
            "Открываю e-learning.bmstu.ru/kaluga/login/index.php с кредами: login:{login} password:{password}")
        driver.get("https://e-learning.bmstu.ru/kaluga/login/index.php")

        cas_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.potentialidplist"))
        )
        cas_button.click()
        logger.success("Переход на страницу авторизации CAS")

        WebDriverWait(driver, 20).until(
            EC.url_contains("proxy.bmstu.ru:8443/cas/login")
        )

        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")
        submit_button = driver.find_element(By.NAME, "submit")

        username_field.send_keys(BMSTU_LOGIN)
        password_field.send_keys(BMSTU_PASSWORD)
        submit_button.click()

        WebDriverWait(driver, 20).until(
            EC.url_contains("e-learning.bmstu.ru/kaluga")
        )
        logger.success("Успешная авторизация")

        time.sleep(3)

        menu_toggle = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "li.nav-item.d-flex.m_user.align-items-center a.dropdown-toggle"))
        )
        menu_toggle.click()

        grades_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'menu-action') and .//span[contains(text(), 'Оценки')]]"))
        )
        grades_link.click()

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "no-overflow"))
        )

        grades_block = driver.find_element(By.CLASS_NAME, "no-overflow")

        screenshot_path = "evaluations.png"

        element_size = grades_block.size
        element_height = element_size['height']

        driver.set_window_size(880, max(800, element_height + 100))

        driver.execute_script(
            "arguments[0].scrollIntoView(true);", grades_block)
        time.sleep(1)

        grades_block.screenshot(screenshot_path)

        return screenshot_path

    except Exception as e:
        logger.error(f"Ошибка в процессе работы: {str(e)}")
        if driver:
            driver.save_screenshot("error.png")
            logger.error("Ошибка: error.png")
        return None
    finally:
        if driver:
            driver.quit()
            logger.info("Браузер закрыт")


