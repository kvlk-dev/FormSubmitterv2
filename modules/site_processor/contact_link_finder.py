import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def run(driver):
    """Поиск контактной ссылки на сайте"""
    contact_keywords = ["contact", "contact us", "get in touch", "request", "estimate", "quote", "call", "email",
                        "message", "write", "reach out", "connect", "send", "submit"]
    contact_link = None
    try:
        # Получаем все ссылки на странице
        links = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )

        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip().lower()
            aria_label = (link.get_attribute("aria-label") or "").strip().lower()
            title = (link.get_attribute("title") or "").strip().lower()

            # Проверяем текст ссылки, aria-label или title
            if any(re.search(rf"\b{kw}\b", text) for kw in contact_keywords) or \
                    any(re.search(rf"\b{kw}\b", aria_label) for kw in contact_keywords) or \
                    any(re.search(rf"\b{kw}\b", title) for kw in contact_keywords):

                if href and "mailto:" not in href and "tel:" not in href:
                    return href
    except Exception as e:
        logging.error(f"Ошибка при поиске контактной ссылки: {e}")
        return None

    if not contact_link:
        logging.warning("Контактная ссылка не найдена по заданным ключевым словам")
    return contact_link
