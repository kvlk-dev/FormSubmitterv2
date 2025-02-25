import logging

def run(sheet, row_num):
        """Добавляем формулу в колонку H при старте обработки"""
        try:
            formula = (
                f'IF(AND(F{row_num}<>"", G{row_num}<>""), G{row_num}-F{row_num}, '
                f'IF(AND(F{row_num}<>"", G{row_num}=""), NOW()-F{row_num}, ""))'
            )
            # Обновляем ячейку в колонке H (если считать с 1 – это столбец 8; поправь при необходимости)
            sheet.update_cell(row_num, 8, f'={formula}')
        except Exception as e:
            logging.error(f"Ошибка добавления формулы в H{row_num}: {str(e)}")
