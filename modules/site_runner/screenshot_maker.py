import re
from urllib.parse import urlparse


def run(driver, processed_url=None, status=None):
    """Создание скриншота"""
    url_host = urlparse(processed_url).netloc
    url_host = re.sub(r'[^\w\-_\. ]', '_', url_host)
    screenshot_path = f"screenshot_{url_host}.png"
    screenshot_url = screenshot_path
    screenshot_path = f"screenshots/{status.lower()}/{screenshot_url}"
    driver.save_screenshot(screenshot_path)
    return screenshot_url