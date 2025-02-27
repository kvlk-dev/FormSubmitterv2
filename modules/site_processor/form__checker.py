import logging

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select


class FormChecker:
    def __init__(self, driver, form_element, timeout=15):
        self.driver = driver
        self.form = form_element
        self.timeout = timeout
    def is_form_successful(self):
        """Основной метод проверки успешности отправки формы"""
        try:
            # Ожидаем изменения состояния формы
            WebDriverWait(self.driver, self.timeout).until(
                EC.staleness_of(self.form)
            )
            return True

        except TimeoutException:
            try:
                # Проверка состояния формы
                return self._check_success_conditions()
            except (StaleElementReferenceException, NoSuchElementException):
                return False

    def _form_state_changed(self, driver):
        """Проверка изменения состояния формы"""
        return self._is_form_removed() or self._is_form_hidden()

    def _check_success_conditions(self):
        """Проверка условий успешной отправки"""
        if self._is_form_removed():
            logging.info("Форма удалена из DOM")
            return True

        return self._is_form_hidden() and self._are_fields_cleared()

    def _is_form_removed(self):
        """Проверка полного удаления формы из DOM"""
        try:
            WebDriverWait(self.driver, 15).until(EC.staleness_of(self.form))
            return True
        except TimeoutException:
            try:
                # Проверка существования элемента в DOM
                self.form.is_enabled()
                return False
            except (StaleElementReferenceException, NoSuchElementException):
                return True

    def _is_form_hidden(self):
        """Проверка видимости формы"""
        try:
            displayed = self.form.is_displayed()
            return not displayed
        except (StaleElementReferenceException, NoSuchElementException):
            return True

    def _are_fields_cleared(self):
        """Проверка очистки заполняемых полей"""
        try:
            # Не проверяем поля если форма удалена
            if self._is_form_removed():
                logging.info("Форма удалена из DOM")
                return True

            fields = self.form.find_elements(By.XPATH,
                                             ".//*[self::input[not(@type='hidden' or @type='submit')] | "
                                             "self::textarea | "
                                             "self::select]"
                                             )

            for field in fields:
                if self._is_field_filled(field):
                    return False
            return True

        except (StaleElementReferenceException, NoSuchElementException):
            return False

    def _is_field_filled(self, field):
        """Проверка заполненности отдельного поля"""
        tag_name = field.tag_name.lower()

        # Для select элементов
        if tag_name == 'select':
            select = Select(field)
            return select.first_selected_option.get_attribute('value') != ''

        # Для input/textarea
        value = field.get_attribute('value') or field.text.strip()
        return bool(value)