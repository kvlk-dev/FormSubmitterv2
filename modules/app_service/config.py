import os
import logging

class Config:
    """Класс конфигурации приложения"""
    def __init__(self):
        self.config = self.init()
 #       self.validate_config()

    def init(self):

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='form_submitter.log'
        )


        CONFIG = {
            'google_credentials': 'credentials.json',
            'spreadsheet_name': "",
            'worksheet_name': "",
            'drive_folder_id': "",
            'captcha_api_key': "",
            'form_data': {
                "name": "",
                "first": "",
                "last": "",
                "phone": "",
                "email": "",
                "message": "",
                "subject": "",
                "zip": ""
            }
        }


        return CONFIG

    def update_config(self, new_config):
        """Обновление конфига с мерджем словарей"""
        self.config.update(new_config)
        self.validate_config()
        return self.config

    def validate_config(self):
            """Валидация обязательных параметров"""
            required = ['google_credentials', 'spreadsheet_name', 'worksheet_name']
            for key in required:
                if not self.config.get(key):
                    raise ValueError(f"Missing required config key: {key}")