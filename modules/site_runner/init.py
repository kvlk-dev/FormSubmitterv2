import logging
import re
from urllib.parse import urlparse
from datetime import datetime
import time
from selenium import webdriver
import undetected_chromedriver as uc
from fake_useragent import UserAgent

from modules.google_service import add_formula, add_processing_status
from modules.site_runner import status_updater


class SiteRunner:
    def __init__(self):
        # Настройка опций для каждого нового экземпляра
        self.chrome_options = self.chrome_options_setup()
        self.firefox_options = self.firefox_options_setup()
    
    def site_runner(self, browser, idx, url,total,sheet):
        """Обработка сайта"""
        driver = None
        try:
            driver = self.browser_setup(browser)
            # Обработка URL
            processed_url = f'https://{url}' if not url.startswith('http') else url
            logging.info(f"Processing {idx - 1}/{total}: {processed_url}")
    
            # Обновление статуса
            add_formula.run(sheet, idx)
            add_processing_status.run(sheet, idx)
    
            # Основная обработка
            status, reason = self.process_site(processed_url)
            logging.info(f"Status: {status}, Reason: {reason}")
            logging.info(f"Slepping for 5 seconds before taking screenshot")

            time.sleep(5)
            status_updater.run(driver, sheet, idx, status, reason)
        except Exception as e:
            logging.critical(f"Critical error processing {url}: {str(e)}")
        finally:
            # Закрытие драйвера после обработки каждого сайта
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logging.warning(f"Ошибка при закрытии драйвера: {str(e)}")

    def browser_setup(self,browser):
        """Настройка браузера"""
        if browser.lower() == "chrome":
            driver = uc.Chrome(options=self.chrome_options)
        elif browser.lower() == "firefox":
            driver = webdriver.Firefox(options=self.firefox_options)
        else:
            logging.error(f"Неизвестный браузер: {browser}")
            return
        return driver

    def chrome_options_setup(self):
        """Настройка опций для Chrome"""
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f"--user-agent={UserAgent().chrome}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-mobile-emulation")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--force-device-scale-factor=1")
        return chrome_options

    def firefox_options_setup(self):
        """Настройка опций для Firefox"""
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.set_preference("general.useragent.override", UserAgent().firefox)
        firefox_options.add_argument("--start-maximized")
        firefox_options.add_argument("--window-size=1920,1080")
        return firefox_options