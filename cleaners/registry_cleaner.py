import winreg
import subprocess
import os
from utils.logger import logger

class RegistryCleaner:
    def __init__(self):
        # Основні гілки для загального пошуку
        self.roots = [
            (winreg.HKEY_CURRENT_USER, r"Software"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software")
        ]
        
        # Специфічні шляхи, де часто залишаються сліди запусків
        self.priority_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"),
            
            # ShellBags - критично важливо для папок
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\BagMRU"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Bags"),
        ]

    def backup_key(self, root_str, key_path):
        """Робить бекап гілки реєстру."""
        safe_path = key_path.replace('\\', '_').replace(' ', '_')[:50]
        backup_file = f"backup_{safe_path}.reg"
        try:
            command = f'reg export "{root_str}\\{key_path}" "{backup_file}" /y'
            subprocess.run(command, shell=True, check=True, capture_output=True)
            return True
        except Exception:
            return False

    def delete_value(self, root, path, name):
        """Видаляє параметр."""
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteValue(key, name)
                return True
        except Exception as e:
            logger.error(f"Помилка видалення {name}: {e}")
            return False

    def clean(self, keywords):
        """Запуск очищення."""
        logger.info("Пошук у пріоритетних зонах (MuiCache, ShellBags та ін.)...")
        for root, path in self.priority_paths:
            root_str = "HKEY_CURRENT_USER" if root == winreg.HKEY_CURRENT_USER else "HKEY_LOCAL_MACHINE"
            self._recursive_scan(root, path, root_str, keywords)

        logger.info("Загальний пошук у гілках Software...")
        for root, base_path in self.roots:
            root_str = "HKEY_CURRENT_USER" if root == winreg.HKEY_CURRENT_USER else "HKEY_LOCAL_MACHINE"
            self._recursive_scan(root, base_path, root_str, keywords)
        
        logger.info("Очищення реєстру завершено.")

    def _recursive_scan(self, root, path, root_str, keywords):
        # Список виключень (гілки, які не треба чіпати)
        blacklist = [
            "Microsoft\\Windows NT\\CurrentVersion\\Perflib", # Тільки системні лічильники
            "Microsoft\\SystemCertificates",                 # Сертифікати
            "Microsoft\\Cryptography"                        # Ключі шифрування
        ]
        
        # Перевірка, чи не в чорному списку поточний шлях
        for item in blacklist:
            if item.lower() in path.lower():
                return

        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE | winreg.KEY_ENUMERATE_SUB_KEYS) as key:
                # Перевірка параметрів
                num_values = winreg.QueryInfoKey(key)[1]
                values_to_delete = []
                for i in range(num_values):
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        for word in keywords:
                            if word.lower() in str(name).lower() or word.lower() in str(value).lower():
                                logger.warning(f"ЗНАЙДЕНО: {root_str}\\{path} -> {name}")
                                values_to_delete.append(name)
                                break
                    except OSError: continue

                if values_to_delete:
                    # Для ShellBags робимо бекап і видаляємо все знайдене
                    self.backup_key(root_str, path)
                    for name in values_to_delete:
                        self.delete_value(root, path, name)

                # Рекурсія
                num_keys = winreg.QueryInfoKey(key)[0]
                for i in range(num_keys):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        new_path = f"{path}\\{sub_key_name}"
                        self._recursive_scan(root, new_path, root_str, keywords)
                    except OSError: continue
                    
        except FileNotFoundError: pass
        except PermissionError: pass
        except Exception: pass
