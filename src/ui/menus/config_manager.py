#!/usr/bin/env python3
"""
Configuration Manager - Main orchestrator for all configuration modules
"""

from typing import Dict, Any
from pathlib import Path

from .config.database_config import DatabaseConfig
from .config.network_config import NetworkConfig
from .config.file_config import FileConfig
from .config.scraping_config import ScrapingConfig
from .config.system_config import SystemConfig
from .config.backup_config import BackupConfig
from src.ui.base_menu import BaseMenu


class ConfigManager(BaseMenu):
    """Main configuration manager that orchestrates all configuration modules"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Configuração", session_stats, data_dir)
        self.data_dir = data_dir
        
        # Initialize all configuration modules
        self.database_config = DatabaseConfig(session_stats, data_dir)
        self.network_config = NetworkConfig(session_stats, data_dir)
        self.file_config = FileConfig(session_stats, data_dir)
        self.scraping_config = ScrapingConfig(session_stats, data_dir)
        self.system_config = SystemConfig(session_stats, data_dir)
        self.backup_config = BackupConfig(session_stats, data_dir)
        
        # Module mapping for easy access
        self.modules = {
            'database': self.database_config,
            'network': self.network_config,
            'file': self.file_config,
            'scraping': self.scraping_config,
            'system': self.system_config,
            'backup': self.backup_config
        }
    
    def menu_system_config(self):
        """Main configuration menu - entry point for all configuration modules"""
        options = [
            "1. 🔧 Configurações do banco de dados",
            "2. 🌐 Configurações de rede",
            "3. 📁 Configurações de arquivos",
            "4. 🕷️ Configurações de scraping",
            "5. ⚙️ Configurações do sistema",
            "6. 💾 Backup e manutenção",
            "7. 📊 Relatório de configurações",
            "8. 🔄 Resetar todas as configurações"
        ]
        
        self.show_menu("🔧 CONFIGURAÇÕES DO SISTEMA", options)
        choice = self.get_user_choice(8)
        
        if choice == "1":
            self.database_config.show_database_menu()
        elif choice == "2":
            self.network_config.show_network_menu()
        elif choice == "3":
            self.file_config.show_file_menu()
        elif choice == "4":
            self.scraping_config.show_scraping_menu()
        elif choice == "5":
            self.system_config.show_system_menu()
        elif choice == "6":
            self.backup_config.show_backup_menu()
        elif choice == "7":
            self._show_configuration_report()
        elif choice == "8":
            self._reset_all_configurations()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _show_configuration_report(self):
        """Show comprehensive configuration report"""
        print("\n📊 RELATÓRIO DE CONFIGURAÇÕES")
        print("═" * 40)
        
        try:
            # Gather statistics from all modules
            stats = {
                'database': self.database_config.get_database_statistics(),
                'network': self.network_config.get_network_statistics(),
                'file': self.file_config.get_file_statistics(),
                'scraping': self.scraping_config.get_scraping_statistics(),
                'system': self.system_config.get_system_statistics(),
                'backup': self.backup_config.get_backup_statistics()
            }
            
            # Database summary
            db_stats = stats['database']
            print("🔧 Banco de Dados:")
            print(f"  Conexão: {'✅ OK' if db_stats.get('connection_available', False) else '❌ Falha'}")
            if db_stats.get('database_size_mb', 0) > 0:
                print(f"  Tamanho: {db_stats['database_size_mb']:.1f} MB")
                print(f"  Tabelas: {db_stats.get('table_count', 0)}")
            
            # Network summary
            net_stats = stats['network']
            print("\n🌐 Rede:")
            print(f"  Conectividade: {'✅ OK' if net_stats.get('internet_connectivity', False) else '❌ Falha'}")
            print(f"  Proxy: {'✅ Configurado' if net_stats.get('proxy_configured', False) else '❌ Não configurado'}")
            print(f"  Timeout: {net_stats.get('timeout_configured', 30)}s")
            
            # File summary
            file_stats = stats['file']
            print("\n📁 Arquivos:")
            print(f"  Formato: {file_stats.get('file_format', 'json').upper()}")
            print(f"  Auto-backup: {'✅ Ativado' if file_stats.get('auto_backup_enabled', False) else '❌ Desativado'}")
            print(f"  Auto-limpeza: {'✅ Ativado' if file_stats.get('auto_cleanup_enabled', False) else '❌ Desativado'}")
            
            # Storage usage
            total_storage = 0
            for key in ['data_size_bytes', 'backups_size_bytes', 'logs_size_bytes', 'cache_size_bytes']:
                total_storage += file_stats.get(key, 0)
            
            if total_storage > 0:
                print(f"  Armazenamento total: {self._format_size(total_storage)}")
            
            # Scraping summary
            scraping_stats = stats['scraping']
            print("\n🕷️ Scraping:")
            print(f"  Workers: {scraping_stats.get('max_workers', 3)}")
            print(f"  Modo: {'Headless' if scraping_stats.get('headless_mode', True) else 'Visual'}")
            print(f"  Navegador: {scraping_stats.get('browser_type', 'chromium').title()}")
            print(f"  Debug: {'✅ Ativado' if scraping_stats.get('debug_mode', False) else '❌ Desativado'}")
            
            # System summary
            system_stats = stats['system']
            print("\n⚙️ Sistema:")
            print(f"  Log level: {system_stats.get('log_level', 'INFO')}")
            print(f"  Cache: {'✅ Ativado' if system_stats.get('cache_enabled', True) else '❌ Desativado'}")
            print(f"  Segurança: {'✅ Ativada' if system_stats.get('security_enabled', True) else '❌ Desativada'}")
            print(f"  Monitoramento: {'✅ Ativado' if system_stats.get('monitoring_enabled', False) else '❌ Desativado'}")
            
            # Backup summary
            backup_stats = stats['backup']
            print("\n💾 Backup:")
            print(f"  Auto-backup: {'✅ Ativado' if backup_stats.get('auto_backup_enabled', True) else '❌ Desativado'}")
            print(f"  Backups disponíveis: {backup_stats.get('backup_count', 0)}")
            if backup_stats.get('backup_total_size', 0) > 0:
                print(f"  Tamanho total: {self._format_size(backup_stats['backup_total_size'])}")
            
            # Overall health
            health_issues = []
            
            if not db_stats.get('connection_available', False):
                health_issues.append("Conexão com banco de dados")
            
            if not net_stats.get('internet_connectivity', False):
                health_issues.append("Conectividade com internet")
            
            if not file_stats.get('config_file_exists', False):
                health_issues.append("Arquivo de configuração ausente")
            
            if not backup_stats.get('backup_directory_exists', False):
                health_issues.append("Diretório de backup ausente")
            
            print("\n🏥 Saúde do Sistema:")
            if health_issues:
                print(f"  ⚠️ {len(health_issues)} problema(s) detectado(s):")
                for issue in health_issues:
                    print(f"    - {issue}")
            else:
                print("  ✅ Sistema saudável!")
            
            # Save detailed report
            save_report = self._validate_boolean_input("\n💾 Salvar relatório detalhado? (s/n): ")
            if save_report:
                self._save_detailed_report(stats)
            
        except Exception as e:
            self.show_error(f"Erro ao gerar relatório: {e}")
    
    def _save_detailed_report(self, stats: Dict[str, Any]):
        """Save detailed configuration report to file"""
        try:
            from datetime import datetime
            import json
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"config_report_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "system_info": {
                    "session_stats": self.session_stats,
                    "data_directory": str(self.data_dir)
                },
                "module_statistics": stats,
                "summary": {
                    "total_modules": len(self.modules),
                    "modules_loaded": len([m for m in self.modules.values() if m is not None])
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.show_success(f"Relatório salvo: {report_file}")
            
        except Exception as e:
            self.show_error(f"Erro ao salvar relatório: {e}")
    
    def _reset_all_configurations(self):
        """Reset all configurations to defaults"""
        print("\n🔄 RESETAR TODAS AS CONFIGURAÇÕES")
        print("═" * 45)
        
        self.show_warning("⚠️ ATENÇÃO: Esta operação irá resetar TODAS as configurações!")
        self.show_warning("⚠️ Todas as configurações personalizadas serão perdidas!")
        
        # Create backup before reset
        create_backup = self._validate_boolean_input("\n💾 Criar backup completo antes de resetar? (s/n): ")
        if create_backup:
            try:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backup_config._perform_backup("full", f"before_full_reset_{timestamp}", True)
                if backup_path:
                    self.show_success(f"Backup criado: {backup_path}")
                else:
                    self.show_error("Falha ao criar backup")
                    return
            except Exception as e:
                self.show_error(f"Erro ao criar backup: {e}")
                return
        
        # Final confirmation
        if not self._confirm_action("RESETAR TODAS AS CONFIGURAÇÕES (IRREVERSÍVEL)"):
            return
        
        try:
            # Reset each module
            reset_results = {}
            
            print("\n🔄 Resetando configurações...")
            
            # Database configuration
            print("  🔧 Resetando banco de dados...")
            try:
                self.database_config._update_env_file("DB_HOST", "localhost")
                self.database_config._update_env_file("DB_PORT", "3306")
                self.database_config._update_env_file("DB_NAME", "ifood_scraper_v3")
                self.database_config._update_env_file("DB_USER", "root")
                self.database_config._update_env_file("DB_POOL_SIZE", "5")
                reset_results['database'] = True
                print("    ✅ Banco de dados resetado")
            except Exception as e:
                reset_results['database'] = False
                print(f"    ❌ Erro: {e}")
            
            # Network configuration
            print("  🌐 Resetando rede...")
            try:
                self.network_config._update_settings("HTTP_TIMEOUT", 30)
                self.network_config._update_settings("USER_AGENT", "iFoodScraper/1.0")
                self.network_config._update_settings("MIN_DELAY", 1.0)
                self.network_config._update_settings("MAX_DELAY", 3.0)
                self.network_config._update_env_file("HTTP_PROXY", "")
                self.network_config._update_env_file("HTTPS_PROXY", "")
                reset_results['network'] = True
                print("    ✅ Rede resetada")
            except Exception as e:
                reset_results['network'] = False
                print(f"    ❌ Erro: {e}")
            
            # File configuration
            print("  📁 Resetando arquivos...")
            try:
                self.file_config._update_settings("DATA_DIR", "data")
                self.file_config._update_settings("BACKUP_DIR", "backups")
                self.file_config._update_settings("LOGS_DIR", "logs")
                self.file_config._update_settings("CACHE_DIR", "cache")
                self.file_config._update_settings("FILE_FORMAT", "json")
                self.file_config._update_settings("AUTO_BACKUP", True)
                self.file_config._update_settings("AUTO_CLEANUP", True)
                reset_results['file'] = True
                print("    ✅ Arquivos resetados")
            except Exception as e:
                reset_results['file'] = False
                print(f"    ❌ Erro: {e}")
            
            # Scraping configuration
            print("  🕷️ Resetando scraping...")
            try:
                self.scraping_config._update_settings("MAX_WORKERS", 3)
                self.scraping_config._update_settings("MAX_RETRIES", 3)
                self.scraping_config._update_settings("HEADLESS_MODE", True)
                self.scraping_config._update_settings("BROWSER_TYPE", "chromium")
                self.scraping_config._update_settings("DEBUG_MODE", False)
                self.scraping_config._update_settings("COLLECT_METRICS", True)
                reset_results['scraping'] = True
                print("    ✅ Scraping resetado")
            except Exception as e:
                reset_results['scraping'] = False
                print(f"    ❌ Erro: {e}")
            
            # System configuration
            print("  ⚙️ Resetando sistema...")
            try:
                self.system_config._update_settings("LOG_LEVEL", "INFO")
                self.system_config._update_settings("CACHE_ENABLED", True)
                self.system_config._update_settings("SECURITY_ENABLED", True)
                self.system_config._update_settings("MONITORING_ENABLED", False)
                self.system_config._update_settings("WEBHOOKS_ENABLED", False)
                self.system_config._update_settings("DEVELOPMENT_MODE", False)
                reset_results['system'] = True
                print("    ✅ Sistema resetado")
            except Exception as e:
                reset_results['system'] = False
                print(f"    ❌ Erro: {e}")
            
            # Backup configuration
            print("  💾 Resetando backup...")
            try:
                self.backup_config._update_settings("AUTO_BACKUP", True)
                self.backup_config._update_settings("BACKUP_COMPRESSION", True)
                self.backup_config._update_settings("BACKUP_RETENTION_DAYS", 30)
                reset_results['backup'] = True
                print("    ✅ Backup resetado")
            except Exception as e:
                reset_results['backup'] = False
                print(f"    ❌ Erro: {e}")
            
            # Summary
            successful_resets = sum(1 for success in reset_results.values() if success)
            total_modules = len(reset_results)
            
            print(f"\n📊 Resultado: {successful_resets}/{total_modules} módulos resetados com sucesso")
            
            if successful_resets == total_modules:
                self.show_success("🎉 Todas as configurações foram resetadas com sucesso!")
            else:
                self.show_warning(f"⚠️ {total_modules - successful_resets} módulo(s) tiveram problemas")
            
            self.show_warning("⚠️ Reinicie o sistema para aplicar todas as mudanças")
            
        except Exception as e:
            self.show_error(f"Erro durante reset completo: {e}")
    
    def _validate_boolean_input(self, prompt: str) -> bool:
        """Validate boolean input (s/n, y/n, sim/não)"""
        response = input(prompt).strip().lower()
        
        if response in ['s', 'sim', 'y', 'yes', '1', 'true']:
            return True
        elif response in ['n', 'não', 'nao', 'no', '0', 'false']:
            return False
        else:
            self.show_error("Por favor, responda com 's' para sim ou 'n' para não")
            return False
    
    def _confirm_action(self, action: str) -> bool:
        """Ask for confirmation before performing an action"""
        confirm = self._validate_boolean_input(f"\n❓ Confirmar {action}? (s/n): ")
        return confirm
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def get_manager_statistics(self) -> Dict[str, Any]:
        """Get statistics from all configuration modules"""
        return {
            'database': self.database_config.get_database_statistics(),
            'network': self.network_config.get_network_statistics(),
            'file': self.file_config.get_file_statistics(),
            'scraping': self.scraping_config.get_scraping_statistics(),
            'system': self.system_config.get_system_statistics(),
            'backup': self.backup_config.get_backup_statistics()
        }
    
    def get_module(self, module_name: str):
        """Get specific configuration module"""
        return self.modules.get(module_name)
    
    def get_all_modules(self) -> Dict[str, Any]:
        """Get all configuration modules"""
        return self.modules.copy()