import logging
import re
import time
import random
from selenium.common import WebDriverException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.site_processor import phone_processor, additional_fields_handler

def run(driver, form, data):
    """Заполнение формы"""
    try:
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
            try:
                element.clear()
                #element.value = ''
                driver.execute_script("arguments[0].value = ''", element)
                element.send_keys(value)
                time.sleep(random.uniform(0.2, 0.5))
            except WebDriverException:
                pass

        for element in form.find_elements(By.XPATH, ".//input[not(@type='hidden')]"):
            for attr in ['id', 'name', 'placeholder', 'aria-label']:
                value = (element.get_attribute(attr) or '').strip().lower()
                if value:
                    for field_type in PRIORITY_ORDER:
                        if fields_mapping[field_type].fullmatch(value):
                            element_value = data[field_type]
                            if field_type == 'phone':
                                element_value = phone_processor.run(driver, data['phone'])
                            fill_element(element, element_value)
                            break

        for textarea in form.find_elements(By.TAG_NAME, 'textarea'):
            for attr in ['id', 'name', 'placeholder']:
                value = (textarea.get_attribute(attr) or '').strip().lower()
                if value and fields_mapping['message'].fullmatch(value):
                    fill_element(textarea, data['message'])
                    break

        for field_type, regex in fields_mapping.items():
            element_filled = False
            for attr in ['name', 'aria-label', 'placeholder', 'id']:
                elements = form.find_elements(By.XPATH, f".//*[@{attr}]")
                for element in elements:
                    if regex.search(element.get_attribute(attr) or ''):
                        element_value = data[field_type]
                        if field_type == 'phone':
                            element_value = phone_processor.run(driver, data['phone'])
                        if element.get_attribute('value') == '':
                            fill_element(element, element_value)
                        element_filled = True
                        break
                if element_filled:
                    break

            if not element_filled:
                labels = form.find_elements(By.XPATH, ".//label")
                for label in labels:
                    if regex.search(label.text or ''):
                        input_id = label.get_attribute("for")
                        element = form.find_element(By.ID, input_id) if input_id else label.find_element(By.XPATH, ".//input | .//textarea")
                        if element:
                            element_value = data[field_type]
                            if field_type == 'phone':
                                element_value = phone_processor.run(driver, data['phone'])
                            fill_element(element, element_value)
                            element_filled = True
                            break


        additional_fields_handler.run(driver, form, data)
        return True, form
    except (NoSuchElementException, StaleElementReferenceException) as e:
        logging.error(f"Form filling error: {str(e)}")
        return False, form
    except Exception as e:
        #logging.error(f"Form filling error: {str(e)}")
        logging.error(f"Form filling error. Exception type: {type(e).__name__}, Args: {e.args}")
        logging.exception("Error details:")
        return False, form