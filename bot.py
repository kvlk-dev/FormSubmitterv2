import subprocess
import sys
import time
import random
import threading
import logging
from datetime import datetime
import os
import re
from urllib.parse import urlparse

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from dotenv import load_dotenv
from oauth2client.transport import request
from twocaptcha import TwoCaptcha
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import modules.config as config
from modules.get_sites import get_sites
from modules.google_service import GoogleService
from modules.site_runner import site_runner


class FormSubmitter:
    def __init__(self):
        self.browser = None
        self.running = False
        self.ua = UserAgent()
        self.proxy = None
        self.captcha = None
        self.sheet = None
        self.drive = None
        self.worksheet = None
        self.captcha_api_key = None
        self.captcha_api = None
        self.captcha_api = TwoCaptcha(self.captcha_api_key)
        self.config = config.init()
        self.google_service = GoogleService(self.config)

    def update_config(self, new_config):
        """Обновление конфига с мерджем словарей"""
        config.update_config(new_config)

    def site_run(self, idx, url, total):
        return site_runner(self.browser, idx, url, total, self.sheet)

    def run_script(self):
        self.browser = self.config.get('browser', 'chrome').lower()
        self.running = True

        self.sheet = self.google_service.init()
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("screenshots/success", exist_ok=True)
        os.makedirs("screenshots/errors", exist_ok=True)
        profile_name = self.config.get("profile_name", "default")

        sites = get_sites.run()
        if not sites:
            logging.error("No sites found in spreadsheet")
            return

        for idx, url in sites:
            if not self.running:
                logging.info("Процесс остановлен пользователем.")
                break
            total = len(sites)
            self.site_run(idx, url, total)

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
