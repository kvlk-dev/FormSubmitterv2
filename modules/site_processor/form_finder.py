import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
def run(driver):
    """Поиск формы на странице"""
    try:
        form_xpaths = [
            "//form",
            "//form//input[@type='submit'] | //form//button[@type='submit']",
            "//div[@role='form' or contains(@class, 'form') or contains(@class, 'contact') or contains(@data-form, 'true')]",
            "//div[descendant::input or descendant::textarea or descendant::select]",
            "//div[(descendant::input or descendant::textarea) and descendant::(button or input[@type='submit'])]",
        ]

        form = None

        for xpath in form_xpaths:
            try:
                form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if form:
                    break
            except TimeoutException:
                continue

        if not form:
            try:
                form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
            except TimeoutException:
                return None
        return form
    except Exception as e:
        logging.error(f"Ошибка при поиске формы: {e}")
        return None

