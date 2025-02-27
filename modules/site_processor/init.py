import logging
import random
import time

from selenium.webdriver.support import expected_conditions as EC

import requests
from selenium.common import WebDriverException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from modules.site_processor import site_availability, contact_link_finder, form_finder, form_filler, phone_processor
from modules.site_processor.captcha_solver import CaptchaSolver
from modules.site_processor.submit_form import SubmitForm


class SiteProcessor:
    def __init__(self, driver):
        self.running = True
        self.driver = driver
        self.phone = None

    def init(self, url, data):
        """Обработка одного сайта с классификацией ошибок"""
        site_available = site_availability.check_http_status(url)
        if not site_available:
            return "Error", "Сайт недоступен"
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

        site_available = site_availability.run(self.driver)

        if not site_available:
            return "Error", "Сайт недоступен"
        if not self.running:
            return "Stopped", ""

        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close']"))
            ).click()
        except Exception:
            pass
        #
        # if "contact" not in self.driver.current_url:
        #     contact_link = contact_link_finder.run(self.driver)
        #     if contact_link:
        #         self.driver.get(contact_link)
        #         time.sleep(random.uniform(0.5, 1.5))
        #         logging.info(f"Найдена контактная ссылка: {contact_link}")
        form = None
        try:
            form = form_finder.run(self.driver)
        except Exception as e:
            logging.error(f"Ошибка при поиске формы: {str(e)}")
            pass
        if not form and "contact" not in self.driver.current_url:
            contact_link = None
            try:
                contact_link = contact_link_finder.run(self.driver)
            except Exception as e:
                logging.error(f"Ошибка при поиске контактной ссылки: {str(e)}")
                pass
            if contact_link:
                self.driver.get(contact_link)
                time.sleep(random.uniform(0.5, 1.5))
                logging.info(f"Найдена контактная ссылка: {contact_link}")
                try:
                    form = form_finder.run(self.driver)
                except Exception as e:
                    logging.error(f"Ошибка при поиске формы: {str(e)}")
                    pass
        if not form:
            return "Error", "Форма не найдена"

        self.phone = data['form_data']['phone'] = phone_processor.run(self.driver, self.phone)

        try:
            fill_result, form = form_filler.run(self.driver, form, data['form_data'])
        except Exception as e:
            logging.error(f"Ошибка при заполнении формы: {str(e)}")
            return "Error", "Ошибка заполнения формы"

        if not fill_result:
            return "Error", "Ошибка заполнения формы"

        # Обработка CAPTCHA, если есть
        if self.driver.find_elements(By.ID, "g-recaptcha-response") or self.driver.find_elements(By.CLASS_NAME,
                                                                                                 "g-recaptcha"):
            try:
                captcha_solver = CaptchaSolver(data['captcha_api_key'])
                if not captcha_solver.solve_recaptcha(self.driver):
                    return "Error", "Ошибка CAPTCHA"
            except Exception as e:
                logging.error(f"Ошибка при решении CAPTCHA: {str(e)}")
                return "Error", "Ошибка CAPTCHA"

        try:
            submit_form = SubmitForm(self.driver, form, data['form_data'])
            status, reason = submit_form.run()
            return status, reason
        except (NoSuchElementException, StaleElementReferenceException) as e:
            # Если элемент исчез, значит форма отправлена
            if "stale element not found" in str(e).lower():
                return "Success", None
        except Exception as e:
            if "stale element not found" in str(e).lower():
                return "Success", None
            logging.error(f"Ошибка при отправке формы: {str(e)}")
            return "Error", "Ошибка отправки формы"
