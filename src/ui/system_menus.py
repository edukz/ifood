#!/usr/bin/env python3
"""
Menus de Sistema - Interface principal para funcionalidades do sistema
"""

import platform
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.scrapers.parallel.windows_parallel_scraper import WindowsParallelScraper, detect_windows
from src.utils.search_optimizer import SearchIndex, QueryOptimizer
from tools.archive_manager import ArchiveManager
from src.ui.base_menu import BaseMenu
from src.config.database import execute_query
from src.config.settings import SETTINGS

# Importar módulos especializados
from .menus.search_menus import SearchMenus
from .menus.parallel_menus import ParallelMenus
from .menus.reports_menus import ReportsMenus
from .menus.config_menus import ConfigMenus
from .menus.status_menus import StatusMenus
from .menus.archive_menus import ArchiveMenus

# Optional imports - sistema funciona sem eles
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    def tabulate(data, headers=None, **kwargs):
        """Fallback function for when tabulate is not available"""
        if not data:
            return "Nenhum dado disponível"
        
        result = []
        if headers:
            result.append("\t".join(str(h) for h in headers))
            result.append("-" * 50)
        
        for row in data:
            if isinstance(row, dict):
                result.append("\t".join(str(row.get(h, '')) for h in (headers or row.keys())))
            else:
                result.append("\t".join(str(cell) for cell in row))
        
        return "\n".join(result)

from src.database.database_adapter import get_database_manager


