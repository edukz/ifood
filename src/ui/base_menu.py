#!/usr/bin/env python3
"""
Base Menu System - Funcionalidades comuns de menu
"""

import os
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.utils.logger import setup_logger
from src.config.settings import SETTINGS


class BaseMenu:
    """Classe base para todos os menus"""
    
    def __init__(self, title: str, session_stats: Dict[str, Any], data_dir: Path):
        self.title = title
        self.session_stats = session_stats
        self.data_dir = data_dir
        self.logger = setup_logger(self.__class__.__name__)
    
    def show_header(self):
        """Mostra cabeçalho do sistema"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("═" * 80)
        print("                    🍔 SISTEMA IFOOD SCRAPER 🍔")
        print("                      Sistema Integrado v2.0")
        print("═" * 80)
        
        # Mostra estatísticas da sessão
        uptime = datetime.now() - self.session_stats['session_start']
        print(f"📊 Sessão atual: {uptime.seconds//3600:02d}:{(uptime.seconds//60)%60:02d}:{uptime.seconds%60:02d}")
        print(f"📈 Extrações: {self.session_stats['categories_extracted']} categorias, "
              f"{self.session_stats['restaurants_extracted']} restaurantes, "
              f"{self.session_stats['products_extracted']} produtos")
        print(f"🔍 Análises: {self.session_stats['products_categorized']} categorizados, "
              f"{self.session_stats['prices_monitored']} preços monitorados")
        print("═" * 80)
    
    def show_menu(self, title: str, options: List[str]):
        """Mostra menu genérico"""
        print(f"\n{title}")
        print("═" * 50)
        for option in options:
            print(option)
        print("0. 🔙 Voltar")
    
    def get_user_choice(self, max_option: int) -> str:
        """Obtém escolha do usuário"""
        return input("\nEscolha: ").strip()
    
    def show_invalid_option(self):
        """Mostra mensagem de opção inválida"""
        print("❌ Opção inválida!")
        self.pause()
    
    def pause(self, message: str = "\nPressione Enter para continuar..."):
        """Pausa para o usuário"""
        input(message)
    
    def load_categories_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Carrega categorias de arquivo CSV"""
        categories = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    categories.append(row)
        except Exception as e:
            self.logger.error(f"Erro ao carregar categorias: {e}")
        
        return categories
    
    def count_files(self, directory: str) -> int:
        """Conta arquivos em um diretório"""
        dir_path = self.data_dir / directory
        if not dir_path.exists():
            return 0
        return len(list(dir_path.glob("*.csv")))
    
    def get_total_size(self) -> int:
        """Calcula tamanho total dos dados"""
        total = 0
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                try:
                    total += os.path.getsize(os.path.join(root, file))
                except:
                    pass
        return total
    
    def format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def find_file(self, file_path: str, search_dirs: List[str] = None) -> Optional[Path]:
        """Procura arquivo em diretórios específicos"""
        path = Path(file_path)
        
        # Se caminho absoluto existe
        if path.exists():
            return path
        
        # Procura em diretórios específicos
        if search_dirs:
            for search_dir in search_dirs:
                search_path = self.data_dir / search_dir / file_path
                if search_path.exists():
                    return search_path
        
        return None
    
    def show_error(self, message: str):
        """Mostra mensagem de erro"""
        print(f"❌ Erro: {message}")
        self.pause()
    
    def show_success(self, message: str):
        """Mostra mensagem de sucesso"""
        print(f"✅ {message}")
    
    def show_warning(self, message: str):
        """Mostra mensagem de aviso"""
        print(f"⚠️ {message}")
    
    def show_info(self, message: str):
        """Mostra mensagem informativa"""
        print(f"ℹ️ {message}")