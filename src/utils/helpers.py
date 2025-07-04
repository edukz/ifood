import os
import csv
from datetime import datetime
from typing import List, Dict, Any
from src.config.settings import SETTINGS


def ensure_directories():
    """Garante que os diretórios necessários existam"""
    os.makedirs(SETTINGS.output_dir, exist_ok=True)
    os.makedirs(SETTINGS.log_dir, exist_ok=True)


def save_to_csv(data: List[Dict[str, Any]], filename: str = None):
    """Salva dados em arquivo CSV"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{SETTINGS.output_dir}/restaurants_{timestamp}.csv"
    
    if not data:
        return
    
    keys = data[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    return filename


def wait_and_retry(func, max_attempts: int = 3, delay: int = 2):
    """Decorator para retry com delay"""
    import time
    
    def wrapper(*args, **kwargs):
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(delay)
    
    return wrapper