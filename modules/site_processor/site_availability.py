import logging
import requests
from urllib3.util.retry import Retry
import urllib3
from requests.adapters import HTTPAdapter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def check_http_status(url):
    """Проверка доступности сайта с расширенной обработкой ошибок"""
    try:
        # Создаем сессию с повторами и User-Agent
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"]
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        # Выполняем запрос с реалистичными заголовками
        response = session.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            },
            verify=False  # Для тестовых серверов с самоподписанными сертификатами
        )

        # Проверяем статус код и наличие контента
        if response.status_code >= 400:
            logging.warning(f"HTTP {response.status_code} для {url}")

            # Исключения для некоторых статусов
            if response.status_code == 403 and "cloudflare" in response.headers.get('Server', ''):
                return True  # Cloudflare может возвращать 403 даже на рабочие сайты

            return False

        # Проверка минимального размера контента
        if len(response.content) < 512:
            logging.warning(f"Маленький размер контента: {len(response.content)} байт")
            return False

        return True

    except requests.exceptions.SSLError:
        logging.warning("Игнорируем SSL ошибку для тестового сервера")
        return True

    except requests.exceptions.ConnectionError as e:
        logging.error(f"Ошибка подключения: {str(e)}")
        return False

    except requests.exceptions.Timeout:
        logging.warning("Таймаут запроса")
        return False

    except Exception as e:
        logging.error(f"Неожиданная ошибка: {str(e)}", exc_info=True)
        return False

def run(driver):

    """Проверка доступности сайта с обработкой DNS-ошибок"""
    # Проверка содержимого страницы на признаки ошибок
    page_source_lower = driver.page_source.lower()
    blocked_phrases = [
        "the chromium authors",
        "mozilla public - license",
        "you have been blocked",
        "dns_probe_finished_nxdomain",  # Ошибка DNS для Chrome
        "err_name_not_resolved",  # Ошибка DNS для Chrome
        "server not found",  # Ошибка DNS для Firefox
        "this site can’t be reached",  # Общая ошибка
        "connection refused"  # Ошибка соединения
    ]
    if any(phrase in page_source_lower for phrase in blocked_phrases):
        logging.warning(f"Сайт недоступен (содержимое): {driver.title}")
        return False

    # Проверка заголовка на наличие ключевых фраз
    blocked_titles = [
        "domain is parked",
        "this site can’t be reached",
        "domain expired",
        "access denied",
        "forbidden",
        "coming soon",
        "godaddy",
        "page not found",
        "website expired",
        "website is under construction",
        "website coming soon",
        "dns",  # Перехватывает "DNS_PROBE_FINISHED_NXDOMAIN" и подобные
        "err_name_not_resolved",
        "server not found"
    ]
    page_title = driver.title.lower()
    for phrase in blocked_titles:
        if phrase in page_title:
            logging.warning(f"Страница недоступна (заголовок): {driver.title}")
            return False

    # Проверка изменения URL (если драйвер не смог перейти на сайт)
    try:
        current_url = driver.current_url.lower()
        initial_url = driver.execute_script("return window.location.href;").lower()
        if current_url != initial_url:
            logging.warning(f"Редирект на ошибку: {current_url}")
            return False
    except Exception as e:
        logging.error(f"Ошибка проверки URL: {str(e)}")

    # Дополнительная проверка для Chrome (ERR_* в title)
    if "err_" in page_title or "nxdomain" in page_title:
        logging.warning(f"Обнаружена ошибка браузера: {driver.title}")
        return False

    return True