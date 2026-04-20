import sys
import os
import glob
from utils.logger import logger
from cleaners.chrome_cleaner import ChromeCleaner
from cleaners.registry_cleaner import RegistryCleaner
from cleaners.journal_cleaner import JournalCleaner
from cleaners.system_cleaner import SystemCleaner

def self_clean():
    """Видаляє бекапи та згадки про саму програму."""
    logger.info("\n--- Запуск самоочищення ---")
    
    # 1. Назва цього файлу/процесу
    current_exe = os.path.basename(sys.executable)
    current_script = os.path.basename(__file__)
    # Використовуємо довгі назви, щоб уникнути конфліктів як з 'CC'
    my_names = [current_exe, current_script, "SchutzstaffelCleaner", "Schutzstaffel"]
    
    # 2. Видалення бекапів (.reg файлів)
    backups = glob.glob("backup_*.reg")
    for b in backups:
        try:
            os.remove(b)
            logger.info(f"Видалено файл бекапу: {b}")
        except: pass

    # 3. Видалення згадок про себе з реєстру та Prefetch
    reg = RegistryCleaner()
    sys_clean = SystemCleaner()
    
    logger.info("Видалення згадок про саму утиліту...")
    reg.clean(my_names)
    sys_clean.clean_prefetch(my_names)
    
    logger.info("Самоочищення завершено. Програма закриється через 3 секунди...")

def main():
    print("========================================")
    print("      Schutzstaffel Cleaner v2.1        ")
    print("========================================")
    
    input_str = input("Введіть слова для видалення (через кому): ").strip()
    keywords = [w.strip() for w in input_str.split(',') if w.strip()] if input_str else []
    
    clean_journal_confirm = input("Очистити USN Journal? (y/n): ").lower()
    
    if not keywords and clean_journal_confirm != 'y':
        logger.info("Нічого не вибрано. Вихід.")
        return

    print("\n--- Починаємо глибоке очищення ---")

    # Створюємо екземпляри
    chrome = ChromeCleaner()
    reg = RegistryCleaner()
    journal = JournalCleaner()
    sys_clean = SystemCleaner()

    # 1. Браузери
    if keywords:
        chrome.clean(keywords)
    
    # 2. Системні файли (Recent, PS, Prefetch, CFG)
    sys_clean.clean_local_cfgs() # Видаляємо всі .cfg у корені LocalAppData
    if keywords:
        sys_clean.clean_recent_and_ps(keywords)
        sys_clean.clean_prefetch(keywords)
    
    # 3. Реєстр (включаючи ShellBags)
    if keywords:
        reg.clean(keywords)
    
    # 4. USN Journal
    if clean_journal_confirm == 'y':
        journal.clean()
    
    print("\n========================================")
    print("Основне очищення завершено.")
    
    confirm_self = input("\nБажаєте провести САМООЧИЩЕННЯ (видалити бекапи та сліди цієї програми)? (y/n): ").lower()
    if confirm_self == 'y':
        self_clean()
    
    print("До побачення!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПерервано користувачем.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Помилка: {e}")
