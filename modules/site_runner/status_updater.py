import logging
from datetime import datetime

from modules.site_runner import screenshot_maker


def run(driver, sheet, row, processed_url, status, reason=None, phone=None):
    """Обновление статуса и добавление скриншота"""
    screenshot_url = screenshot_maker.run(driver, processed_url, status)
    try:
       updates = []
       if status == "Error":
          updates.append({"range": f"B{row}", "values": [["Error"]]})
          updates.append({"range": f"C{row}", "values": [[reason or '']]})
       else:
          updates.append({"range": f"B{row}", "values": [[status]]})

          updates.append({"range": f"D{row}", "values": [[phone or '']]})
          updates.append({"range": f"E{row}", "values": [[screenshot_url or '']]})
          updates.append({"range": f"G{row}", "values": [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]})

          sheet.batch_update(updates)  # Отправка одним запросом
    except Exception as e:
         print(row, status, reason, phone, screenshot_url)
         logging.info(f"Updating row {row}: status={status}, phone={phone}, screenshot={screenshot_url}")
         logging.error(f"Status update error: {str(e)}")
