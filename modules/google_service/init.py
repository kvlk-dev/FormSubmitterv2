import logging

import gspread
from google.oauth2 import service_account

class GoogleService:
    def __init__(self, config):
        self.sheet = None
        self.drive_service = None
        self.config = config

    def validate_config(self):
        """Проверка конфига на наличие необходимых полей"""
        if not self.config.get('google_credentials'):
            raise ValueError('google_credentials not found in config')
        if not self.config.get('spreadsheet_name'):
            raise ValueError('spreadsheet_name not found in config')
        if not self.config.get('worksheet_name'):
            raise ValueError('worksheet_name not found in config')

    def init(self):
        """Инициализация Google сервисов с едиными credentials"""
        self.validate_config()  # Проверка перед использованием

        try:
            # Создаем единые учетные данные
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

            creds = service_account.Credentials.from_service_account_file(
                self.config['google_credentials'],
                scopes=scope
            )

            # Инициализация Sheets
            gc = gspread.authorize(creds)

            self.sheet = gc.open(self.config['spreadsheet_name']).worksheet(
                self.config['worksheet_name']
            )

            # Инициализация Drive (используем те же credentials)
            #self.drive_service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            raise ValueError(f"Error initializing Google services: {str(e)}")
        return self.sheet
