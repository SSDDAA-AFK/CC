import logging
import sys

def setup_logger():
    logger = logging.getLogger("PrivacyCleaner")
    logger.setLevel(logging.INFO)
    
    # Консольний вивід
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

logger = setup_logger()
