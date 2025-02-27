import datetime
import random
import time
from datetime import datetime, timedelta
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import re
from typing import List, Optional, Dict, Union


class ErrorsDetector:
    def __init__(self, driver, form_element, data: Dict[str, str], timeout: int = 15):
        self.driver = driver
        self.form = form_element
        self.timeout = timeout
        self.data = self._process_input_data(data)
        self.logger = logging.getLogger(__name__)
        self.actions = ActionChains(driver)
        self.wait = WebDriverWait(driver, timeout)

        self.error_patterns = {
            'required': re.compile(
                r'\b(required|mandatory|obligatory|поле обязательно|обязательное)\b',
                re.I | re.U
            ),
            'invalid': re.compile(
                r'\b(invalid|incorrect|неверно|неправильный|формат)\b',
                re.I | re.U
            ),
            'length': re.compile(
                r'\b(length|длина|символ|characters|минимальная|максимальная)\b',
                re.I | re.U
            ),
            'unique': re.compile(
                r'\b(unique|already exists|уже существует|повтор|занят)\b',
                re.I | re.U
            ),
            'server': re.compile(
                r'\b(error|server|ошибка|problem|issue)\b',
                re.I | re.U
            )
        }

    def _process_input_data(self, data: Dict) -> Dict:
        """Нормализация входных данных"""
        processed = {}
        for key, value in data.items():
            if isinstance(value, str):
                processed[key] = value.strip()
            else:
                processed[key] = str(value).strip()
        return processed

    def run(self) -> bool:
        """Основной workflow обработки ошибок"""
        try:
            errors = self._wait_for_errors()
            if not errors:
                return True

            self.logger.info(f"Найдено ошибок: {len(errors)}, начинаем исправление...")
            return self._process_errors(errors)

        except Exception as e:
            self.logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
            return False

    def _wait_for_errors(self) -> List[WebElement]:
        """Ожидание появления ошибок с таймаутом"""
        error_locators = [
            (By.CSS_SELECTOR, "[class*='error'], [class*='invalid']"),
            (By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'ошибка')]"),
            (By.CSS_SELECTOR, "[aria-invalid='true'], [role='alert']")
        ]

        errors = []
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            for locator in error_locators:
                try:
                    elements = self.driver.find_elements(*locator)
                    visible_errors = [el for el in elements if el.is_displayed()]
                    errors.extend(visible_errors)
                except:
                    continue

            if errors:
                return list(set(errors))  # Убираем дубликаты

            time.sleep(0.5)

        return []

    def _process_errors(self, errors: List[WebElement]) -> bool:
        """Обработка списка ошибок"""
        success = True
        for error in errors:
            try:
                if not self._handle_single_error(error):
                    success = False
            except Exception as e:
                self.logger.warning(f"Ошибка обработки элемента: {str(e)}")
                success = False
        return success

    def _handle_single_error(self, error_element: WebElement) -> bool:
        """Обработка одной ошибки"""
        field = self._find_related_field(error_element)
        error_type = self._classify_error(error_element)

        if not field:
            self.logger.warning(f"Не удалось найти связанное поле для ошибки: {error_element.text}")
            return False

        self.logger.debug(f"Обработка {error_type} ошибки для поля {field.get_attribute('name')}")

        fix_strategies = {
            'required': self._fix_required_field,
            'invalid': self._fix_invalid_format,
            'length': self._fix_length_issue,
            'unique': self._fix_unique_value,
            'server': self._handle_server_error
        }

        strategy = fix_strategies.get(error_type, self._generic_fix)
        return strategy(field, error_element)

    def _find_related_field(self, error_element: WebElement) -> Optional[WebElement]:
        """Поиск связанного поля с использованием многоуровневого подхода"""
        # Уровень 1: Поиск через ARIA-атрибуты
        if field := self._find_by_aria(error_element):
            return field

        # Уровень 2: Поиск в DOM-структуре
        if field := self._find_in_dom(error_element):
            return field

        # Уровень 3: Поиск по тексту и лейблам
        return self._find_by_text_context(error_element)

    def _find_by_aria(self, error_element: WebElement) -> Optional[WebElement]:
        """Поиск через ARIA-атрибуты"""
        try:
            error_id = error_element.get_attribute('id')
            if error_id:
                return self.form.find_element(
                    By.CSS_SELECTOR, f"[aria-describedby~='{error_id}'], [aria-errormessage='{error_id}']"
                )
        except:
            return None

    def _find_in_dom(self, error_element: WebElement) -> Optional[WebElement]:
        """Поиск в DOM-структуре"""
        locators = [
            ("preceding-sibling::*[self::input or self::select or self::textarea]", "xpath"),
            ("following-sibling::*[self::input or self::select or self::textarea]", "xpath"),
            (".//ancestor::div[contains(@class, 'form-group')]//input", "xpath"),
            ("input, select, textarea", "css")
        ]

        for locator, by in locators:
            try:
                return error_element.find_element(by, locator)
            except:
                continue
        return None

    def _find_by_text_context(self, error_element: WebElement) -> Optional[WebElement]:
        """Поиск по контексту текста ошибки"""
        error_text = error_element.text.lower()
        candidates = []

        for field in self.form.find_elements(By.CSS_SELECTOR, "input, select, textarea"):
            label_text = self._get_field_label_text(field).lower()
            if self._calculate_text_similarity(error_text, label_text) > 0.3:
                candidates.append(field)

        return candidates[0] if candidates else None

    def _classify_error(self, error_element: WebElement) -> str:
        """Классификация ошибки с использованием комбинированного подхода"""
        error_text = error_element.text.lower()

        # Анализ по ключевым словам
        for error_type, pattern in self.error_patterns.items():
            if pattern.search(error_text):
                return error_type

        # Анализ визуальных характеристик
        classes = error_element.get_attribute('class').lower()
        if 'required' in classes:
            return 'required'
        if 'server' in classes:
            return 'server'

        return 'unknown'

    def _fix_required_field(self, field: WebElement, *_) -> bool:
        """Исправление обязательных полей"""
        current_value = self._get_field_value(field)
        if not current_value or current_value.isspace():
            new_value = self._generate_field_value(field)
            return self._safe_input(field, new_value)
        return True

    def _get_field_value(self, field: WebElement) -> str:
        """Получение значения поля"""
        if field.tag_name.lower() == 'select':
            return field.find_element(By.CSS_SELECTOR, 'option:checked').text
        return field.get_attribute('value')

    def _generate_field_value(self, field: WebElement) -> Union[str, int, float]:
        """Генерация значения для поля"""
        field_type = field.get_attribute('type').lower()
        field_name = field.get_attribute('name').lower()

        generators = {
            'email': lambda: self.data.get('email', 'test@example.com'),
            'tel': lambda: self._format_phone_number(),
            'number': lambda: random.randint(1, 100),
            'date': lambda: (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'password': lambda: f"Passw0rd!{random.randint(10,99)}"
        }

        if 'zip' in field_name:
            return random.randint(10000, 99999)
        if 'name' in field_name:
            return f"TestUser{random.randint(1, 100)}"

        return generators.get(field_type, lambda: "TestValue123")()

    def _fix_invalid_format(self, field: WebElement, error_element: WebElement) -> bool:
        """Исправление формата данных"""
        error_text = error_element.text.lower()
        current_value = self._get_field_value(field)

        if 'email' in error_text or field.get_attribute('type') == 'email':
            return self._safe_input(field, self.data.get('email', 'test@example.com'))

        if 'phone' in error_text or field.get_attribute('type') == 'tel':
            return self._safe_input(field, self._format_phone_number())

        return self._safe_input(field, self._generate_smart_value(field))

    def _format_phone_number(self) -> str:
        """Форматирование телефонного номера"""
        phone = self.data.get('phone', '')
        return re.sub(r'\D', '', phone)[-10:]

    def _generate_smart_value(self, field: WebElement) -> Union[str, int, float]:
        """Генерация значений с учётом типа поля"""
        return self._generate_field_value(field)

    def _safe_input(self, field: WebElement, value: Union[str, int, float]) -> bool:
        """Безопасный ввод данных с проверкой"""
        try:
            self.actions.move_to_element(field).click().pause(0.5)
            field.send_keys(Keys.CONTROL + "a")
            field.send_keys(Keys.DELETE)
            field.send_keys(str(value))
            self.actions.pause(0.5).perform()

            return self.wait.until(
                lambda d: field.get_attribute('value') == str(value)
            )
        except Exception as e:
            self.logger.error(f"Ошибка ввода данных: {str(e)}")
            return False

    def _fix_length_issue(self, field: WebElement, *_) -> bool:
        """Исправление проблемы с длиной"""
        current_value = self._get_field_value(field)
        min_length = int(field.get_attribute('minlength') or 0)
        max_length = int(field.get_attribute('maxlength') or 50)

        if len(current_value) < min_length:
            new_value = current_value.ljust(min_length, 'x')
            return self._safe_input(field, new_value)
        elif len(current_value) > max_length:
            new_value = current_value[:max_length]
            return self._safe_input(field, new_value)
        return True

    def _fix_unique_value(self, field: WebElement, *_) -> bool:
        """Исправление проблемы уникальности"""
        new_value = self._generate_unique_value(field)
        return self._safe_input(field, new_value)

    def _generate_unique_value(self, field: WebElement) -> str:
        """Генерация уникального значения"""
        base_value = self._generate_field_value(field)
        return f"{base_value}{random.randint(1000,9999)}"

    def _handle_server_error(self, *_) -> bool:
        """Обработка серверных ошибок"""
        self.logger.warning("Обнаружена серверная ошибка, повторная попытка...")
        time.sleep(random.uniform(2, 5))
        return self._retry_submission()

    def _retry_submission(self) -> bool:
        """Повторная отправка формы"""
        try:
            submit_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            ))
            submit_button.click()
            return True
        except:
            return False

    def _generic_fix(self, field: WebElement, *_) -> bool:
        """Общая стратегия исправления"""
        new_value = self._generate_field_value(field)
        return self._safe_input(field, new_value)

    def _get_field_label_text(self, field: WebElement) -> str:
        """Получение текста лейбла поля"""
        if field.get_attribute('aria-label'):
            return field.get_attribute('aria-label')
        try:
            label = self.driver.find_element(
                By.CSS_SELECTOR, f"label[for='{field.get_attribute('id')}']"
            )
            return label.text
        except:
            return ''

    @staticmethod
    def _calculate_text_similarity(text1: str, text2: str) -> float:
        """Вычисление схожести текстов"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        common = words1 & words2
        return len(common) / (len(words1 | words2) + 1e-9)