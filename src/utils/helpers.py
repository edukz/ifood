
import os
from datetime import datetime
from typing import List, Dict, Any
from src.config.settings import SETTINGS

def ensure_directories():
    """Garante que os diretórios necessários existam"""
    os.makedirs(SETTINGS.output_dir, exist_ok=True)
    os.makedirs(SETTINGS.log_dir, exist_ok=True)

def save_to_mysql(data: List[Dict[str, Any]], data_type: str = "restaurants", category: str = "Geral", city: str = "São Paulo"):
    """Salva dados no MySQL (substitui save_to_csv)"""
    if not data:
        return None
    
    from src.database.database_adapter import get_database_manager
    
    db_manager = get_database_manager()
    
    if data_type == "restaurants":
        result = db_manager.save_restaurants(data, category, city)
        return f"MySQL: {result.get('new', 0)} novos, {result.get('updated', 0)} atualizados"
    elif data_type == "categories":
        result = db_manager.save_categories(data, city)
        return f"MySQL: {result.get('new', 0)} novos, {result.get('updated', 0)} atualizados"
    elif data_type == "products":
        # Para produtos, precisa de restaurant_name e restaurant_id
        restaurant_name = data[0].get('restaurant_name', 'Unknown')
        restaurant_id = data[0].get('restaurant_id', 'unknown')
        result = db_manager.save_products(data, restaurant_name, restaurant_id)
        return f"MySQL: {result.get('new', 0)} novos, {result.get('updated', 0)} atualizados"
    else:
        raise ValueError(f"Tipo de dados não suportado: {data_type}")

# Função de compatibilidade - DEPRECADA
def save_to_csv(data: List[Dict[str, Any]], filename: str = None):
    """
    DEPRECADA: Use save_to_mysql() instead
    Esta função agora redireciona para MySQL
    """
    import warnings
    warnings.warn(
        "save_to_csv() está DEPRECADA. Use save_to_mysql() para salvar no banco de dados.",
        DeprecationWarning,
        stacklevel=2
    )
    
    return save_to_mysql(data, "restaurants")

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