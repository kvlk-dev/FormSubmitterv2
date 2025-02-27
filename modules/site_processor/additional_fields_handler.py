import random
import time
import logging
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import WebDriverException, TimeoutException

from modules.site_processor import phone_processor


def run(driver, form, data):
    """Обработка полей с использованием ActionChains"""
    try:
        actions = ActionChains(driver)

        def human_click(element):
            """Имитирует человеческий клик"""
            try:
                actions.reset_actions()
                driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", element)
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(element))
                actions.move_to_element(element).pause(random.uniform(0.1, 0.3)).click().perform()
            except Exception:
                element.click()

        def human_type(element, text):
            """Имитирует человеческий ввод текста"""
            try:
                actions.reset_actions()
                driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", element)
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(element))

                # Очистка поля
                actions.move_to_element(element).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
                actions.send_keys(Keys.BACKSPACE)
                # Переход в начало строки нажатием клавиши Home
                actions.move_to_element(element).click().key_down(Keys.HOME).perform()
                # Ввод текста
                actions.send_keys_to_element(element, text)
                actions.pause(random.uniform(0.05, 0.2))
                actions.perform()
            except Exception as e:
                element.clear()
                element.send_keys(text)

        # Обработка select с улучшенной имитацией
        select_fields = form.find_elements(By.TAG_NAME, 'select')
        for select in select_fields:
            try:
                human_click(select)
                options = select.find_elements(By.TAG_NAME, 'option')
                if len(options) > 1:
                    option = options[random.randint(1, len(options) - 1)]
                    human_click(option)
                else:
                    human_click(options[0])
                time.sleep(0.3)
            except Exception:
                continue

        # Обработка radio с паузами
        radio_buttons = form.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        if radio_buttons:
            human_click(random.choice(radio_buttons))

        # Чекбоксы с рандомным выбором
        checkboxes = form.find_elements(By.XPATH, ".//input[@type='checkbox']")
        for checkbox in checkboxes:
            try:
                if random.choice([True, False]):
                    human_click(checkbox)
                    time.sleep(random.uniform(0.1, 0.4))
            except Exception:
                continue

        # Обработка текстовых полей
        text_inputs = form.find_elements(By.CSS_SELECTOR,
                                         "input[type='text'], input[type='email'], input[type='tel']")
        for input_field in text_inputs:
            if input_field.get_attribute('value') == '':
                try:
                    human_type(input_field, "soon")
                except Exception:
                    continue

        # Числовые поля с улучшенным вводом
        number_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='number']")
        for number_input in number_inputs:
            if number_input.get_attribute('value') == '':
                try:
                    value = "11111"
                    if number_input.get_attribute('min') or number_input.get_attribute('max'):
                        min_val = int(number_input.get_attribute('min')) if number_input.get_attribute('min') else 0
                        max_val = int(number_input.get_attribute('max')) if number_input.get_attribute('max') else 100
                        value = str(random.randint(min_val, max_val))
                    human_type(number_input, value)
                except Exception:
                    continue

        # Телефонные поля с расширенной обработкой
        tel_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='tel']")
        for tel_input in tel_inputs:
            if tel_input.get_attribute('value') == '':
                try:
                    phone = phone_processor.run(driver, data['phone'])
                    human_type(tel_input, phone)
                except Exception:
                    continue

    except Exception as e:
        logging.warning(f"Additional fields error: {str(e)}")