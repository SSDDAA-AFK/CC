import sys
from utils.logger import logger
from cleaners.chrome_cleaner import ChromeCleaner
from cleaners.registry_cleaner import RegistryCleaner
from cleaners.journal_cleaner import JournalCleaner

def main():
    print("========================================")
    print("      Privacy Cleaner v1.1              ")
    print("========================================")
    
    # 1. Запит слів для очищення Chrome та Реєстру
    input_str = input("Введіть слова для видалення (через кому): ").strip()
    if not input_str:
        logger.error("Слова не введені.")
        keywords = []
    else:
        keywords = [w.strip() for w in input_str.split(',') if w.strip()]
    
    # 2. Запит про очищення USN Journal
    clean_journal_confirm = input("Очистити USN Journal? (y/n): ").lower()
    
    if not keywords and clean_journal_confirm != 'y':
        logger.info("Нічого не вибрано для очищення. Вихід.")
        return

    print("\n--- Починаємо роботу ---")

    # Крок А: Chrome
    if keywords:
        logger.info("Крок 1: Очищення Google Chrome")
        chrome = ChromeCleaner()
        chrome.clean(keywords)
    
    # Крок Б: Реєстр
    if keywords:
        logger.info("Крок 2: Очищення Реєстру Windows")
        reg = RegistryCleaner()
        reg.clean(keywords)
    
    # Крок В: USN Journal
    if clean_journal_confirm == 'y':
        logger.info("Крок 3: Очищення USN Journal")
        journal = JournalCleaner()
        journal.clean()
    
    print("\n========================================")
    print("Очищення завершено. Перевірте лог вище.")
    print("========================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПерервано користувачем.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Непередбачена помилка: {e}")
