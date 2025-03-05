import logging
import random
from argparse import Action

from selenium.common import ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback

from modules.site_processor.errors_detector import ErrorsDetector
from modules.site_processor.form_checker import FormChecker


class SubmitForm:
    def __init__(self, driver, form, data):
        self.driver = driver
        self.data = data
        self.form = form
        self.initial_phone = data['phone']

    def run(self):
        """Поиск и нажатие на кнопку отправки с улучшенной обработкой ошибок и
        попытками исправления для англоязычных контактных форм."""
        submitted = False
        form_checker = FormChecker(self.driver, self.form)
        try:
            logging.info("Нажимаем Enter и отправляем")
            inputs = self.form.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], input[type="tel"], textarea')
            actions = ActionChains(self.driver)
            for input in inputs:
                try:
                    if input.is_displayed() and input.is_enabled():
                        logging.info(f"Пробуем отправить форму, нажав Enter на поле {input.get_attribute('id') or input.get_attribute('name') or input.get_attribute('class')}")
                        actions.move_to_element(input).click().send_keys(Keys.ENTER).perform()
                        actions.reset_actions()
                        time.sleep(random.uniform(0.5, 1.5))
                        break
                except ElementNotInteractableException:
                    logging.error(f"Поле {input.get_attribute('id')} не доступно для ввода, пробуем следующее")
                    pass
                except Exception as e:
                    logging.error(f"Ошибка при нажатии Enter: {str(e)}")
                    pass
            time.sleep(random.uniform(3, 5))
            try:
                if form_checker.is_form_successful():
                    return "Success", None
                else:
                    return "Error", "Ошибка при отправке формы"
            except Exception as e:
                logging.error(f"Ошибка при проверке успешности отправки формы: {str(e)}")
                logging.error(traceback.format_exc())
                return "Error", "Ошибка при отправке формы"
            #     errors_detector = ErrorsDetector(self.driver, self.form, self.data)
            #     status = errors_detector.run()
            #     if status:
            #         return "Success", None
            #     else:
            #         return "Error", "Ошибка при отправке формы"
        except Exception as e:
            logging.error(f"Ошибка при отправке формы: {str(e)}")
            logging.error(traceback.format_exc())
            return "Error", "Ошибка при отправке формы"
            pass
        # try:
        #     self.form.submit()
        #     time.sleep(random.uniform(3, 5))
        #     if form_checker.is_form_successful():
        #         submitted = True
        # except Exception as e:
        #     logging.error(f"Ошибка при отправке формы: {str(e)}")
        #     submitted = False
        #     try:
        #         self.driver.execute_script("arguments[0].querySelector('button').click();", self.form)
        #         time.sleep(random.uniform(3, 5))
        #         if form_checker.is_form_successful():
        #             submitted = True
        #     except Exception as e:
        #         logging.error(f"Ошибка при отправке формы: {str(e)}")
        #         logging.error(traceback.format_exc())
        #         submitted = False
        #         pass
        #
        # if submitted:
        #     return "Success", None
        # try:
        #     # ищем form input[type="submit"] или button[type="submit"] внутри self.form
        #     submit_button = self.form.find_element(By.CSS_SELECTOR, "input[type='submit'], button")
        #     WebDriverWait(self.driver, 20).until(
        #         EC.presence_of_element_located(submit_button)
        #     )
        #     self.driver.execute_script("window.scrollTo(0, arguments[0].getBoundingClientRect().top)", submit_button)
        #     try:
        #         submit_button.click()
        #     except Exception as e:
        #         logging.error(f"Ошибка при клике на кнопку отправки: {str(e)}")
        #         try:
        #             self.driver.execute_script("arguments[0].click();", submit_button)
        #         except Exception as e:
        #             logging.error(f"Ошибка при клике на кнопку отправки: {str(e)}")
        #             pass
        #     time.sleep(random.uniform(3, 5))
        #     if form_checker.is_form_successful():
        #         submitted = True
        # except TimeoutException:
        #     logging.error(f"Не удалось отправить форму (timeout): возможно, проблема с сайтом.")
        #     pass
        #     #return "Error", "Timeout при отправке формы"
        #
        # if submitted:
        #     return "Success", None
        #
        # try:
        #     # Уточняем локаторы кнопки отправки, добавляем специфические для
        #     # контактных форм варианты
        #     submit_button = WebDriverWait(self.driver, 20).until(
        #         EC.element_to_be_clickable((
        #             By.XPATH,
        #             "//input[@type='submit'] | //button[@type='submit'] | "
        #             "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
        #             "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')] | "
        #             "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')] | "
        #             "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')] | "
        #             "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')] | "
        #             "//*[contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
        #             "//*[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]"
        #         # Общие варианты
        #         ))
        #     )
        #     if not submit_button:
        #
        #         xpath_submit_button = (
        #             "//input[@type='submit'] | //button[@type='submit'] | "
        #             "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]] | "
        #             "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')]] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')] | "
        #             "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')]] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')] | "
        #             "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')]] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')] | "
        #             "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')]] | "
        #             "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')] | "
        #             "//*[contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
        #             "//*[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]"
        #         )
        #         submit_button = WebDriverWait(self.driver, 20).until(
        #             EC.element_to_be_clickable((By.XPATH, xpath_submit_button))
        #         )
        #
        #     if submit_button:
        #         submit_button.click()
        #         time.sleep(random.uniform(3, 5))
        #         if form_checker.is_form_successful():
        #             return "Success", None
        #     else:
        #         return "Error","Ошибка отправки формы"
        except TimeoutException:
            return "Error", "Timeout при отправке формы"