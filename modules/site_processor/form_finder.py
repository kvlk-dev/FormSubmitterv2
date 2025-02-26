import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

def run(driver):
    """Поиск формы с использованием комбинированного подхода"""
    try:
        # Сначала ищем стандартную форму
        try:
            form = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'form'))
            )
            logging.info(f"Стандартная форма найдена: {form.tag_name}")
            return form
        except TimeoutException:
            logging.info("Стандартная форма не найдена, ищем через расширенные селекторы")

        # Если стандартная форма не найдена, используем расширенные селекторы
        form_selectors = [
            "//form[.//input|.//textarea|.//select]",
            "//form[@role='form']",
            "//div[@role='form'][.//input|.//textarea]",
            "//div[contains(@class, 'form') and (.//input or .//textarea)]",
            "//div[contains(@data-form, 'true')][.//button[@type='submit']]"
        ]

        form = WebDriverWait(driver, 10).until(
            EC.any_of(
                *[EC.visibility_of_element_located((By.XPATH, xpath))
                  for xpath in form_selectors]
            )
        )
        logging.info(f"Форма найдена через расширенные селекторы: {form.tag_name}")
        return form

    except TimeoutException:
        logging.warning("Форма не найдена в течение 20 секунд")
        return None
    except Exception as e:
        logging.error(f"Критическая ошибка при поиске формы: {str(e)}", exc_info=True)
        return None