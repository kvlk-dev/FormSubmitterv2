import logging
import random
import re
import phone_processor

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
class SubmitForm:
    def __init__(self, driver, form, data):
        self.driver = driver
        self.data = data
        self.form = form
        self.initial_phone = data['phone']



    def is_form_successful(self):
        # Ключевые слова для проверки URL
        success_keywords = ["success", "thank", "confirm", "done", "completed", "submitted", "finished"]

        # Проверка URL
        if any(keyword in self.driver.current_url for keyword in success_keywords):
            return True

        # Проверка исчезновения формы
        try:
            WebDriverWait(self.driver, 10).until_not(
                EC.invisibility_of_element(self.form)
            )
            return True
        except TimeoutException:
            pass

        # 1. Проверка успешной отправки
        try:
            success_message = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'thanks') or "
                    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'thank you') or "
                    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sent') or "
                    "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'success')]"
                ))
            )
            if success_message.is_displayed():
                return True
        except TimeoutException:
            pass  # Сообщение об успехе не найдено

        # Проверка появления сообщения об успехе
        try:
            success_message = self.driver.find_element(By.CSS_SELECTOR, ".success-message")
            if success_message.is_displayed():
                return True
        except:
            pass

        return False

    def submit_form(self):
        """Поиск и нажатие на кнопку отправки с улучшенной обработкой ошибок и
        попытками исправления для англоязычных контактных форм."""
        try:
            # Уточняем локаторы кнопки отправки, добавляем специфические для
            # контактных форм варианты
            submit_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//input[@type='submit'] | //button[@type='submit'] | "
                    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
                    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')] | "
                    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')] | "
                    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')] | "
                    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')] | "
                    "//*[contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
                    "//*[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]"
                # Общие варианты
                ))
            )
            if not submit_button:

                xpath_submit_button = (
                    "//input[@type='submit'] | //button[@type='submit'] | "
                    "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]] | "
                    "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')]] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')] | "
                    "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')]] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'contact')] | "
                    "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')]] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit message')] | "
                    "//button[.//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')]] | "
                    "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send message')] | "
                    "//*[contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')] | "
                    "//*[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]"
                )
                submit_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_submit_button))
                )

            if submit_button:
                submit_button.click()
                time.sleep(random.uniform(3, 5))
                if self.is_form_successful():
                    return "Success", None
            #    return "Success", None
            else:
                return "Error: Ошибка отправки формы", None, None

          #  driver.execute_script("arguments[0].click();", submit_button)
           # time.sleep(random.uniform(3, 5))
            #if "thank" in driver.page_source.lower() or "success" in driver.page_source.lower() or "sent" in driver.page_source.lower():
            #    return "Success", ""

            # 1. Поиск конкретных сообщений об ошибках (более приоритетно):
            # Расширяем список типичных ошибок для контактных форм
            error_messages = {
                "invalid email": [
                    "//div[contains(text(), 'email') and contains(., 'invalid')] | "
                    "//span[contains(text(), 'email') and contains(., 'invalid')] | "
                    "//*[contains(@class, 'email-error')] | //*[contains(@id, 'email-error')] | "
                    "//p[contains(., 'email') and contains(., 'incorrect')] | "
                    "//p[contains(., 'email') and contains(., 'wrong')] | "
                    "//p[contains(., 'email') and contains(., 'format')] | "
                    "//input[@type='email' and contains(@class, 'is-invalid')] | "
                    "//input[@type='email' and contains(@class, 'error')]"
                ],
                "required field": [
                    "//div[contains(text(), 'required')] | //span[contains(text(), 'required')] | "
                    "//*[contains(@class, 'required-error')] | //*[contains(@id, 'required-error')] | "
                    "//p[contains(., 'field') and contains(., 'required')] | "
                    "//p[contains(., 'field') and contains(., 'necessary')] | "
                    "//p[contains(., 'must be filled')] | "
                    "//input[contains(@class, 'is-invalid')] | //input[contains(@class, 'error')] | "
                    "//select[contains(@class, 'is-invalid')] | //select[contains(@class, 'error')] | "
                    "//textarea[contains(@class, 'is-invalid')] | //textarea[contains(@class, 'error')]"
                ],
                "invalid phone": [
                    "//div[contains(text(), 'phone')] | //span[contains(text(), 'phone')] | "
                    "//*[contains(@class, 'phone-error')] | //*[contains(@id, 'phone-error')] | "
                    "//p[contains(., 'phone') and contains(., 'invalid')] | "
                    "//p[contains(., 'phone') and contains(., 'incorrect')] | "
                    "//p[contains(., 'phone') and contains(., 'format')] | "
                    "//input[@type='tel' and contains(@class, 'is-invalid')] | "

                    "//input[@type='tel' and contains(@class, 'error')]"
                ],
                "incorrect format": [  # Общий случай для неверного формата
                    "//*[contains(text(), 'invalid')] | //*[contains(text(), 'incorrect')] | "
                    "//*[contains(text(), 'format')] | //*[contains(text(), 'wrong')] | "
                    "//input[contains(@class, 'is-invalid')] | //input[contains(@class, 'error')] | "
                    "//select[contains(@class, 'is-invalid')] | //select[contains(@class, 'error')] | "
                    "//textarea[contains(@class, 'is-invalid')] | //textarea[contains(@class, 'error')]"
                ],
                # Добавляем специфические ошибки для контактных форм
                "spam detected": [  # Пример: обнаружен спам
                    "//*[contains(text(), 'spam')] | //*[contains(text(), 'bot')] | "
                    "//*[contains(text(), 'suspicious activity')] | //*[contains(text(), 'blocked')]"
                ],
                "message too short": [  # Пример: слишком короткое сообщение
                    "//*[contains(text(), 'short')] | //*[contains(text(), 'too short')] | "
                    "//*[contains(text(), 'characters')] | //*[contains(text(), 'minimum')] | "
                    "//*[contains(text(), 'length')] | //*[contains(text(), 'at least')]"
                ],
                "message too long": [  # Пример: слишком длинное сообщение
                    "//*[contains(text(), 'long')] | //*[contains(text(), 'too long')] | "
                    "//*[contains(text(), 'characters')] | //*[contains(text(), 'maximum')] | "
                    "//*[contains(text(), 'limit')] | //*[contains(text(), 'exceed')] "
                ],
                # ... другие специфические ошибки для контактных форм
            }

            for error_text, locators in error_messages.items():
                for locator in locators:
                    try:
                        error_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, locator))
                        )
                        error_message = error_element.text
                        if error_text.lower() in error_message.lower():
                            logging.error(f"Ошибка отправки формы: {error_message}")

                            # Попытка исправить ошибку (только для определенных типов)
                            if error_text in ["invalid email", "required field", "invalid phone", "incorrect format"]:
                                if self.try_fix_error(error_text):  # Вызываем функцию исправления
                                    logging.info(f"Ошибка '{error_text}' исправлена. Повторная отправка...")
                                    submit_button.click()  # Повторно кликаем по кнопке
                                    time.sleep(random.uniform(3, 5))  # Ждем
                                    return self.submit_form()  # Рекурсивно вызываем submit_form, чтобы проверить,
                                    # что ошибка исправлена.
                                else:
                                    logging.warning(f"Не удалось исправить ошибку '{error_text}'.")
                                    return f"Error",error_message
                            else:
                                return f"Error",error_message
                    except TimeoutException:
                        pass
                    except Exception as e:
                        logging.error(f"Ошибка при поиске ошибки: {e}")
                        pass

            if self.is_form_successful():
                return "Success", ""

            # 2. Общий поиск ошибок (менее приоритетно, если конкретные не найдены):
            try:
                general_error_element = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'error') or contains(@class, 'error') or contains(@id, 'error')]"))
                )
                general_error_message = general_error_element.text
                if general_error_message and len(general_error_message) < 5:
                    return "Success", ""  # Возможно, это не ошибка, а просто текст

                logging.error(f"Общая ошибка отправки формы: {general_error_message}")
                return f"Error",general_error_message
            except TimeoutException:
                pass  # Общая ошибка не найдена
            except Exception as e:
                logging.error(f"Ошибка при поиске общей ошибки: {e}")
                pass

            # 3. Успешная отправка (если ошибок не найдено):
            logging.info("Форма отправлена без ошибок")
            return "Success", ""

        except TimeoutException:  # Ошибка при клике на submit
            logging.error(f"Не удалось отправить форму (timeout): возможно, проблема с сайтом.")
            return "Error","Timeout при отправке формы"
        except Exception as e:  # Ошибка при поиске кнопки или отправке
            logging.error(f"Ошибка при отправке формы: {str(e)}")
            return f"Error", "Неизвестная ошибка"

    def try_fix_error(self, error_text):
        """Попытка исправить наиболее распространенные ошибки в форме."""
        try:
            if error_text == "invalid email":
                email_field = self.driver.find_element(By.XPATH, "//input[@type='email']")
                current_email = email_field.get_attribute("value")
                if "@" not in current_email:
                    email_field.clear()
                    email_field.send_keys(self.data['email'])  # Пробуем ещё раз
                else:
                    email_field.clear()
                    email_field.send_keys(self.data['email'])  # Пробуем ещё раз
                return True
            elif error_text == "required field":
                # Находим первое пустое обязательное поле и заполняем его
                required_fields = self.driver.find_elements(By.XPATH, "//input[@required and not(@value)] | //textarea[@required and not(text())] | //select[@required and not(option[@selected])]")  # Добавил проверку select и textarea
                if required_fields:
                    field = random.choice(required_fields)  # Заполняем случайное поле
                    field.send_keys("soon")  # Заполняем тестовыми данными. Можно улучшить, генерируя более реалистичные данные.
                    return True
            elif error_text == "invalid phone":
                phone_field = self.driver.find_element(By.XPATH, "//input[@type='tel']")
                phone = phone_field.get_attribute("value")
                cleaned_phone = re.sub(r'\D', '', phone)  # Оставляем только цифры
                if len(cleaned_phone) < 10:  # Пример: если номер слишком короткий
                    phone_field.clear()
                    phone = phone_processor.run(self.driver, self.initial_phone)  # Получаем номер с сайта
                    phone_field.send_keys(phone)  # Добавляем цифры
                return True
            elif error_text == "incorrect format":
                # Попытка очистить поле. Возможно, пользователь ввел что-то совсем не то.
                invalid_fields = self.driver.find_elements(By.XPATH, "//input[@class='is-invalid'] | //input[@class='error'] | //select[@class='is-invalid'] | //select[@class='error'] | //textarea[@class='is-invalid'] | //textarea[@class='error']")
                if invalid_fields:
                    field = random.choice(invalid_fields)
                    field.clear()
                    return True
            return False  # Не удалось определить, как исправить ошибку
        except Exception as e:
            logging.error(f"Ошибка при попытке исправления ошибки: {e}")
            return False

