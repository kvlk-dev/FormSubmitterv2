import logging
from datetime import datetime

from modules.site_runner import screenshot_maker

def run(driver, sheet, row, processed_url, status, reason=None, phone=None, site_email=None, site_phone=None):
    """Обновление статуса и добавление скриншота"""
    screenshot_url = screenshot_maker.run(driver, processed_url, status)
    try:
        updates = [
            {"range": f"B{row}", "values": [[status]]},
            {"range": f"C{row}", "values": [[reason or '']]},
            {"range": f"D{row}", "values": [[phone or '']]},
            {"range": f"E{row}", "values": [[screenshot_url or '']]},
            {"range": f"G{row}", "values": [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]},
            {"range": f"J{row}", "values": [[site_email or '']]},
            {"range": f"I{row}", "values": [[site_phone or '']]}
        ]

        sheet.batch_update(updates)

    except Exception as e:
        print(row, status, reason, phone, screenshot_url)
        logging.info(f"Updating row {row}: status={status}, phone={phone}, screenshot={screenshot_url}")
        logging.error(f"Status update error: {str(e)}")