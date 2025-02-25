import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
import os
import json

from modules.app_service.form_submitter import FormSubmitter
from modules.app_service.text_handler import TextHandler
from modules.app_service.profile_manager import ProfileManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='form_submitter.log',
    filemode='a'
)

submitter = FormSubmitter()

def start_script():
    config = {
        'google_credentials': 'credentials.json',
        'spreadsheet_name': spreadsheet_entry.get(),
        'worksheet_name': worksheet_entry.get(),
        'drive_folder_id': drive_folder_entry.get(),
        'captcha_api_key': captcha_api_entry.get(),
        'form_data': {
            "name": name_entry.get(),
            "first": first_entry.get(),
            "last": last_entry.get(),
            "phone": phone_entry.get(),
            "email": email_entry.get(),
            "message": message_entry.get(),
            "subject": subject_entry.get(),
            "zip": zip_entry.get(),
        }
    }

    submitter.update_config(config)
    submitter.browser = browser_choice.get()

    thread = threading.Thread(target=submitter.run_script)
    thread.start()


def stop_script():
    submitter.stop_script()


def save_current_profile():
    name = profile_name_entry.get()
    if not name:
        messagebox.showerror("Error", "Profile name cannot be empty")
        return

    config = {
        'spreadsheet_name': spreadsheet_entry.get(),
        'worksheet_name': worksheet_entry.get(),
        'captcha_api_key': captcha_api_entry.get(),
        'form_data': {
            "name": name_entry.get(),
            "first": first_entry.get(),
            "last": last_entry.get(),
            "phone": phone_entry.get(),
            "email": email_entry.get(),
            "subject": subject_entry.get(),
            "message": message_entry.get(),
            "zip": zip_entry.get(),
        }
    }

    ProfileManager.save_profile(name, config)
    update_profile_list()
    profile_combobox.set(name)


def delete_current_profile():
    name = profile_name_entry.get()
    if not name:
        return

    try:
        ProfileManager.delete_profile(name)
        update_profile_list()
        profile_name_entry.delete(0, tk.END)
        profile_combobox.set('')
    except Exception as e:
        messagebox.showerror("Error", str(e))


def load_selected_profile(event):
    name = profile_combobox.get()
    if not name:
        return

    try:
        config = ProfileManager.load_profile(name)
        profile_name_entry.delete(0, tk.END)
        profile_name_entry.insert(0, name)

        spreadsheet_entry.delete(0, tk.END)
        spreadsheet_entry.insert(0, config.get('spreadsheet_name', ''))

        worksheet_entry.delete(0, tk.END)
        worksheet_entry.insert(0, config.get('worksheet_name', ''))

        drive_folder_entry.delete(0, tk.END)
        drive_folder_entry.insert(0, config.get('drive_folder_id', ''))

        captcha_api_entry.delete(0, tk.END)
        captcha_api_entry.insert(0, config.get('captcha_api_key', ''))

        form_data = config.get('form_data', {})
        name_entry.delete(0, tk.END)
        name_entry.insert(0, form_data.get('name', ''))

        first_entry.delete(0, tk.END)
        first_entry.insert(0, form_data.get('first', ''))

        last_entry.delete(0, tk.END)
        last_entry.insert(0, form_data.get('last', ''))

        phone_entry.delete(0, tk.END)
        phone_entry.insert(0, form_data.get('phone', ''))

        email_entry.delete(0, tk.END)
        email_entry.insert(0, form_data.get('email', ''))

        message_entry.delete(0, tk.END)
        message_entry.insert(0, form_data.get('message', ''))

        subject_entry.delete(0, tk.END)
        subject_entry.insert(0, form_data.get('subject', ''))

        zip_entry.delete(0, tk.END)
        zip_entry.insert(0, form_data.get('zip', ''))
    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_profile_list():
    profiles = ProfileManager.get_profiles()
    profile_combobox['values'] = profiles


