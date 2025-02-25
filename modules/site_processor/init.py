import logging
import random
import time

from selenium.webdriver.support import expected_conditions as EC

import requests
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from modules.site_processor import site_availability, contact_link_finder, form_finder


class SiteProcessor:
    def __init__(self):
        self.running = False
        self.driver = None

    def init(self, url):
        """Обработка одного сайта с классификацией ошибок"""
        try:
            # Попытка открыть сайт
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
        except WebDriverException as e:
            error_message = str(e).lower()
            if "ssl" in error_message or "cert" in error_message:
                return "Error", "Ошибка SSL"
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка загрузки сайта: {str(e)}")
            return "Error", "Сайт недоступен"
        except Exception as e:
            logging.error(f"Ошибка загрузки сайта: {str(e)}")
            return "Error", "Сайт недоступен"

        if "The Chromium Authors" in self.driver.page_source or "Mozilla Public - License" in self.driver.page_source:
            return "Error", "Сайт недоступен"

        if "You have been blocked" in self.driver.page_source:
            return "Error", "Cloudflare"
        site_available = site_availability.run(self.driver)

        if not site_available:
            return "Error", "Сайт недоступен"
        if not self.running:
            return "Stopped", ""

        try:
            # Закрытие попапов
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close']"))
                ).click()
            except Exception:
                pass

            contact_link = contact_link_finder.run(self.driver)
            if contact_link:
                self.driver.get(contact_link)
                time.sleep(random.uniform(0.5, 1.5))
                logging.info(f"Найдена контактная ссылка: {contact_link}")

            form = form_finder.run(self.driver)
            if not form:
                return "Error", "Форма не найдена"

            fill_form = form_filler.run(self.driver, form)

            # Поиск основной формы
            #    try:
            #        form = WebDriverWait(self.driver, 25).until(
            #            EC.presence_of_element_located((By.XPATH, "//form//input[@type='submit'] | //form//button[@type='submit']"))
            #        )
            #    except Exception:
            #        return "Error","Форма не найдена"
            fill_result, form = self.fill_form(self.driver)

            # Заполнение формы
            if not fill_result:
                return "Error", "Ошибка заполнения формы"

            # Обработка CAPTCHA, если есть
            if self.driver.find_elements(By.ID, "g-recaptcha-response") or self.driver.find_elements(By.CLASS_NAME,
                                                                                                     "g-recaptcha"):
                if not self.solve_recaptcha(self.driver):
                    return "Error", "Ошибка CAPTCHA"

            return self.submit_form(self.driver, form)  # Сохраняем результаты submit_form
            #
            # if status != True:  # Проверяем статус. Если не True, значит ошибка.
            #     return status, None
            # else:
            #     return "Error","Ошибка отправки формы"
            #

        except Exception as e:
            logging.error(f"Общая ошибка: {str(e)}")
            return "Error", "Ошибка элемента"
