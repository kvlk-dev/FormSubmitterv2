import logging
import re

from selenium.webdriver.common.by import By


def run(driver):
    """Поиск контактных данных на сайте"""
    email = None
    phone = None
    try:
        # Поиск контактов
        contacts = driver.find_elements(By.XPATH,
            "//a[contains(@href, 'mailto:') or contains(@href, 'tel:') or contains(@href, 'skype:')]"
        )
        for contact in contacts:
            if "mailto:" in contact.get_attribute("href"):
                email = contact.get_attribute("href").replace("mailto:", "")
            elif "tel:" in contact.get_attribute("href"):
                phone = contact.get_attribute("href").replace("tel:", "")
        # оставляем только цифры в номере
        if phone:
            phone = re.sub(r'\D', '', phone)
        return email, phone
    except Exception as e:
        logging.error(f"Ошибка поиска контактов: {str(e)}")
    # Если контакты не найдены - regex  поиск
    try:
        page_source = driver.page_source
        email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        phone_pattern = re.compile(r"""
            (?:(?:\+?\d{1,3}[\s\.-]*)?)         # Опциональный международный код
            (?:(?:\(\d{2,4}\))|(?:\d{2,4}))       # Код региона в скобках или без
            [\s\.-]*                             # Разделители: пробел, точка, тире
            (?:\d{2,4}[\s\.-]*){2,4}              # Основная часть номера
            """, re.VERBOSE)
        emails = email_pattern.findall(page_source)
        phones = phone_pattern.findall(page_source)
        if emails:
            email = emails[0]
        if phones:
            phone = phones[0]
        if phone:
            phone = re.sub(r'\D', '', phone)
        return email, phone
    except Exception as e:
        logging.error(f"Ошибка поиска контактов через регулярное выражение: {str(e)}")