def create_settings_frame(parent):
    frame = tk.LabelFrame(parent, text="Settings")
    frame.pack(pady=5, fill='x', padx=5)

    # Spreadsheet settings
    tk.Label(frame, text="Spreadsheet:").grid(row=0, column=0, sticky='e')
    tk.Label(frame, text="Worksheet:").grid(row=1, column=0, sticky='e')
    tk.Label(frame, text="Drive Folder ID:").grid(row=2, column=0, sticky='e')
    tk.Label(frame, text="Captcha API Key:").grid(row=3, column=0, sticky='e')

    global spreadsheet_entry, worksheet_entry, drive_folder_entry, captcha_api_entry
    spreadsheet_entry = tk.Entry(frame)
    worksheet_entry = tk.Entry(frame)
    drive_folder_entry = tk.Entry(frame)
    captcha_api_entry = tk.Entry(frame)

    spreadsheet_entry.grid(row=0, column=1, sticky='we', padx=5, pady=2)
    worksheet_entry.grid(row=1, column=1, sticky='we', padx=5, pady=2)
    drive_folder_entry.grid(row=2, column=1, sticky='we', padx=5, pady=2)
    captcha_api_entry.grid(row=3, column=1, sticky='we', padx=5, pady=2)

    # Form data settings
    form_frame = tk.LabelFrame(frame, text="Form Data")
    form_frame.grid(row=4, column=0, columnspan=2, sticky='we', padx=5, pady=5)

    labels = ["Name:", "First Name:", "Last Name:", "Phone:", "Email:", "Message:", "Subject:", "ZIP:"]
    entries = []
    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label).grid(row=i, column=0, sticky='e')
        entry = tk.Entry(form_frame)
        entry.grid(row=i, column=1, sticky='we', padx=5, pady=2)
        entries.append(entry)

    global name_entry, first_entry, last_entry, phone_entry, email_entry, message_entry, subject_entry, zip_entry
    name_entry, first_entry, last_entry, phone_entry, email_entry, message_entry, subject_entry, zip_entry = entries

    return frame


def create_profile_frame(parent):
    frame = tk.Frame(parent)
    frame.pack(pady=5, fill='x', padx=5)

    global profile_combobox, profile_name_entry
    profile_combobox = ttk.Combobox(frame, width=25)
    profile_combobox.pack(side=tk.LEFT, padx=5)
    profile_combobox.bind('<<ComboboxSelected>>', load_selected_profile)

    profile_name_entry = tk.Entry(frame, width=25)
    profile_name_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(frame, text="Save", command=save_current_profile).pack(side=tk.LEFT, padx=5)
    tk.Button(frame, text="Delete", command=delete_current_profile).pack(side=tk.LEFT, padx=5)

    update_profile_list()
    return frame


def main():
    global browser_choice
    root = tk.Tk()
    root.title("Form Submitter v2.0.0")

    # Browser selection
    browser_frame = tk.Frame(root)
    browser_frame.pack(pady=5)
    browser_choice = tk.StringVar(value="chrome")
    tk.Label(browser_frame, text="Browser:").pack(side=tk.LEFT)
    tk.Radiobutton(browser_frame, text="Chrome", variable=browser_choice, value="chrome").pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(browser_frame, text="Firefox", variable=browser_choice, value="firefox").pack(side=tk.LEFT, padx=5)

    # Settings and profiles
    create_profile_frame(root)
    create_settings_frame(root)

    # Control buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Start", width=15, command=start_script).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Stop", width=15, command=stop_script).pack(side=tk.LEFT, padx=5)

    # Logging area
    log_frame = tk.Frame(root)
    log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    text_area = tk.Text(log_frame, height=15, width=80)
    scrollbar = tk.Scrollbar(log_frame, command=text_area.yview)
    text_area.config(yscrollcommand=scrollbar.set)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    handler = TextHandler(text_area)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    root.mainloop()


if __name__ == "__main__":
    main()