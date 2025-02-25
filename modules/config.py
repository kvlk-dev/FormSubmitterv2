def init():
    import os
    import logging
    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='form_submitter.log'
    )

    load_dotenv('.env')

    initial_phone = os.getenv("PHONE")
    CONFIG = {
        'google_credentials': 'credentials.json',
        'spreadsheet_name': os.getenv('SPREADSHEET_NAME'),
        'worksheet_name': os.getenv('WORKSHEET_NAME'),
        'drive_folder_id': os.getenv('DRIVE_FOLDER_ID'),
        'captcha_api_key': os.getenv("CAPTCHA_API_KEY"),
        'form_data': {
            "name": os.getenv("FIRST_NAME"),
            "first": os.getenv("FIRST_NAME"),
            "last": os.getenv("LAST_NAME"),
            "phone": initial_phone,
            "email": os.getenv("EMAIL"),
            "message": os.getenv("MESSAGE"),
            "subject": os.getenv("SUBJECT"),
            "zip": os.getenv("ZIP"),
        }
    }

    return CONFIG

def update_config(self, new_config):
        """Обновление конфига с мерджем словарей"""
        self.config.update(new_config)

def validate_config(self):
        """Валидация обязательных параметров"""
        required = ['google_credentials', 'spreadsheet_name', 'worksheet_name']
        for key in required:
            if not self.config.get(key):
                raise ValueError(f"Missing required config key: {key}")