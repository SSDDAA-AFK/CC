import os
import glob
from utils.logger import logger

class SystemCleaner:
    def __init__(self):
        # Шляхи до системних папок (автоматично для поточного користувача)
        self.recent_dir = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Recent')
        self.prefetch_dir = r"C:\Windows\Prefetch"
        self.local_appdata = os.environ['LOCALAPPDATA']
        self.ps_history = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt')

    def clean_recent_and_ps(self, keywords):
        """Очищення Recent Files та історії PowerShell."""
        logger.info("Очищення Recent Files та історії PowerShell...")
        
        # 1. Recent Files
        if os.path.exists(self.recent_dir):
            for f in os.listdir(self.recent_dir):
                for word in keywords:
                    if word.lower() in f.lower():
                        try:
                            os.remove(os.path.join(self.recent_dir, f))
                            logger.info(f"Видалено ярлик: {f}")
                        except: pass

        # 2. PowerShell History
        if os.path.exists(self.ps_history):
            try:
                with open(self.ps_history, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Фільтруємо рядки, які НЕ містять ключових слів
                new_lines = [line for line in lines if not any(word.lower() in line.lower() for word in keywords)]
                
                if len(new_lines) < len(lines):
                    with open(self.ps_history, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    logger.info(f"Очищено історію PowerShell (видалено {len(lines) - len(new_lines)} рядків).")
            except Exception as e:
                logger.error(f"Не вдалося очистити історію PowerShell: {e}")

    def clean_prefetch(self, keywords):
        """Очищення Prefetch файлів."""
        logger.info("Очищення Prefetch...")
        if not os.path.exists(self.prefetch_dir):
            return

        files = glob.glob(os.path.join(self.prefetch_dir, "*.pf"))
        for f in files:
            file_name = os.path.basename(f)
            for word in keywords:
                if word.upper() in file_name.upper():
                    try:
                        os.remove(f)
                        logger.info(f"Видалено Prefetch: {file_name}")
                    except: pass

    def clean_local_cfgs(self):
        """Видалення ВСІХ .cfg файлів безпосередньо в папці LocalAppData (без підпапок)."""
        logger.info(f"Очищення всіх .cfg файлів у корені {self.local_appdata}...")
        
        try:
            # Отримуємо список усіх файлів тільки в цій директорії (без рекурсії)
            for file in os.listdir(self.local_appdata):
                full_path = os.path.join(self.local_appdata, file)
                
                # Перевіряємо, що це файл (не папка) і він має розширення .cfg
                if os.path.isfile(full_path) and file.lower().endswith('.cfg'):
                    try:
                        os.remove(full_path)
                        logger.info(f"Видалено файл конфігурації: {file}")
                    except Exception as e:
                        logger.error(f"Не вдалося видалити {file}: {e}")
        except Exception as e:
            logger.error(f"Помилка при доступі до LocalAppData: {e}")
