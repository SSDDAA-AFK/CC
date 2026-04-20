import subprocess
import os
import sys
import ctypes
from utils.logger import logger

class JournalCleaner:
    def __init__(self):
        # Список дисків, які ми можемо очистити
        self.available_drives = ['C:', 'D:', 'E:', 'F:']

    def is_admin(self):
        """Перевірка на права адміністратора."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def clean(self):
        """Очищення USN Journal для вибраного диска."""
        print("\n--- Очищення USN Journal ---")
        for i, drive in enumerate(self.available_drives, 1):
            print(f"  {i} - {drive}")
        
        try:
            choice = input("\nВиберіть диск для очищення (номер): ").strip()
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(self.available_drives):
                logger.error("Неправильний вибір диска.")
                return

            drive = self.available_drives[int(choice) - 1]
            logger.info(f"Перевірка USN Journal на диску {drive}...")

            # Перевірка наявності журналу
            check_cmd = f"fsutil usn queryjournal {drive}"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"USN Journal не знайдено на диску {drive} або доступ обмежено.")
                return

            logger.info(f"Видалення USN Journal на {drive}...")
            
            # Команда видалення журналу (потребує прав адміністратора)
            # Якщо скрипт уже запущено від адміна, виконуємо напряму. 
            # Якщо ні — викликаємо PowerShell для запиту прав.
            delete_cmd = f"fsutil usn deletejournal /D {drive}"
            
            if self.is_admin():
                process = subprocess.run(delete_cmd, shell=True, capture_output=True, text=True)
                if process.returncode == 0:
                    logger.info(f"USN Journal успішно видалено на {drive}.")
                else:
                    logger.error(f"Помилка при видаленні: {process.stderr}")
            else:
                logger.warning("Потрібні права адміністратора для видалення журналу. Запит прав...")
                ps_cmd = f"Start-Process cmd -ArgumentList '/c fsutil usn deletejournal /D {drive}' -Verb RunAs"
                subprocess.run(["powershell", "-Command", ps_cmd], shell=True)
                logger.info("Запит на видалення надіслано через PowerShell.")

        except Exception as e:
            logger.error(f"Помилка під час очищення журналу: {e}")
