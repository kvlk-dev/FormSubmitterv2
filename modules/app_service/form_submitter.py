import sys
import time
import random
import logging
import os
from fake_useragent import UserAgent

from modules.app_service.config import Config
from modules.app_service.progress_window import ProgressWindow
from modules.google_service import get_sites
from modules.google_service.init import GoogleService
from modules.site_runner import init


class FormSubmitter:
    def __init__(self):
        self.thread = None
        self.browser = None
        self.running = False
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
        self.driver = None
        self.progress_window = None
        self.stop_button = None
        self.start_button = None

    def set_progress_window(self, window):
        """Установка ссылки на окно прогресса"""
        self.progress_window = window

    def update_progress(self, current, total=None):
        """Обновление прогресс-бара"""
        if self.progress_window:
            self.progress_window.queue.put(("progress", {"current": current, "total": total}))

    def update_config(self, new_config):
        """Обновление конфига с мерджем словарей"""
        self.config_class.update_config(new_config)

    def run_script(self):
        """Запуск скрипта"""
        try:
            self.browser = self.config.get('browser', 'chrome').lower()
            self.running = True

            self.sheet = self.google_service.init()
            os.makedirs("screenshots", exist_ok=True)
            os.makedirs("screenshots/success", exist_ok=True)
            os.makedirs("screenshots/error", exist_ok=True)
            profile_name = self.config.get("profile_name", "default")

            sites = get_sites.run(self.sheet)
            if not sites:
                logging.error("No sites found in spreadsheet")
                return

            total = len(sites)
            # Вместо прямого вызова методов окна
            #self.progress_window.queue.put(("progress", 0))
            self.progress_window.queue.put(("total", total))
            count = 0
            for idx, url in sites:

                if not self.running:
                    logging.info("Процесс остановлен пользователем.")
                    break
                # Вместо прямого вызова методов окна
                site_runner = init.SiteRunner()
                site_runner.run(self.browser, idx, url, total, self.sheet,self.config)
                count += 1
                self.progress_window.queue.put(("progress", count))

                # Небольшая пауза между итерациями
                if self.running and idx < len(sites):
                        time.sleep(random.uniform(2, 5))
        except Exception as e:
            logging.error(f"Ошибка в скрипте: {str(e)}")
            self.stop_script()
        finally:
            self.stop_script()

    def stop_script(self):
        self.running = False
        if self.driver:
            self.driver.quit()  # Закрытие драйвера
        #if self.thread:
        #    self.thread.stop()
        self.start_button.config(state="normal", text="Start")
        self.stop_button.config(state="disabled", text="Stop")

        #if self.progress_window and self.progress_window.winfo_exists():
        #    self.progress_window.destroy()
        logging.info("Скрипт остановлен.")
