
def kill_browser_processes():
    import subprocess
    """Принудительно закрывает процессы браузеров через taskkill (для Windows)"""
    browser_names = ["chrome.exe", "chromedriver.exe", "firefox.exe", "geckodriver.exe"]

    for name in browser_names:
        try:
            subprocess.run(["taskkill", "/F", "/IM", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Ошибка при завершении {name}: {e}")