class SystemMenus(BaseMenu):
    """Interface principal para funcionalidades do sistema"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path,
                 search_optimizer: QueryOptimizer, archive_manager: ArchiveManager):
        super().__init__("Sistema", session_stats, data_dir)
        self.search_optimizer = search_optimizer
        self.archive_manager = archive_manager
        self.db = get_database_manager()
        
        # Inicializar módulos especializados
        self.search_menus = SearchMenus(session_stats, data_dir, search_optimizer)
        self.parallel_menus = ParallelMenus(session_stats, data_dir)
        self.reports_menus = ReportsMenus(session_stats, data_dir)
        self.config_menus = ConfigMenus(session_stats, data_dir)
        self.status_menus = StatusMenus(session_stats, data_dir)
        self.archive_menus = ArchiveMenus(session_stats, data_dir, archive_manager)
        
        # Import analysis components on demand
        self.product_categorizer = None
    
    def menu_system_main(self):
        """Menu principal do sistema"""
        options = [
            "1. 🔍 Sistema de busca",
            "2. 🚀 Execução paralela",
            "3. 📊 Relatórios e análises",
            "4. ⚙️ Configurações",
            "5. 📈 Status do sistema",
            "6. 📁 Gerenciamento de arquivos",
            "7. 🏷️ Status de categorias",
            "8. 🔧 Ferramentas avançadas"
        ]
        
        self.show_menu("🖥️ SISTEMA", options)
        choice = self.get_user_choice(8)
        
        if choice == "1":
            self.search_menus.menu_search_system()
        elif choice == "2":
            self.parallel_menus.menu_parallel_execution()
        elif choice == "3":
            self.reports_menus.menu_reports()
        elif choice == "4":
            self.config_menus.menu_system_config()
        elif choice == "5":
            self.status_menus.menu_system_status()
        elif choice == "6":
            self.archive_menus.menu_file_management()
        elif choice == "7":
            self.check_categories_status()
        elif choice == "8":
            self.menu_advanced_tools()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    # ================== STATUS DE CATEGORIAS ==================
    
    def check_categories_status(self):
        """Verifica o status das categorias no banco de dados"""
        try:
            self.show_section_header("📊 STATUS DAS CATEGORIAS")
            
            # 1. Contagem total de categorias
            total_categories = execute_query("SELECT COUNT(*) as total FROM categories WHERE is_active = TRUE", fetch_one=True)
            print(f"🏷️  Total de categorias ativas: {total_categories['total'] if total_categories else 0}")
            
            # 2. Categorias por cidade
            print("\n🌍 CATEGORIAS POR CIDADE:")
            city_stats = execute_query("""
                SELECT 
                    CASE 
                        WHEN url LIKE '%birigui%' THEN 'Birigui'
                        WHEN url LIKE '%aracatuba%' THEN 'Araçatuba'
                        WHEN url LIKE '%penapolis%' THEN 'Penápolis'
                        ELSE 'Outras'
                    END as cidade,
                    COUNT(*) as total
                FROM categories 
                WHERE is_active = TRUE
                GROUP BY cidade
                ORDER BY total DESC
            """, fetch_all=True)
            
            for city in city_stats or []:
                print(f"   • {city['cidade']}: {city['total']} categorias")
            
            # 3. Categorias recém adicionadas (últimas 24h)
            recent_categories = execute_query("""
                SELECT name, created_at 
                FROM categories 
                WHERE is_active = TRUE 
                  AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                ORDER BY created_at DESC
                LIMIT 10
            """, fetch_all=True)
            
            if recent_categories:
                print(f"\n🆕 CATEGORIAS ADICIONADAS (últimas 24h):")
                for cat in recent_categories:
                    created_time = cat['created_at'].strftime('%H:%M:%S')
                    print(f"   • {cat['name']} - {created_time}")
            else:
                print(f"\n🆕 Nenhuma categoria adicionada nas últimas 24h")
            
            # 4. Categorias mais populares (com mais restaurantes)
            print(f"\n🔥 CATEGORIAS MAIS POPULARES:")
            popular_categories = execute_query("""
                SELECT c.name, COUNT(r.id) as restaurant_count
                FROM categories c
                LEFT JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                WHERE c.is_active = TRUE
                GROUP BY c.id, c.name
                ORDER BY restaurant_count DESC
                LIMIT 10
            """, fetch_all=True)
            
            for cat in popular_categories or []:
                print(f"   • {cat['name']}: {cat['restaurant_count']} restaurantes")
            
            # 5. Análise de performance
            print(f"\n📈 ANÁLISE DE PERFORMANCE:")
            
            # Últimas extrações
            last_extractions = execute_query("""
                SELECT COUNT(*) as extracted_today
                FROM categories 
                WHERE is_active = TRUE 
                  AND created_at >= CURDATE()
            """, fetch_one=True)
            
            print(f"   • Categorias extraídas hoje: {last_extractions['extracted_today'] if last_extractions else 0}")
            
            # Taxa de sucesso (categorias com restaurantes)
            with_restaurants = execute_query("""
                SELECT COUNT(DISTINCT c.id) as count
                FROM categories c
                JOIN restaurants r ON r.category LIKE CONCAT('%', c.name, '%')
                WHERE c.is_active = TRUE
            """, fetch_one=True)
            
            total_active = total_categories['total'] if total_categories else 0
            success_rate = (with_restaurants['count'] / total_active * 100) if total_active > 0 else 0
            
            print(f"   • Taxa de sucesso: {success_rate:.1f}% ({with_restaurants['count']} com restaurantes)")
            
            # Categorias vazias
            empty_categories = total_active - with_restaurants['count']
            print(f"   • Categorias vazias: {empty_categories}")
            
            # 6. Recomendações
            print(f"\n💡 RECOMENDAÇÕES:")
            
            recommendations = []
            
            if empty_categories > 0:
                recommendations.append(f"🔧 Revisar {empty_categories} categorias sem restaurantes")
            
            if success_rate < 80:
                recommendations.append("🔄 Executar nova extração de restaurantes")
            
            if last_extractions['extracted_today'] == 0:
                recommendations.append("📊 Considerar extração de novas categorias")
            
            if recommendations:
                for rec in recommendations:
                    print(f"   • {rec}")
            else:
                print("   ✅ Sistema de categorias operando normalmente")
            
        except Exception as e:
            self.show_error(f"Erro ao verificar status das categorias: {e}")
        
        self.pause()
    
    # ================== FERRAMENTAS AVANÇADAS ==================
    
    def menu_advanced_tools(self):
        """Menu de ferramentas avançadas"""
        options = [
            "1. 🔧 Otimizador de consultas",
            "2. 📊 Análise de dados",
            "3. 🧪 Ferramentas de teste",
            "4. 🔄 Migração de dados",
            "5. 🛠️ Manutenção do sistema",
            "6. 📈 Monitoramento avançado",
            "7. 🔍 Debug e diagnóstico",
            "8. 🎯 Otimização de performance"
        ]
        
        self.show_menu("🔧 FERRAMENTAS AVANÇADAS", options)
        choice = self.get_user_choice(8)
        
        if choice == "1":
            self._query_optimizer()
        elif choice == "2":
            self._data_analysis()
        elif choice == "3":
            self._testing_tools()
        elif choice == "4":
            self._data_migration()
        elif choice == "5":
            self._system_maintenance()
        elif choice == "6":
            self._advanced_monitoring()
        elif choice == "7":
            self._debug_diagnostic()
        elif choice == "8":
            self._performance_optimization()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _query_optimizer(self):
        """Otimizador de consultas"""
        print("\n🔧 OTIMIZADOR DE CONSULTAS")
        print("═" * 50)
        
        try:
            # Usar o search_optimizer
            if self.search_optimizer:
                # Análise de índices
                print("📊 Analisando índices existentes...")
                
                with self.db.get_cursor() as (cursor, _):
                    # Verificar índices das tabelas principais
                    tables = ['restaurants', 'products', 'categories']
                    
                    for table in tables:
                        try:
                            cursor.execute(f"SHOW INDEX FROM {table}")
                            indexes = cursor.fetchall()
                            print(f"  {table}: {len(indexes)} índices")
                            
                            # Mostrar índices principais
                            for index in indexes[:3]:  # Mostrar apenas os 3 primeiros
                                print(f"    • {index.get('Key_name', 'N/A')} ({index.get('Column_name', 'N/A')})")
                        except Exception as e:
                            print(f"  {table}: Erro ao verificar índices - {e}")
                
                # Sugestões de otimização
                print(f"\n💡 SUGESTÕES DE OTIMIZAÇÃO:")
                print("  • Criar índice composto em restaurants(category, rating)")
                print("  • Otimizar consultas de busca por texto")
                print("  • Implementar cache para consultas frequentes")
                print("  • Considerar particionamento de tabelas grandes")
                
                # Executar otimizações
                optimize = input("\n🔧 Executar otimizações automáticas? (s/N): ").strip().lower()
                if optimize == 's':
                    print("⚠️  Funcionalidade em desenvolvimento")
                    print("💡 Use as opções do menu de configurações para otimizar o banco")
            else:
                print("❌ Search optimizer não disponível")
                
        except Exception as e:
            self.show_error(f"Erro no otimizador: {e}")
        
        self.pause()
    
    def _data_analysis(self):
        """Análise de dados"""
        print("\n📊 ANÁLISE DE DADOS")
        print("═" * 50)
        
        try:
            # Usar o reports_menus para análise
            print("🔄 Redirecionando para sistema de relatórios...")
            self.reports_menus.menu_reports()
            
        except Exception as e:
            self.show_error(f"Erro na análise: {e}")
        
        self.pause()
    
    def _testing_tools(self):
        """Ferramentas de teste"""
        print("\n🧪 FERRAMENTAS DE TESTE")
        print("═" * 50)
        
        test_options = [
            "1. 🔍 Testar conectividade",
            "2. 🧪 Testar scrapers",
            "3. 💾 Testar banco de dados",
            "4. 🌐 Testar rede",
            "5. 📊 Testar performance"
        ]
        
        self.show_menu("🧪 OPÇÕES DE TESTE", test_options)
        choice = self.get_user_choice(5)
        
        if choice == "1":
            self._test_connectivity()
        elif choice == "2":
            self._test_scrapers()
        elif choice == "3":
            self._test_database()
        elif choice == "4":
            self._test_network()
        elif choice == "5":
            self._test_performance()
        
        self.pause()
    
    def _test_connectivity(self):
        """Testar conectividade"""
        print("\n🔍 TESTE DE CONECTIVIDADE")
        
        # Usar o status_menus para teste
        print("🔄 Executando verificação de saúde...")
        self.status_menus._health_check()
    
    def _test_scrapers(self):
        """Testar scrapers"""
        print("\n🧪 TESTE DE SCRAPERS")
        
        # Usar o parallel_menus para teste
        print("🔄 Redirecionando para demonstração de performance...")
        self.parallel_menus._demo_performance()
    
    def _test_database(self):
        """Testar banco de dados"""
        print("\n💾 TESTE DE BANCO DE DADOS")
        
        # Usar o config_menus para teste
        print("🔄 Redirecionando para teste de conexão...")
        self.config_menus._test_connection()
    
    def _test_network(self):
        """Testar rede"""
        print("\n🌐 TESTE DE REDE")
        
        # Usar o config_menus para teste
        print("🔄 Redirecionando para teste de conectividade...")
        self.config_menus._test_connectivity()
    
    def _test_performance(self):
        """Testar performance"""
        print("\n📊 TESTE DE PERFORMANCE")
        
        # Usar o status_menus para teste
        print("🔄 Redirecionando para métricas de performance...")
        self.status_menus._performance_metrics()
    
    def _data_migration(self):
        """Migração de dados"""
        print("\n🔄 MIGRAÇÃO DE DADOS")
        print("═" * 50)
        
        print("⚠️  Funcionalidade em desenvolvimento")
        print("💡 Use as opções do menu de arquivos para migrar dados")
        print("🔄 Redirecionando para gerenciamento de arquivos...")
        
        self.archive_menus.menu_file_management()
    
    def _system_maintenance(self):
        """Manutenção do sistema"""
        print("\n🛠️ MANUTENÇÃO DO SISTEMA")
        print("═" * 50)
        
        maintenance_options = [
            "1. 🗑️ Limpeza de arquivos",
            "2. 🔧 Otimização do banco",
            "3. 📦 Compactação de dados",
            "4. 🔄 Verificação de integridade",
            "5. 💾 Backup automático"
        ]
        
        self.show_menu("🛠️ OPÇÕES DE MANUTENÇÃO", maintenance_options)
        choice = self.get_user_choice(5)
        
        if choice == "1":
            self.archive_menus._cleanup_files()
        elif choice == "2":
            self.config_menus._optimize_database()
        elif choice == "3":
            self.archive_menus._compress_files()
        elif choice == "4":
            self.status_menus._health_check()
        elif choice == "5":
            self.config_menus._backup_restore()
        
        self.pause()
    
    def _advanced_monitoring(self):
        """Monitoramento avançado"""
        print("\n📈 MONITORAMENTO AVANÇADO")
        print("═" * 50)
        
        # Usar o status_menus para monitoramento
        print("🔄 Redirecionando para dashboard em tempo real...")
        self.status_menus._realtime_dashboard()
    
    def _debug_diagnostic(self):
        """Debug e diagnóstico"""
        print("\n🔍 DEBUG E DIAGNÓSTICO")
        print("═" * 50)
        
        # Usar o status_menus para debug
        print("🔄 Redirecionando para análise de logs...")
        self.status_menus._logs_audit()
    
    def _performance_optimization(self):
        """Otimização de performance"""
        print("\n🎯 OTIMIZAÇÃO DE PERFORMANCE")
        print("═" * 50)
        
        # Usar o parallel_menus para otimização
        print("🔄 Redirecionando para configuração de workers...")
        self.parallel_menus._configure_workers()
    
    # ================== FUNÇÕES AUXILIARES ==================
    
    def show_section_header(self, title: str):
        """Mostra cabeçalho de seção"""
        print(f"\n{title}")
        print("═" * len(title))
    
    def show_subsection_header(self, title: str):
        """Mostra cabeçalho de subseção"""
        print(f"\n{title}")
        print("-" * len(title))
    
    def show_success(self, message: str):
        """Mostra mensagem de sucesso"""
        print(f"✅ {message}")
    
    def show_warning(self, message: str):
        """Mostra mensagem de aviso"""
        print(f"⚠️  {message}")
    
    def show_info(self, message: str):
        """Mostra mensagem de informação"""
        print(f"ℹ️  {message}")
    
    def format_file_size(self, size_bytes: int) -> str:
        """Formata tamanho de arquivo"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def format_time_ago(self, timestamp: datetime) -> str:
        """Formata tempo decorrido"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} dia{'s' if diff.days > 1 else ''} atrás"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hora{'s' if hours > 1 else ''} atrás"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minuto{'s' if minutes > 1 else ''} atrás"
        else:
            return "Agora mesmo"
    
    def confirm_action(self, message: str) -> bool:
        """Confirma uma ação"""
        response = input(f"⚠️  {message} (s/N): ").strip().lower()
        return response in ['s', 'sim', 'y', 'yes']
    
    def get_user_selection(self, items: List[str], prompt: str = "Escolha uma opção") -> int:
        """Obtém seleção do usuário de uma lista"""
        if not items:
            return -1
        
        print(f"\n{prompt}:")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item}")
        
        try:
            choice = int(input(f"\nEscolha [1-{len(items)}]: ").strip())
            if 1 <= choice <= len(items):
                return choice - 1
            else:
                return -1
        except ValueError:
            return -1
    
    def display_table(self, data: List[Dict], headers: List[str], max_rows: int = 20):
        """Exibe dados em formato de tabela"""
        if not data:
            print("Nenhum dado para exibir")
            return
        
        # Limitar número de linhas
        display_data = data[:max_rows]
        
        # Preparar dados para tabela
        table_data = []
        for row in display_data:
            table_row = []
            for header in headers:
                value = row.get(header, 'N/A')
                # Limitar tamanho do texto
                if isinstance(value, str) and len(value) > 30:
                    value = value[:27] + "..."
                table_row.append(value)
            table_data.append(table_row)
        
        # Exibir tabela
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Mostrar informação sobre dados ocultos
        if len(data) > max_rows:
            print(f"\n... e mais {len(data) - max_rows} registros")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do banco de dados"""
        try:
            with self.db.get_cursor() as (cursor, _):
                stats = {}
                
                # Contagem de tabelas
                cursor.execute("SELECT COUNT(*) as count FROM restaurants")
                stats['restaurants'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM products")
                stats['products'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM categories WHERE is_active = TRUE")
                stats['categories'] = cursor.fetchone()['count']
                
                return stats
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas do banco: {e}")
            return {'restaurants': 0, 'products': 0, 'categories': 0}
    
    def log_system_action(self, action: str, details: str = ""):
        """Registra ação do sistema"""
        try:
            self.logger.info(f"Sistema - {action}: {details}")
        except Exception:
            pass  # Falha silenciosa no log
    
    def cleanup_temporary_files(self):
        """Limpa arquivos temporários"""
        try:
            # Usar o archive_menus para limpeza
            self.archive_menus._remove_unnecessary_files()
        except Exception as e:
            self.logger.error(f"Erro na limpeza de arquivos temporários: {e}")
    
    def validate_system_health(self) -> bool:
        """Valida saúde do sistema"""
        try:
            # Verificar conexão com banco
            with self.db.get_cursor() as (cursor, _):
                cursor.execute("SELECT 1")
                
            # Verificar diretórios essenciais
            essential_dirs = [Path("data"), Path("logs"), Path("cache")]
            for dir_path in essential_dirs:
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            self.logger.error(f"Erro na validação de saúde: {e}")
            return False