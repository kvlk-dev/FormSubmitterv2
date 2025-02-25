import logging
from urllib.parse import urlparse


def run(driver):
    """Проверка доступности сайта"""
    if "The Chromium Authors" in driver.page_source or "Mozilla Public - License" in driver.page_source:
        logging.warning(f"Сайт недоступен: {driver.title}")
        return False
    blocked_titles = [
        "domain is  parked",
        "this site can’t be reached", "domain expired",
        "access denied", "forbidden", "coming soon","godaddy",
        "page not found",
        "website expired", "website is under construction", "website coming soon",
    ]

    # Извлечение домена из URL
    url = driver.current_url

    # Проверка доступности страницы
    page_title = driver.title.lower()
    url_host = urlparse(url).netloc
    for blocked in blocked_titles:
        if blocked in page_title:
            logging.warning(f"Страница недоступна: {driver.title}")
            return False
    if url_host in page_title:
        logging.warning(f"Страница недоступна: {driver.title}")
        return False
    return True