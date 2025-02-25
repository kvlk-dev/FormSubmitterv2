import sys
import time
import random
import logging
import os
from fake_useragent import UserAgent
from modules.app_service.config import Config
from modules.google_service import get_sites
from modules.google_service.init import GoogleService
from modules.site_runner import init


class FormSubmitter:
    def __init__(self):
        self.browser = None
        self.running = True
        self.ua = UserAgent()
        self.proxy = None
        self.captcha = None
        self.sheet = None
        self.drive = None
        self.worksheet = None
        self.captcha_api_key = None
        self.config = None
        self.config_class = Config()
        self.config = self.config_class.init()
        self.google_service = GoogleService(self.config)

    def update_config(self, new_config):
        """Обновление конфига с мерджем словарей"""
        self.config_class.update_config(new_config)

    def run_script(self):
        self.browser = self.config.get('browser', 'chrome').lower()
        self.running = True

        self.sheet = self.google_service.init()
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("screenshots/success", exist_ok=True)
        os.makedirs("screenshots/errors", exist_ok=True)
        profile_name = self.config.get("profile_name", "default")

        sites = get_sites.run(self.sheet)
        if not sites:
            logging.error("No sites found in spreadsheet")
            return

        for idx, url in sites:
            if not self.running:
                logging.info("Процесс остановлен пользователем.")
                break
            total = len(sites)
            site_runner = init.SiteRunner()
            site_runner.run(self.browser, idx, url, total, self.sheet,self.config)

            # Небольшая пауза между итерациями
            if self.running and idx < len(sites):
                    time.sleep(random.uniform(2, 5))

    def stop_script(self):
        self.running = False
        if self.thread:
            self.thread.join()  # Ожидание завершения потока

        self.driver.quit()  # Закрытие драйвера
        logging.info("Скрипт остановлен.")
        sys.exit(0)
