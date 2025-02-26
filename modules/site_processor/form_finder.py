import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


def run(driver):
    """Поиск видимой и кликабельной формы на странице"""
    try:
        # Оптимизированные XPath-селекторы
        form_selectors = [
            # Приоритетные селекторы
            "//form[.//input|.//textarea|.//select]",  # Форма с элементами ввода
            "//form[@role='form']",  # Явное указание роли

            # Дополнительные селекторы
            "//div[@role='form'][.//input|.//textarea]",  # Div с ролью формы
            "//div[contains(@class, 'form') and (.//input or .//textarea)]",  # Класс + элементы
            "//div[contains(@data-form, 'true')][.//button[@type='submit']]"  # data-атрибут
        ]

        # Ищем все возможные формы за общий таймаут
        form = WebDriverWait(driver, 15).until(
            EC.any_of(
                *[EC.visibility_of_element_located((By.XPATH, xpath))
                  for xpath in form_selectors]
            )
        )
        logging.info(f"Форма найдена: {form.tag_name}")
        return form

    except TimeoutException:
        logging.warning("Форма не найдена в течение 15 секунд")
        return None
    except Exception as e:
        logging.error(f"Критическая ошибка при поиске формы: {str(e)}", exc_info=True)
        return None