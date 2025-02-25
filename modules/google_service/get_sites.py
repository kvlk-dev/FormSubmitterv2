import logging
def run(sheet):
        """Получение сайтов с пустыми статусами из 2 и 3 столбцов"""
        try:
            all_data = sheet.get_all_values()
            return [
                (row_idx + 2, row[0].strip())  # +2: заголовок + нумерация с 1
                for row_idx, row in enumerate(all_data[1:])  # Пропускаем заголовок
                if len(row) > 2 and row[0].strip() and (not row[1].strip() or row[1].strip() != "Success")
            ]
        except Exception as e:
            logging.error(f"Ошибка получения сайтов: {str(e)}")
            return []