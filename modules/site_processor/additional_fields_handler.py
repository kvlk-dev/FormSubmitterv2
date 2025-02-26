import random
import time
import logging
from selenium.webdriver.common.by import By

from modules.site_processor import phone_processor


def run(driver, form, data):
    """Обработка select, radio, checkbox, текстовых и числовых полей (только обязательных)"""
    try:
        # Обработка select
        select_fields = form.find_elements(By.TAG_NAME, 'select')
        for select in select_fields:
            try:
                options = select.find_elements(By.TAG_NAME, 'option')
                if options:
                    select.click()
                    time.sleep(random.uniform(0.3, 0.7))
                    random.choice(options).click()
            except Exception:
                continue



        # Обработка radio
        radio_buttons = form.find_elements(By.XPATH, ".//input[@type='radio']")
        if radio_buttons:
            random.choice(radio_buttons).click()

        # Обработка checkbox
        checkboxes = form.find_elements(By.XPATH, ".//input[@type='checkbox']")
        for checkbox in checkboxes:
            try:
                if random.choice([True, False]):
                    checkbox.click()
            except Exception:
                continue

        # Локальная функция для определения обязательности поля
        def is_field_required(input_field):
            """Проверяет, обязательно ли поле для заполнения"""
            if input_field.get_attribute("required") is not None:
                return True
            input_id = input_field.get_attribute("id")
            if input_id:
                try:
                    label = input_field.find_element(By.XPATH, f"//label[@for='{input_id}']")
                    if label.text.strip().endswith("*"):
                        return True
                except Exception:
                    pass
            return False

        # Обработка текстовых полей (input type="text")
        text_inputs = form.find_elements(By.XPATH, ".//input[@type='text']")
        for input_field in text_inputs:
            if is_field_required(input_field) and input_field.get_attribute('value') == '':
                try:
                    input_field.clear()
                    input_field.send_keys("soon")
                except Exception:
                    continue

        # Обработка числовых полей (input type="number") только если обязательные
        number_inputs = form.find_elements(By.XPATH, ".//input[@type='number']")
        for number_input in number_inputs:
            if is_field_required(number_input) and number_input.get_attribute('value') == '':
                try:
                    number_input.clear()
                    if number_input.get_attribute('min') or number_input.get_attribute('max'):
                        min = (int(number_input.get_attribute('min')) if number_input.get_attribute('min') else 0)
                        max = (int(number_input.get_attribute('max')) if number_input.get_attribute('max') else 100)
                        number_input.send_keys(
                            str(random.randint(min, max))
                        )
                    else:
                        number_input.send_keys("11111")
                except Exception:
                    continue
        tel_inputs = form.find_elements(By.XPATH, ".//input[@type='tel']")
        for tel_input in tel_inputs:
            if is_field_required(tel_input) and tel_input.get_attribute('value') == '':
                try:
                    tel_input.clear()
                    tel_input.send_keys(phone_processor.run(driver,data['phone']))
                except Exception:
                    continue

    except Exception as e:
        logging.warning(f"Additional fields error: {str(e)}")
