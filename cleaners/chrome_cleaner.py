import os
import sqlite3
import shutil
import subprocess
from utils.logger import logger

class ChromeCleaner:
    def __init__(self):
        # Стандартний шлях до профілю Chrome на Windows
        local_app_data = os.path.expandvars('%LOCALAPPDATA%')
        self.history_path = os.path.join(local_app_data, 'Google', 'Chrome', 'User Data', 'Default', 'History')
        # Також може бути профіль "Profile 1", "Profile 2" тощо.
        # Для простоти поки використовуємо "Default".
        
    def is_chrome_running(self):
        """Перевіряє, чи запущений Chrome через tasklist."""
        try:
            output = subprocess.check_output('tasklist', shell=True).decode('cp1251', errors='ignore')
            return 'chrome.exe' in output.lower()
        except Exception as e:
            logger.error(f"Помилка при перевірці процесів: {e}")
            return False

    def clean(self, keywords):
        """Видаляє записи, що містять ключові слова, з бази даних History."""
        if not os.path.exists(self.history_path):
            logger.warning(f"Шлях до історії Chrome не знайдено: {self.history_path}")
            return

        if self.is_chrome_running():
            logger.error("Chrome запущений! Будь ласка, закрийте браузер перед очищенням.")
            return

        # Створюємо тимчасову копію для роботи (на всяк випадок)
        temp_history = self.history_path + ".tmp"
        try:
            shutil.copy2(self.history_path, temp_history)
            
            conn = sqlite3.connect(temp_history)
            cursor = conn.cursor()

            for word in keywords:
                # Видалення з таблиці urls (відвідані сторінки)
                cursor.execute("DELETE FROM urls WHERE url LIKE ? OR title LIKE ?", (f'%{word}%', f'%{word}%'))
                urls_deleted = cursor.rowcount
                
                # Видалення з таблиці keyword_search_terms (пошукові запити)
                cursor.execute("DELETE FROM keyword_search_terms WHERE term LIKE ?", (f'%{word}%',))
                terms_deleted = cursor.rowcount
                
                if urls_deleted > 0 or terms_deleted > 0:
                    logger.info(f"Слово '{word}': видалено {urls_deleted} посилань та {terms_deleted} пошукових запитів.")

            conn.commit()
            conn.close()

            # Замінюємо оригінальний файл обробленим
            shutil.move(temp_history, self.history_path)
            logger.info("Очищення історії Chrome завершено успішно.")

        except Exception as e:
            logger.error(f"Помилка під час очищення Chrome: {e}")
            if os.path.exists(temp_history):
                os.remove(temp_history)
