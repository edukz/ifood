#!/usr/bin/env python3
"""
Sistema iFood Scraper - Menu Principal Modular
Interface unificada para todas as funcionalidades
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Classe simples para substituir ParallelScraper
class SimpleScraperConfig:
    """Configuração simples para substituir ParallelScraper"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
from src.utils.search_optimizer import QueryOptimizer
from src.utils.product_categorizer import ProductCategorizer
from src.utils.price_monitor import PriceMonitor
from tools.archive_manager import ArchiveManager
from src.utils.logger import setup_logger
from src.config.settings import SETTINGS

# Imports dos módulos de menu
from src.ui.extraction_menus import ExtractionMenus
from src.ui.analysis_menus import AnalysisMenus
from src.ui.system_menus import SystemMenus

class iFoodMenuSystem:
    """Sistema de menu principal integrado e modular"""
    
    def __init__(self):
        self.logger = setup_logger("iFoodMenu")
        self.data_dir = Path(SETTINGS.output_dir)
        
        # Inicializa componentes principais
        # Substituído ParallelScraper por configuração simples
        self.parallel_scraper = SimpleScraperConfig(max_workers=3)
        self.search_optimizer = QueryOptimizer()
        self.archive_manager = ArchiveManager()
        self.product_categorizer = ProductCategorizer()
        self.price_monitor = PriceMonitor()
        
        # Estatísticas da sessão
        self.session_stats = {
            'categories_extracted': 0,
            'restaurants_extracted': 0,
            'products_extracted': 0,
            'files_compressed': 0,
            'searches_performed': 0,
            'products_categorized': 0,
            'prices_monitored': 0,
            'session_start': datetime.now()
        }
        
        # Inicializa módulos de menu
        self.extraction_menus = ExtractionMenus(self.session_stats, self.data_dir)
        self.analysis_menus = AnalysisMenus(self.session_stats, self.data_dir, 
                                          self.product_categorizer, self.price_monitor)
        self.system_menus = SystemMenus(self.session_stats, self.data_dir,
                                       self.parallel_scraper, self.search_optimizer,
                                       self.archive_manager)
    
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
    
    def show_main_menu(self):
        """Mostra menu principal reorganizado"""
        print("\n🎯 MENU PRINCIPAL:")
        print("1. 🏷️  Extrair Categorias")
        print("2. 🏪 Extrair Restaurantes")
        print("3. 🍕 Extrair Produtos")
        print("4. 🚀 Execução Paralela")
        print("5. 🔍 Sistema de Busca")
        print("6. 🏪 Visualizar Restaurantes")
        print("7. 📊 Relatórios e Análises")
        print("8. ⚙️  Configurações")
        print("9. 📋 Status do Sistema")
        print("0. 🚪 Sair")
        print("═" * 80)
    
    def run(self):
        """Executa o sistema principal"""
        try:
            self.logger.info("Iniciando sistema iFood Scraper")
            
            while True:
                self.show_header()
                self.show_main_menu()
                
                choice = input("\nEscolha: ").strip()
                
                if choice == "1":
                    self.extraction_menus.menu_extract_categories()
                elif choice == "2":
                    self.extraction_menus.menu_extract_restaurants()
                elif choice == "3":
                    self.extraction_menus.menu_extract_products()
                elif choice == "4":
                    self.system_menus.menu_parallel_execution()
                elif choice == "5":
                    self.system_menus.menu_search_system()
                elif choice == "6":
                    self.system_menus.view_restaurants_menu()
                elif choice == "7":
                    self.system_menus.menu_reports_and_analytics()
                elif choice == "8":
                    self.system_menus.menu_settings_expanded()
                elif choice == "9":
                    self.system_menus.menu_system_status_consolidated()
                elif choice == "0":
                    self._shutdown()
                    break
                else:
                    print("❌ Opção inválida!")
                    input("\nPressione Enter para continuar...")
                    
        except KeyboardInterrupt:
            self._shutdown()
        except Exception as e:
            self.logger.error(f"Erro no sistema: {e}")
            print(f"❌ Erro inesperado: {e}")
            input("\nPressione Enter para continuar...")
    
    def _shutdown(self):
        """Encerra o sistema"""
        print("\n🔄 Encerrando sistema...")
        
        # Mostra estatísticas finais
        uptime = datetime.now() - self.session_stats['session_start']
        print(f"\n📊 Estatísticas da sessão:")
        print(f"  ⏱️  Tempo ativo: {uptime.seconds//3600:02d}:{(uptime.seconds//60)%60:02d}:{uptime.seconds%60:02d}")
        print(f"  🎯 Total de extrações: {sum([
            self.session_stats['categories_extracted'],
            self.session_stats['restaurants_extracted'],
            self.session_stats['products_extracted']
        ])}")
        print(f"  🔍 Análises realizadas: {self.session_stats['products_categorized']} + {self.session_stats['prices_monitored']}")
        
        self.logger.info("Sistema encerrado")
        print("\n✅ Sistema encerrado com sucesso!")
        print("🍔 Obrigado por usar o iFood Scraper!")

def main():
    """Função principal"""
    system = iFoodMenuSystem()
    system.run()

if __name__ == "__main__":
    main()