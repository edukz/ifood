#!/usr/bin/env python3
"""
Sistema de Configuração - Refactored modular version
Main interface for the modular configuration system
"""

from typing import Dict, Any
from pathlib import Path

from .config_manager import ConfigManager
from src.ui.base_menu import BaseMenu


class ConfigMenus(BaseMenu):
    """Menus especializados para configurações do sistema - Versão Modular"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Configuração", session_stats, data_dir)
        
        # Initialize the modular configuration manager
        self.config_manager = ConfigManager(session_stats, data_dir)
        
        # Statistics tracking
        self.stats = {
            'menu_accesses': 0,
            'config_changes': 0,
            'backups_created': 0,
            'errors': 0
        }
    
    def menu_system_config(self):
        """Menu principal de configurações usando sistema modular"""
        self.stats['menu_accesses'] += 1
        
        try:
            # Delegate to the modular configuration manager
            self.config_manager.menu_system_config()
            
        except Exception as e:
            self.stats['errors'] += 1
            self.show_error(f"Erro no menu de configurações: {e}")
    
    def get_config_statistics(self) -> Dict[str, Any]:
        """Get configuration menu statistics"""
        stats = self.stats.copy()
        
        # Get statistics from all modules
        try:
            module_stats = self.config_manager.get_manager_statistics()
            stats['module_statistics'] = module_stats
            
            # Summary statistics
            stats['total_modules'] = len(self.config_manager.get_all_modules())
            stats['modules_loaded'] = len([m for m in self.config_manager.get_all_modules().values() if m is not None])
            
        except Exception as e:
            stats['statistics_error'] = str(e)
        
        return stats
    
    def get_module(self, module_name: str):
        """Get specific configuration module"""
        return self.config_manager.get_module(module_name)
    
    def get_all_modules(self) -> Dict[str, Any]:
        """Get all configuration modules"""
        return self.config_manager.get_all_modules()
    
    def backup_current_config(self) -> bool:
        """Create backup of current configuration"""
        try:
            backup_module = self.config_manager.get_module('backup')
            if backup_module:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_module._perform_backup("config", f"manual_backup_{timestamp}", True)
                
                if backup_path:
                    self.stats['backups_created'] += 1
                    self.show_success(f"Backup criado: {backup_path}")
                    return True
                else:
                    self.show_error("Falha ao criar backup")
                    return False
            else:
                self.show_error("Módulo de backup não disponível")
                return False
                
        except Exception as e:
            self.stats['errors'] += 1
            self.show_error(f"Erro ao criar backup: {e}")
            return False
    
    def quick_database_test(self) -> bool:
        """Quick database connection test"""
        try:
            db_module = self.config_manager.get_module('database')
            if db_module:
                # Use the database module's test method
                db_module._test_connection()
                return True
            else:
                self.show_error("Módulo de banco de dados não disponível")
                return False
                
        except Exception as e:
            self.stats['errors'] += 1
            self.show_error(f"Erro no teste de banco: {e}")
            return False
    
    def quick_network_test(self) -> bool:
        """Quick network connectivity test"""
        try:
            net_module = self.config_manager.get_module('network')
            if net_module:
                # Use the network module's test method
                net_module._test_connectivity()
                return True
            else:
                self.show_error("Módulo de rede não disponível")
                return False
                
        except Exception as e:
            self.stats['errors'] += 1
            self.show_error(f"Erro no teste de rede: {e}")
            return False
    
    def export_configuration(self) -> bool:
        """Export all configuration to file"""
        try:
            import json
            from datetime import datetime
            
            # Get all configuration data
            config_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'type': 'modular_export',
                'statistics': self.get_config_statistics(),
                'modules': {}
            }
            
            # Export data from each module
            for module_name, module in self.config_manager.get_all_modules().items():
                if module:
                    try:
                        if hasattr(module, f'get_{module_name}_statistics'):
                            config_data['modules'][module_name] = getattr(module, f'get_{module_name}_statistics')()
                        else:
                            config_data['modules'][module_name] = {'status': 'available'}
                    except Exception as e:
                        config_data['modules'][module_name] = {'error': str(e)}
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"config_export_{timestamp}.json"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.show_success(f"Configuração exportada: {export_file}")
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            self.show_error(f"Erro ao exportar configuração: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        health = {
            'overall_status': 'healthy',
            'issues': [],
            'warnings': [],
            'modules': {}
        }
        
        try:
            # Check each module's health
            for module_name, module in self.config_manager.get_all_modules().items():
                if module:
                    try:
                        if hasattr(module, f'get_{module_name}_statistics'):
                            stats = getattr(module, f'get_{module_name}_statistics')()
                            health['modules'][module_name] = {
                                'status': 'healthy',
                                'statistics': stats
                            }
                        else:
                            health['modules'][module_name] = {'status': 'available'}
                    except Exception as e:
                        health['modules'][module_name] = {
                            'status': 'error',
                            'error': str(e)
                        }
                        health['issues'].append(f"Módulo {module_name}: {e}")
                else:
                    health['modules'][module_name] = {'status': 'not_loaded'}
                    health['warnings'].append(f"Módulo {module_name} não carregado")
            
            # Determine overall status
            if health['issues']:
                health['overall_status'] = 'unhealthy'
            elif health['warnings']:
                health['overall_status'] = 'warning'
            
        except Exception as e:
            health['overall_status'] = 'error'
            health['issues'].append(f"Erro na verificação de saúde: {e}")
        
        return health


# Backward compatibility - Legacy class for existing integrations
class ConfigMenusLegacy(ConfigMenus):
    """Classe de compatibilidade com versão anterior"""
    
    def _database_config(self):
        """Método legacy - usa novo módulo"""
        db_module = self.config_manager.get_module('database')
        if db_module:
            db_module.show_database_menu()
    
    def _network_config(self):
        """Método legacy - usa novo módulo"""
        net_module = self.config_manager.get_module('network')
        if net_module:
            net_module.show_network_menu()
    
    def _file_config(self):
        """Método legacy - usa novo módulo"""
        file_module = self.config_manager.get_module('file')
        if file_module:
            file_module.show_file_menu()
    
    def _scraping_config(self):
        """Método legacy - usa novo módulo"""
        scraping_module = self.config_manager.get_module('scraping')
        if scraping_module:
            scraping_module.show_scraping_menu()
    
    def _logging_config(self):
        """Método legacy - usa novo módulo"""
        system_module = self.config_manager.get_module('system')
        if system_module:
            system_module._configure_logging()
    
    def _advanced_config(self):
        """Método legacy - usa novo módulo"""
        system_module = self.config_manager.get_module('system')
        if system_module:
            system_module._configure_advanced()
    
    def _backup_restore(self):
        """Método legacy - usa novo módulo"""
        backup_module = self.config_manager.get_module('backup')
        if backup_module:
            backup_module.show_backup_menu()
    
    def _reset_config(self):
        """Método legacy - usa novo módulo"""
        backup_module = self.config_manager.get_module('backup')
        if backup_module:
            backup_module._reset_config()