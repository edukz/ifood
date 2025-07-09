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
load_dotenv(override=True)

from src.utils.search_optimizer import QueryOptimizer
from src.utils.product_categorizer import ProductCategorizer
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
        
        # Verifica status do sistema na inicialização
        self._check_system_status()
        
        # Inicializa componentes principais
        self.search_optimizer = QueryOptimizer()
        self.archive_manager = ArchiveManager()
        self.product_categorizer = ProductCategorizer()
        
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
                                          self.product_categorizer)
        self.system_menus = SystemMenus(self.session_stats, self.data_dir,
                                       self.search_optimizer, self.archive_manager)
    
    def show_header(self):
        """Mostra cabeçalho do sistema"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("═" * 80)
        print("                    🍔 SISTEMA IFOOD SCRAPER 🍔")
        print("                      Sistema Integrado v2.0")
        print("═" * 80)
        
        # Mostra configurações atuais
        print(f"⚙️  Configurações: {SETTINGS.city} | {os.getenv('DB_NAME')} | {os.getenv('DB_USER')}")
        
        # Mostra estatísticas do banco de dados real
        db_stats = self._get_database_stats()
        uptime = datetime.now() - self.session_stats['session_start']
        print(f"📊 Sessão atual: {uptime.seconds//3600:02d}:{(uptime.seconds//60)%60:02d}:{uptime.seconds%60:02d}")
        print(f"📈 Dados no banco: {db_stats['categories']} categorias, "
              f"{db_stats['restaurants']} restaurantes, "
              f"{db_stats['products']} produtos")
        print(f"🔍 Sessão atual: {self.session_stats['products_categorized']} categorizados")
        print("═" * 80)
    
    def show_main_menu(self):
        """Mostra menu principal reorganizado"""
        print("\n🎯 MENU PRINCIPAL:")
        print("1. 🔧 Scrapy Unitário")
        print("2. 🚀 Execução Paralela")
        print("3. 🔍 Sistema de Busca")
        print("4. 🏪 Visualizar Restaurantes")
        print("5. 📊 Relatórios e Análises")
        print("6. ⚙️  Configurações")
        print("7. 📋 Status do Sistema")
        print("8. ℹ️  Informações do Sistema")
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
                    self.extraction_menus.menu_scrapy_unitario()
                elif choice == "2":
                    self.system_menus.parallel_menus.menu_parallel_execution()
                elif choice == "3":
                    self.system_menus.search_menus.menu_search_system()
                elif choice == "4":
                    self._view_restaurants_menu()
                elif choice == "5":
                    self.system_menus.reports_menus.menu_reports()
                elif choice == "6":
                    self.system_menus.config_menus.menu_system_config()
                elif choice == "7":
                    self.system_menus.status_menus.menu_system_status()
                elif choice == "8":
                    self._show_system_info()
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
    
    def _check_system_status(self):
        """Verifica status do sistema na inicialização"""
        try:
            from src.database.database_adapter import get_database_manager
            db = get_database_manager()
            self.db_status = True
            self.logger.info("Conexão com banco de dados estabelecida")
        except Exception as e:
            self.db_status = False
            self.logger.warning(f"Banco de dados não disponível: {e}")
    
    def _get_database_stats(self):
        """Obtém estatísticas reais do banco de dados"""
        try:
            from src.database.database_adapter import get_database_manager
            db = get_database_manager()
            
            # Consulta real ao banco de dados
            stats = db.get_statistics()
            return {
                'categories': stats.get('total_categories', 0),
                'restaurants': stats.get('total_restaurants', 0),
                'products': stats.get('total_products', 0)
            }
        except Exception as e:
            self.logger.warning(f"Erro ao obter estatísticas do banco: {e}")
            return {
                'categories': 0,
                'restaurants': 0,
                'products': 0
            }
    
    def _view_restaurants_menu(self):
        """Menu para visualizar restaurantes"""
        try:
            # Usar o sistema de busca para visualizar restaurantes
            self.system_menus.search_menus.menu_search_system()
        except Exception as e:
            self.logger.error(f"Erro ao acessar menu de restaurantes: {e}")
            print(f"❌ Erro ao acessar menu de restaurantes: {e}")
            input("\nPressione Enter para continuar...")
    
    def _show_system_info(self):
        """Mostra informações detalhadas do sistema"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("═" * 80)
        print("                    ℹ️  INFORMAÇÕES DO SISTEMA")
        print("═" * 80)
        
        # Status do Sistema
        print("\n📊 STATUS DO SISTEMA:")
        print(f"  ✅ Versão: 2.0")
        print(f"  ✅ Cidade configurada: {SETTINGS.city}")
        print(f"  ✅ Banco de dados: {os.getenv('DB_NAME')}")
        print(f"  ✅ Usuário MySQL: {os.getenv('DB_USER')}")
        print(f"  ✅ Modo headless: {SETTINGS.headless}")
        print(f"  ✅ Diretório de saída: {SETTINGS.output_dir}")
        
        # Scrapers Disponíveis
        print("\n🔧 SCRAPERS ATIVOS (4):")
        print("  ✅ CategoryScraper - Extrai categorias de comida")
        print("  ✅ RestaurantScraper - Extrai dados dos restaurantes")
        print("  ✅ ProductScraper - Extrai cardápios e produtos")
        print("  ✅ WindowsParallelScraper - Execução paralela otimizada")
        
        # Funcionalidades
        print("\n🚀 FUNCIONALIDADES PRINCIPAIS:")
        print("  1️⃣ Scrapy Unitário (categorias, restaurantes, produtos)")
        print("  2️⃣ Processamento paralelo para múltiplas categorias")
        print("  3️⃣ Sistema de busca integrado")
        print("  4️⃣ Visualização de dados extraídos")
        print("  5️⃣ Relatórios e análises")
        print("  6️⃣ Configurações avançadas")
        print("  7️⃣ Status e monitoramento")
        print("  8️⃣ Informações do sistema")
        
        # Banco de Dados
        print("\n🗄️ ESTRUTURA DO BANCO DE DADOS:")
        print("  📋 8 tabelas principais:")
        print("     • categories - Categorias de comida")
        print("     • restaurants - Dados dos restaurantes")
        print("     • products - Cardápios e produtos")
        print("     • price_history - Histórico de preços")
        print("     • restaurant_details - Informações extras")
        print("     • reviews - Avaliações de clientes")
        print("     • extraction_logs - Logs de extração")
        print("     • system_config - Configurações do sistema")
        
        # Status da Conexão
        if hasattr(self, 'db_status') and self.db_status:
            print("\n✅ CONEXÃO COM BANCO: ATIVA")
            try:
                from src.database.database_adapter import get_database_manager
                db = get_database_manager()
                stats = db.get_statistics()
                print(f"  📊 Categorias cadastradas: {stats['total_categories']}")
                print(f"  📊 Restaurantes cadastrados: {stats['total_restaurants']}")
                print(f"  📊 Produtos cadastrados: {stats['total_products']}")
            except:
                pass
        else:
            print("\n❌ CONEXÃO COM BANCO: INATIVA")
        
        # Instruções de Uso
        print("\n📖 FLUXO RECOMENDADO:")
        print("  1. Usar Scrapy Unitário (opção 1) para extrair:")
        print("     • 1.1 - Categorias")
        print("     • 1.2 - Restaurantes de categorias escolhidas")
        print("     • 1.3 - Produtos dos restaurantes")
        print("  2. Usar execução paralela (opção 2) para processar múltiplas categorias")
        
        # Melhorias Recentes
        print("\n🆕 MELHORIAS RECENTES:")
        print("  ✅ Sistema otimizado - removidos scrapers não utilizados")
        print("  ✅ Banco MySQL configurado - ifood_scraper_v3")
        print("  ✅ Configurações via arquivo .env")
        print("  ✅ Sistema de logs melhorado")
        print("  ✅ Tratamento de erros aprimorado")
        
        print("\n" + "═" * 80)
        input("\nPressione Enter para voltar ao menu principal...")

def main():
    """Função principal"""
    system = iFoodMenuSystem()
    system.run()

if __name__ == "__main__":
    main()