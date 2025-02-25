import logging

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
def run(driver, initial_phone: str) -> str | tuple[str, str]:
    """
    Извлечение первых 3 цифр из номера на сайте и добавление к нашему номеру.
    Сначала ищем ссылки с "tel:". Если ссылки не найдены, сканируем HTML-код страницы
    по регулярному выражению, охватывающему различные варианты оформления телефонных номеров.
    """
    # 1. Пытаемся найти номер через ссылки (href с tel:)
    try:
        phone_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'tel:')]"))
        )
        if phone_links:
            raw_phone = phone_links[0].get_attribute('href')
            # Убираем всё, что не цифра
            digits = re.sub(r'\D', '', raw_phone)
            if len(digits) >= 3:
                site_code = digits[:3]
                clean_our_phone = re.sub(r'\D+', '', initial_phone)
                number = f"{site_code}{clean_our_phone}"
                return format(number)
    except Exception as e:
        logging.warning(f"Ошибка обработки телефона через ссылку: {str(e)}")

    # 2. Если ссылок нет, ищем номер в HTML-коде страницы по регулярному выражению
    try:
        page_source = driver.page_source
        phone_pattern = re.compile(r"""
            (?:(?:\+?\d{1,3}[\s\.-]*)?)         # Опциональный международный код
            (?:(?:\(\d{2,4}\))|(?:\d{2,4}))       # Код региона в скобках или без
            [\s\.-]*                             # Разделители: пробел, точка, тире
            (?:\d{2,4}[\s\.-]*){2,4}              # Основная часть номера
            """, re.VERBOSE)
        matches = phone_pattern.findall(page_source)
        if matches:
            for match in matches:
                digits = re.sub(r"\D", "", match)
                if len(digits) >= 3:
                    site_code = digits[:3]
                    clean_our_phone = re.sub(r'\D+', '', initial_phone)
                    return format(f"{site_code}{clean_our_phone}")
    except Exception as e:
        logging.warning(f"Ошибка обработки телефона через регулярное выражение: {str(e)}")

    # Если ничего не найдено – возвращаем номер из конфигурации по умолчанию
    return format(initial_phone)

def format(phone: str) -> str:
    import re
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return digits.zfill(10)[:10]  # Возвращаем первые 10 циф