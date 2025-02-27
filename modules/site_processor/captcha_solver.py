import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
class CaptchaSolver:
    def __init__(self, captcha_api_key):
        self.client = TwoCaptcha(captcha_api_key)
        pass

    def solve_recaptcha(self, driver):
        """Определяем версию reCAPTCHA и решаем её"""
        try:
            version = self.get_recaptcha_version(driver)
            logging.info(f"Определённая версия reCAPTCHA: {version}")
            site_key = None
            try:
                site_key = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
                ).get_attribute("data-sitekey")
            except Exception:
                pass
            if not site_key:
                try:
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
                    )
                    site_key = re.search(r"k=([^&]+)", iframe.get_attribute("src")).group(1)
                except Exception:
                    pass
            if not site_key:
                logging.warning("Не удалось получить sitekey reCAPTCHA")
                return False


            if version == "v3":
                return self.solve_recaptcha_v3(driver, site_key)  # Аккуратно решаем v3

            elif version in ["v2", "v2-invisible"]:
                return self.solve_recaptcha_v2(driver,site_key)  # Обычное решение v2

            else:
                logging.warning("Не удалось определить версию reCAPTCHA")
                return False

        except Exception as e:
            logging.error(f"Ошибка при решении CAPTCHA: {str(e)}")
            return False

    def get_recaptcha_version(self, driver):
        """Определяет версию reCAPTCHA на странице"""
        try:
            # Ищем все iframe
            recaptcha_iframes = driver.find_elements(By.TAG_NAME, "iframe")

            for iframe in recaptcha_iframes:
                src = iframe.get_attribute("src")
                if "recaptcha/api2/anchor" in src:
                    return "v2"
                elif "recaptcha/enterprise/anchor" in src:
                    return "v3"

            # Invisible reCAPTCHA (v2)
            if driver.find_elements(By.CLASS_NAME, "grecaptcha-badge"):
                return "v2-invisible"

            # Проверяем наличие grecaptcha.execute() для v3
            is_v3 = driver.execute_script(
                "return typeof grecaptcha !== 'undefined' && typeof grecaptcha.execute === 'function'")
            if is_v3:
                return "v3"

            return "unknown"
        except Exception as e:
            logging.error(f"Ошибка при определении версии reCAPTCHA: {str(e)}")
            return "error"

    def solve_recaptcha_v3(self,driver,site_key):
        """Решение reCAPTCHA v3 через 2Captcha"""
        try:
            logging.info("Определена reCAPTCHA v3")
            logging.info("Отправляем запрос на решение reCAPTCHA v3...")

            # Отправляем запрос на 2Captcha (важно указать action!)
            task = self.client.recaptcha(
                sitekey=site_key,
                url=driver.current_url,
                version="v3",
                action="submit",
                score=0.9  # Запрашиваем максимальный score
            )
            logging.info("Получен токен")
            # Вставляем токен в поле g-recaptcha-response
            driver.execute_script(f'document.getElementById("g-recaptcha-response").value = "{task["code"]}";')

            logging.info("reCAPTCHA v3 решена, токен вставлен.")

            return True

        except Exception as e:
            logging.error(f"Ошибка при решении reCAPTCHA v3: {str(e)}")
            return False

    def solve_recaptcha_v2(self, driver,site_key):
        try:
            logging.info("Отправляем запрос на решение reCAPTCHA v2...")
            result = self.client.recaptcha(
                sitekey=site_key,
                url=driver.current_url
            )
            logging.info("Получен токен")
            driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML = "{result["code"]}";')
            return True
        except Exception as e:
            logging.error(f"Ошибка решения reCAPTCHA v2: {str(e)}")
            return False
