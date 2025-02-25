import logging
import re
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.site_processor import phone_processor, additional_fields_handler


def run(driver,form,data):
    """Заполнение формы"""
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form)

    # получаем все элементы формы
    form_elements = form.find_elements(By.XPATH, ".//input | .//textarea | .//select")

    # Компилируем регулярные выражения для поиска полей
    fields_mapping = {
        'name': re.compile(r'\b(name|fullname|full|your-name|full\s?name|your\s?name)\b', re.IGNORECASE),
        'first': re.compile(r'\b(first|first-name|firstname|first\s?name|given)\b', re.IGNORECASE),
        'last': re.compile(r'\b(last|last-name|lastname|last\s?name|surname)\b', re.IGNORECASE),
        'email': re.compile(r'\b(email|your-email|e-mail|mail)\b', re.IGNORECASE),
        'message': re.compile(r'\b(message|comments|your-message|question|comment|tell|feedback)\b',
                              re.IGNORECASE),
        'subject': re.compile(r'\b(subject|theme|topic|title)\b', re.IGNORECASE),
        'phone': re.compile(r'\b(phone|tel|telephone|contact|mobile|cell)\b', re.IGNORECASE),
        'zip': re.compile(r'\b(zip|postal|post|code|index)\b', re.IGNORECASE)
    }
    try:
        for field_type, regex in fields_mapping.items():
            element_filled = False
            for attr in ['name', 'aria-label', 'placeholder', 'id']:
                try:
                    elements = form.find_elements(By.XPATH, f".//*[@{attr}]")
                    for element in elements:
                        if regex.search(element.get_attribute(attr) or ''):
                            if field_type == 'phone':
                                data[field_type] = phone_processor.run(driver, data['phone'])
                            element.clear()
                            element.send_keys(data[field_type])
                            time.sleep(random.uniform(0.3, 0.7))
                            element_filled = True
                            break
                    if element_filled:
                        break
                except Exception:
                    continue

            if not element_filled:
                try:
                    labels = form.find_elements(By.XPATH, ".//label")
                    for label in labels:
                        if regex.search(label.text or ''):
                            input_id = label.get_attribute("for")
                            if input_id:
                                element = form.find_element(By.ID, input_id)
                            else:
                                element = label.find_element(By.XPATH, ".//input | .//textarea")
                            if element:
                                if field_type == 'phone':
                                    data[field_type] = phone_processor.run(driver, data['phone'])
                                element.clear()
                                element.send_keys(data[field_type])
                                time.sleep(random.uniform(0.3, 0.7))
                                element_filled = True
                                break
                except Exception:
                    continue

            if not element_filled and field_type == 'message':
                try:
                    element = WebDriverWait(form, 25).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'textarea'))
                    )
                    element.clear()
                    element.send_keys(data[field_type])
                    time.sleep(random.uniform(0.3, 0.7))
                except Exception as e:
                    logging.warning(f"Не удалось найти поле для {field_type}: {str(e)}")

        additional_fields_handler.run(driver, form, data)
        return True, form
    except Exception as e:
        logging.error(f"Form filling error: {str(e)}")
        return False, None