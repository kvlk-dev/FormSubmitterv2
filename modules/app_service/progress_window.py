import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
import logging
from collections import defaultdict


class ProgressWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Progress Monitor")
        self.geometry("1000x800")

        # Инициализация состояния
        self.total_tasks = 0
        self.completed = 0
        self.errors = defaultdict(int)
        self.queue = queue.Queue()
        self._original_handlers = []
        self._after_id = None
        self._closed = False

        # Настройка GUI
        self.create_widgets()
        self.setup_logging()
        self.protocol("WM_DELETE_WINDOW", self.safe_destroy)
        self.start_queue_processing()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Панель прогресса
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient='horizontal',
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        # Статистика
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)

        ttk.Label(stats_frame, text="Total Tasks:").pack(side=tk.LEFT)
        self.total_label = ttk.Label(stats_frame, text="0")
        self.total_label.pack(side=tk.LEFT, padx=10)

        ttk.Label(stats_frame, text="Processed:").pack(side=tk.LEFT)
        self.completed_label = ttk.Label(stats_frame, text="0")
        self.completed_label.pack(side=tk.LEFT, padx=10)

        ttk.Label(stats_frame, text="Errors:").pack(side=tk.LEFT)
        self.errors_label = ttk.Label(stats_frame, text="0")
        self.errors_label.pack(side=tk.LEFT, padx=10)

        # Вкладки
        self.notebook = ttk.Notebook(main_frame)

        # Вкладка логов
        self.log_tab = ttk.Frame(self.notebook)
        self.log_text = scrolledtext.ScrolledText(
            self.log_tab,
            wrap=tk.WORD,
            state='disabled'
        )
        self.log_text.pack(expand=True, fill=tk.BOTH)

        # Вкладка ошибок
        self.error_tab = ttk.Frame(self.notebook)
        self.error_tree = ttk.Treeview(
            self.error_tab,
            columns=("Type", "Count"),
            show="headings",
            selectmode="none"
        )
        self.error_tree.heading("Type", text="Error Type")
        self.error_tree.heading("Count", text="Count")
        self.error_tree.column("Type", width=400, anchor=tk.W)
        self.error_tree.column("Count", width=100, anchor=tk.CENTER)
        self.error_tree.pack(expand=True, fill=tk.BOTH)

        self.notebook.add(self.log_tab, text="Logs")
        self.notebook.add(self.error_tab, text="Errors")
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Кнопки управления
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        self.close_btn = ttk.Button(
            btn_frame,
            text="Close",
            command=self.safe_destroy,
            state=tk.DISABLED
        )
        self.close_btn.pack(side=tk.LEFT, padx=5)

    def setup_logging(self):
        """Настройка системы логирования"""
        self.gui_handler = GuiLogHandler(self.queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.gui_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        self._original_handlers = root_logger.handlers.copy()
        root_logger.addHandler(self.gui_handler)

    def start_queue_processing(self):
        """Запуск обработки очереди"""
        if not self._closed:
            self._after_id = self.after(100, self.process_queue)

    def process_queue(self):
        """Обработка сообщений из очереди"""
        if self._closed or not self.winfo_exists():
            return

        try:
            while True:
                msg = self.queue.get_nowait()
                self.process_record(msg)
        except queue.Empty:
            pass

        self.start_queue_processing()

    def process_record(self, msg):
        """Обработка одной записи лога"""
        if self._closed or not self.winfo_exists():
            return

        try:

            if isinstance(msg, tuple):
                msg_type, content = msg
                if msg_type == "progress":
                    self.update_progress(content)
                    return
                elif msg_type == "total":
                    self.update_total_tasks(content)
                    return
                else:
                    msg = str(msg)  # На всякий случай приводим к строке
            # Обновление логов
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.configure(state='disabled')
            self.log_text.see(tk.END)

            # Обработка статусов
            if "Status:" in msg:
                self.handle_status_message(msg)

        except tk.TclError as e:
            if "invalid command name" in str(e):
                self.safe_destroy()
            else:
                raise

    def handle_status_message(self, msg):
        """Обработка статусов"""
        try:
            status_part = msg.split("Status: ")[1]
            status, reason = status_part.split(", Reason: ", 1)
            status = status.strip().lower()

            if status == "error":
                self.add_error(reason)

        except Exception as e:
            logging.error(f"Error parsing status message: {str(e)}")

    def add_error(self, error_type):
        """Добавление ошибки в статистику"""
        self.errors[error_type] += 1
        self.errors_label.config(text=str(sum(self.errors.values())))
        self.update_error_tree()

    def update_error_tree(self):
        """Обновление списка ошибок"""
        if not self.winfo_exists():
            return

        self.error_tree.delete(*self.error_tree.get_children())
        for error_type, count in self.errors.items():
            self.error_tree.insert("", tk.END, values=(error_type, count))

    def update_progress(self, current):
        """Обновление прогресса"""
        if self._closed or not self.winfo_exists():
            return

        self.completed = current
        try:
            self.progress_bar["value"] = self.completed
            self.completed_label.config(text=str(self.completed))

            #if self.completed >= self.total_tasks:
                # self.on_all_tasks_completed()
        except tk.TclError:
            print("TclError")
            #self.safe_destroy()

    def update_total_tasks(self, total):
        """Обновление общего количества задач"""
        if self.winfo_exists():
            self.total_tasks = total
            self.progress_bar.config(maximum=total)
            self.total_label.config(text=str(total))

    def on_all_tasks_completed(self):
        """Действия при завершении задач"""
        if self.winfo_exists():
            self.close_btn.config(state=tk.NORMAL)
#            messagebox.showinfo(
#                "Complete",
#                f"Completed: {self.completed}\nErrors: {sum(self.errors.values())}"
 #           )

    def safe_destroy(self):
        """Безопасное закрытие окна"""
        if self._closed:
            return

        self._closed = True

        # Остановка обработки очереди
        if self._after_id:
            self.after_cancel(self._after_id)

        # Восстановление логгеров
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.gui_handler)
        root_logger.handlers = self._original_handlers

        # Закрытие окна
        if self.winfo_exists():
            self.destroy()


class GuiLogHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self._closed = False

    def emit(self, record):
        """Отправка сообщения в очередь"""
        if not self._closed:
            try:
                msg = self.format(record)
                self.queue.put(msg)
            except Exception as e:
                logging.error(f"Log queue error: {str(e)}")

    def close(self):
        self._closed = True
        super().close()