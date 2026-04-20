import winreg
import subprocess
import os
from utils.logger import logger

class RegistryCleaner:
    def __init__(self):
        self.roots = [
            (winreg.HKEY_CURRENT_USER, r"Software"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software")
        ]

    def backup_key(self, root_str, key_path):
        """Робить бекап гілки реєстру."""
        # Спрощуємо назву файлу для бекапу
        safe_path = key_path.replace('\\', '_').replace(' ', '_')[:50]
        backup_file = f"backup_{safe_path}.reg"
        try:
            command = f'reg export "{root_str}\\{key_path}" "{backup_file}" /y'
            subprocess.run(command, shell=True, check=True, capture_output=True)
            logger.info(f"Створено бекап: {backup_file}")
            return True
        except Exception:
            # Якщо шлях занадто довгий або інша помилка
            return False

    def delete_value(self, root, path, name):
        """Видаляє конкретний параметр."""
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteValue(key, name)
                return True
        except Exception as e:
            logger.error(f"Не вдалося видалити параметр {name}: {e}")
            return False

    def clean(self, keywords):
        """Запуск пошуку та видалення."""
        logger.info("Пошук та очищення реєстру розпочато...")
        for root, base_path in self.roots:
            root_str = "HKEY_CURRENT_USER" if root == winreg.HKEY_CURRENT_USER else "HKEY_LOCAL_MACHINE"
            self._recursive_scan(root, base_path, root_str, keywords)
        logger.info("Очищення реєстру завершено.")

    def _recursive_scan(self, root, path, root_str, keywords):
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE | winreg.KEY_ENUMERATE_SUB_KEYS) as key:
                # Перевірка параметрів (values)
                num_values = winreg.QueryInfoKey(key)[1]
                values_to_delete = []
                for i in range(num_values):
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        for word in keywords:
                            if word.lower() in str(name).lower() or word.lower() in str(value).lower():
                                logger.warning(f"Знайдено згадку '{word}' у {root_str}\\{path} -> {name}")
                                values_to_delete.append(name)
                                break
                    except OSError: continue

                if values_to_delete:
                    # Робимо один бекап на весь ключ перед видаленням його параметрів
                    self.backup_key(root_str, path)
                    for name in values_to_delete:
                        self.delete_value(root, path, name)

                # Рекурсія по підключам (keys)
                num_keys = winreg.QueryInfoKey(key)[0]
                for i in range(num_keys):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        new_path = f"{path}\\{sub_key_name}"
                        # Якщо саме ім'я ключа містить слово - виводимо попередження
                        # (Видалення цілих гілок реєстру дуже небезпечне, тому ми видаляємо тільки параметри)
                        for word in keywords:
                            if word.lower() in sub_key_name.lower():
                                logger.warning(f"КЛЮЧ містить '{word}': {root_str}\\{new_path}")
                        
                        self._recursive_scan(root, new_path, root_str, keywords)
                    except OSError: continue
                    
        except PermissionError: pass
        except Exception: pass
