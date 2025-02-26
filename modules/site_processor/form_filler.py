import logging
import re
import time
import random

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.site_processor import phone_processor, additional_fields_handler


def run(driver,form,data):
    """Заполнение формы"""
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form)
    PRIORITY_ORDER = ['email', 'phone', 'zip', 'name', 'first', 'last',  'subject', 'message']
    fields_mapping = [
        ('email', re.compile(r'^email$|e-?mail$|your-?email$', re.I)),
        ('phone', re.compile(r'^phone$|tel$|telephone$|mobile$|cell$', re.I)),
        ('zip', re.compile(r'^zip$|postal$|post$|code$', re.I)),
        ('first', re.compile(r'^first$|first-?name$|given$', re.I)),
        ('last', re.compile(r'^last$|last-?name$|surname$', re.I)),
        ('name', re.compile(r'^name$|full-?name$|your-?name$', re.I)),
        ('subject', re.compile(r'^subject$|title$|topic$', re.I)),
        ('message', re.compile(r'^message$|comment$|feedback$', re.I))
    ]
    # Обработка input-полей
    for element in form.find_elements(By.XPATH, ".//input[not(@type='hidden')]"):
        element_value = None
        for attr in ['id', 'name', 'placeholder', 'aria-label']:
            value = (element.get_attribute(attr) or '').strip().lower()
            if not value:
                continue

            # Проверяем поля в порядке приоритета
            for field_type in PRIORITY_ORDER:
                pattern = next(p for ft, p in fields_mapping if ft == field_type)
                if pattern.fullmatch(value):
                    if field_type == 'phone':
                        data[field_type] = phone_processor.run(driver, data['phone'])
                    element_value = data.get(field_type)
                    break
            if element_value:
                break

        if element_value:
            try:
                element.clear()
                element.send_keys(element_value)
                time.sleep(random.uniform(0.2, 0.5))
            except WebDriverException:
                pass

    # Обработка textarea
    for textarea in form.find_elements(By.TAG_NAME, 'textarea'):
        content = None
        for attr in ['id', 'name', 'placeholder']:
            value = (textarea.get_attribute(attr) or '').strip().lower()
            if not value:
                continue

            if fields_mapping[-1][1].fullmatch(value):  # Проверка для message
                content = data.get('message')
                break

        if content:
            try:
                textarea.clear()
                textarea.send_keys(content)
                time.sleep(random.uniform(0.2, 0.5))
            except WebDriverException:
                pass
    # try:
    #     for field_type, regex in fields_mapping.items():
    #         element_filled = False
    #         for attr in ['name', 'aria-label', 'placeholder', 'id']:
    #             try:
    #                 elements = form.find_elements(By.XPATH, f".//*[@{attr}]")
    #                 for element in elements:
    #                     if regex.search(element.get_attribute(attr) or ''):
    #                         if field_type == 'phone':
    #                             data[field_type] = phone_processor.run(driver, data['phone'])
    #                         element.clear()
    #                         element.send_keys(data[field_type])
    #                         time.sleep(random.uniform(0.3, 0.7))
    #                         element_filled = True
    #                         break
    #                 if element_filled:
    #                     break
    #             except Exception:
    #                 continue
    #
    #         if not element_filled:
    #             try:
    #                 labels = form.find_elements(By.XPATH, ".//label")
    #                 for label in labels:
    #                     if regex.search(label.text or ''):
    #                         input_id = label.get_attribute("for")
    #                         if input_id:
    #                             element = form.find_element(By.ID, input_id)
    #                         else:
    #                             element = label.find_element(By.XPATH, ".//input | .//textarea")
    #                         if element:
    #                             if field_type == 'phone':
    #                                 data[field_type] = phone_processor.run(driver, data['phone'])
    #                             element.clear()
    #                             element.send_keys(data[field_type])
    #                             time.sleep(random.uniform(0.3, 0.7))
    #                             element_filled = True
    #                             break
    #             except Exception:
    #                 continue
    #
    #         if not element_filled and field_type == 'message':
    #             try:
    #                 element = WebDriverWait(form, 25).until(
    #                     EC.presence_of_element_located((By.TAG_NAME, 'textarea'))
    #                 )
    #                 element.clear()
    #                 element.send_keys(data[field_type])
    #                 time.sleep(random.uniform(0.3, 0.7))
    #             except Exception as e:
    #                 logging.warning(f"Не удалось найти поле для {field_type}: {str(e)}")
    #

        additional_fields_handler.run(driver, form, data)
        return True, form
    # except Exception as e:
    #     logging.error(f"Form filling error: {str(e)}")
    #     return False, None