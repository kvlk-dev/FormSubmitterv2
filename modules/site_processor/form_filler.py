import logging
import re
import time
import random
import traceback

from selenium.common import WebDriverException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.site_processor import phone_processor, additional_fields_handler

def run(driver, form, data):
    """Заполнение формы"""
    try:
        filled_elements = []
        actions = ActionChains(driver)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form)
        PRIORITY_ORDER = ['email', 'phone', 'zip', 'name', 'first', 'last', 'subject', 'message']
        fields_mapping = {
            'email': re.compile(r'^email$|e-?mail$|your-?email$', re.I),
            'phone': re.compile(r'^phone$|tel$|telephone$|mobile$|cell$', re.I),
            'zip': re.compile(r'^zip$|postal$|post$|code$', re.I),
            'first': re.compile(r'^first$|first-?name$|given$|first name$', re.I),
            'last': re.compile(r'^last$|last-?name$|surname$|last name$', re.I),
            'name': re.compile(r'^name$|full-?name$|your-?name$|full name$', re.I),
            'subject': re.compile(r'^subject$|title$|topic$', re.I),
            'message': re.compile(r'^message$|comment$|feedback$', re.I)
        }


        def fill_element(element, value):
            """Заполнение элемента формы"""

            if element in filled_elements:
                return
            try:
                actions.reset_actions()
                # Прокрутка к элементу и ожидание кликабельности
                driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", element)
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable(element)
                )
                element.clear()
                logging.info(f"Поле {element.get_attribute('id')} очищено")
                # Очистка поля через комбинацию клавиш
                # actions.move_to_element(element).click()
                # actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
                # actions.send_keys(Keys.BACKSPACE)
                # actions.perform()

                # нажатие клавиши Home
                logging.info(f"Переход в начало строки")
                actions.move_to_element(element).click().key_down(Keys.HOME).perform()
                actions.pause(random.uniform(0.1, 0.3))
                logging.info(f"Ввод значения {value} в поле {element.get_attribute('id') or element.get_attribute('name') or element.get_attribute('class')}")
                if element.get_attribute('type') == 'tel':
                    for digit in value:
                        actions.send_keys(digit)
                        actions.pause(random.uniform(0.05, 0.2))
                else:
                    actions.send_keys_to_element(element, value)
                    actions.pause(random.uniform(0.05, 0.2))
                actions.perform()
                filled_elements.append(element)

                time.sleep(random.uniform(0.2, 0.5))

            except (WebDriverException, TimeoutException) as e:
                if element.is_displayed() and element.is_enabled():
                    logging.warning(f"Alternative fill method for {element.get_attribute('id')}")
                    element.clear()
                    element.send_keys(value)
        # for element in form.find_elements(By.XPATH, ".//input[not(@type='hidden')]"):
        #     for attr in ['id', 'name', 'placeholder', 'aria-label']:
        #         value = (element.get_attribute(attr) or '').strip().lower()
        #         if value:
        #             for field_type in PRIORITY_ORDER:
        #                 if fields_mapping[field_type].fullmatch(value):
        #                     element_value = data[field_type]
        #                     # if field_type == 'phone':
        #                     #     element_value = phone_processor.run(driver, data['phone'])
        #                     fill_element(element, element_value)
        #                     break

        for textarea in form.find_elements(By.TAG_NAME, 'textarea'):
            t_fill = False

            for attr in ['id', 'name', 'placeholder','aria-label']:
                value = (textarea.get_attribute(attr) or '').strip().lower()
                if value and ("message" in value or "comment" in value or "feedback" in value or "text" in value or "description" in value or "reason" in value or "details" in value or "inquiry" in value):
                    fill_element(textarea, data['message'])
                    t_fill = True
                    break
            if not t_fill and textarea.is_displayed():
                fill_element(textarea, "soon")

        for input_field in form.find_elements(By.TAG_NAME, 'input'):
            if input_field.get_attribute('type') != 'text' and input_field.get_attribute('type') != 'tel' and input_field.get_attribute('type') != 'email':
                continue
            found = False
            if input_field.get_attribute('type') == 'email':
                fill_element(input_field, data['email'])

                found = True
            if input_field.get_attribute('type') == 'tel':
                fill_element(input_field, data['phone'])
                found = True
            if input_field.get_attribute('type') == 'text':
                for attr in ['id', 'name', 'placeholder', 'aria-label']:
                    value = (input_field.get_attribute(attr) or '').strip().lower()
                    if value:
                        element_value = None
                        for field_type in PRIORITY_ORDER:
                            if fields_mapping[field_type].match(value):
                                element_value = data[field_type]
                                break
                        if element_value:
                            fill_element(input_field, element_value)
                            found = True
                            break

            if not found:
                labels = form.find_elements(By.XPATH, ".//label")
                for label in labels:
                    for fields_mapping_key, regex in fields_mapping.items():
                        label_text = label.text.lower().replace('*', '').strip()
                        if regex.search(label_text or ''):
                            input_id = label.get_attribute("for")
                            element = form.find_element(By.ID, input_id) if input_id else label.find_element(By.XPATH, ".//input | .//textarea")
                            if element:
                                element_value = data[fields_mapping_key]
                                fill_element(element, element_value)
                                found = True
                                break

            if not found:
                fill_element(input_field, "soon")

        #
        # for field_type, regex in fields_mapping.items():
        #     element_filled = False
        #     for attr in ['name', 'aria-label', 'placeholder', 'id']:
        #         elements = form.find_elements(By.XPATH, f".//*[@{attr}]")
        #         for element in elements:
        #             if regex.search(element.get_attribute(attr) or ''):
        #                 element_value = data[field_type]
        #                 # if field_type == 'phone':
        #                 #     element_value = phone_processor.run(driver, data['phone'])
        #                 fill_element(element, element_value)
        #                 element_filled = True
        #                 break
        #         if element_filled:
        #             break
        #
        #     if not element_filled:
        #         labels = form.find_elements(By.XPATH, ".//label")
        #         for label in labels:
        #             if regex.search(label.text or ''):
        #                 input_id = label.get_attribute("for")
        #                 element = form.find_element(By.ID, input_id) if input_id else label.find_element(By.XPATH, ".//input | .//textarea")
        #                 if element:
        #                     element_value = data[field_type]
        #                     # if field_type == 'phone':
        #                     #     element_value = phone_processor.run(driver, data['phone'])
        #                     fill_element(element, element_value)
        #                     element_filled = True
        #                     break

        additional_fields_handler.run(driver, form, data, filled_elements)
        return True, form
    except (NoSuchElementException, StaleElementReferenceException) as e:
        logging.error(f"Form filling error: {str(e)}")
        logging.error(traceback.format_exc())
        return False, form
    except Exception as e:
        #logging.error(f"Form filling error: {str(e)}")
        logging.error(f"Form filling error. Exception type: {type(e).__name__}, Args: {e.args}")
        logging.exception("Error details:")
        logging.error(traceback.format_exc())
        return False, form