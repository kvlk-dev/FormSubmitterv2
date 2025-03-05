import random
import time
import logging
import traceback
from xml.etree.ElementPath import xpath_tokenizer

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import any_of
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import WebDriverException, TimeoutException

from modules.site_processor import phone_processor


def run(driver, form, data,filled_elements):
    """Обработка полей с использованием ActionChains"""
    try:
        actions = ActionChains(driver)

        def human_click(element,click_on_label=False):

            """Имитирует человеческий клик"""
            try:
                actions.reset_actions()
                driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", element)
                if click_on_label:
                    element_id = element.get_attribute('id')
                    label = form.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                    actions.move_to_element(label).pause(random.uniform(0.1, 0.3)).click().perform()
                else:
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(element))
                    actions.move_to_element(element).pause(random.uniform(0.1, 0.3)).click().perform()
            except Exception:
                logging.error(f"Ошибка при клике на элемент {element.get_attribute('id') or element.get_attribute('name') or element.get_attribute('class')}")
                try:
                    if click_on_label:
                        label = form.find_element(By.CSS_SELECTOR, f"label[for='{element.get_attribute('id')}']")
                        driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", label)
                        label.click()
                    else:
                        element.click()
                except Exception:
                    pass

        def human_type(element, text):
            """Имитирует человеческий ввод текста"""
            global filled_elements
            if element in filled_elements:
                return
            try:
                actions.reset_actions()
                driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", element)
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(element))
                logging.info(f"Дополнительный ввод в поле {element.get_attribute('id') or element.get_attribute('name') or element.get_attribute('class')}")

                # Очистка поля
                logging.info(f"Очистка поля {element.get_attribute('id')}")
                element.clear()
                #actions.send_keys(Keys.BACKSPACE)
                # Переход в начало строки нажатием клавиши Home
                logging.info(f"Переход в начало строки")
                actions.move_to_element(element).click().key_down(Keys.HOME).perform()
                # Ввод текста
                actions.pause(random.uniform(0.1, 0.3))
                logging.info(f"Ввод значения {text} в поле {element.get_attribute('id') or element.get_attribute('name') or element.get_attribute('class')}")
                if element.get_attribute('type') == 'tel':
                    for digit in text:
                        actions.send_keys(digit)
                        actions.pause(random.uniform(0.05, 0.2))
                else:
                    actions.send_keys_to_element(element, text)
                actions.pause(random.uniform(0.05, 0.2))
                actions.perform()
            except Exception as e:
                element.clear()
                element.send_keys(text)
            filled_elements.append(element)

        # Обработка select с улучшенной имитацией
        select_fields = form.find_elements(By.TAG_NAME, 'select')
        for select in select_fields:
            try:
                select = Select(select)
                # choose random option
                options = select.options
                if len(options) > 1:
                    option = options[random.randint(1, len(options) - 1)]
                    select.select_by_visible_text(option.text)
                else:
                    select.select_by_index(0)
                time.sleep(0.3)
            except Exception:
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
                    human_click(checkbox,True)
                    time.sleep(random.uniform(0.1, 0.4))
            except Exception:
                continue

        # Обработка текстовых полей
        text_inputs = form.find_elements(By.TAG_NAME, 'input')
                                         #"input[type='text'], input[type='email'], input[type='tel']")
        text_inputs.extend(form.find_elements(By.XPATH, ".//input[not(@type='hidden')]"))
        text_inputs.extend(form.find_elements(By.CSS_SELECTOR, "input"))

        for input_field in text_inputs:
            if input_field.get_attribute('type') == 'hidden' or input_field.get_attribute('type') == 'submit' or input_field.get_attribute('type') == 'radio' or input_field.get_attribute('type') == 'checkbox':
                continue
            if input_field.get_attribute('value') != '':
                continue
            try:
                if input_field.get_attribute('type') == 'tel':
                    phone = data['phone']
                    print("Phone: ", phone)
                    human_type(input_field, phone)
                elif "email" in input_field.get_attribute('placeholder').lower() or "email" in input_field.get_attribute('aria-label').lower() or "email" in input_field.get_attribute('name').lower() or "email" in input_field.get_attribute('id').lower() or "email" in input_field.get_attribute('class').lower() or "e-mail" in input_field.get_attribute('placeholder').lower() or "e-mail" in input_field.get_attribute('aria-label').lower() or "e-mail" in input_field.get_attribute('name').lower() or "e-mail" in input_field.get_attribute('id').lower() or "e-mail" in input_field.get_attribute('class').lower() or input_field.get_attribute('type') == 'email':
                    human_type(input_field, data['email'])
                else:
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

        text_areas = form.find_elements(By.CSS_SELECTOR, "textarea")
        keywords = ['message', 'comment', 'feedback', 'question', 'text', 'note', 'description','messege']
        for text_area in text_areas:
          #  if text_area.get_attribute('value') == '':
                try:
                    if any(keyword in text_area.get_attribute('placeholder').lower() for keyword in keywords) or any(keyword in text_area.get_attribute('aria-label').lower() for keyword in keywords) or any(keyword in text_area.get_attribute('name').lower() for keyword in keywords) or any(keyword in text_area.get_attribute('id').lower() for keyword in keywords) or any(keyword in text_area.get_attribute('class').lower() for keyword in keywords):
                        human_type(text_area, data['message'])
                    else:
                        human_type(text_area, 'soon')
                except Exception:
                    continue



    except Exception as e:
        logging.warning(f"Additional fields error: {str(e)}")
        logging.error(traceback.format_exc())