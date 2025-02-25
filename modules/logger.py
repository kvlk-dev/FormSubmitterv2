import logging
import tkinter as tk

class TextHandler(logging.Handler):
    """Кастомный логгер, пишущий логи в tkinter.Text"""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        # Чтобы не блокировать GUI, добавляем текст через метод .after(...)
        self.text_widget.after(0, self._append_log, msg)

    def _append_log(self, msg):
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)  # Скроллим вниз до последней строчки
