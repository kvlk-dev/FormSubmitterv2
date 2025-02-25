import logging
from datetime import datetime

def run(sheet, idx):
    """Добавляем статус обработки"""
    try:
        sheet.update_cell(idx, 2, "Processing")
        sheet.update_cell(idx, 6, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        logging.error(f"Ошибка добавления статуса обработки в B{idx}: {str(e)}")
