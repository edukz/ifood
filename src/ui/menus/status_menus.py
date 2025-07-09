#!/usr/bin/env python3
"""
Status Menus - Modular status monitoring and system health interface
"""

from typing import Dict, Any
from pathlib import Path

from .status.status_manager import StatusManager
from src.ui.base_menu import BaseMenu


class StatusMenus(BaseMenu):
    """Modern modular status monitoring interface"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Status do Sistema", session_stats, data_dir)
        self.status_manager = StatusManager(session_stats, data_dir)
    
    def menu_system_status(self):
        """Main system status menu using modular system"""
        return self.status_manager.menu_system_status()
    
    # Quick access methods for commonly used functionality
    def show_general_status(self):
        """Show general system status"""
        return self.status_manager.show_general_status()
    
    def show_database_status(self):
        """Show database status"""
        return self.status_manager.show_database_status()
    
    def show_scrapers_status(self):
        """Show scrapers status"""
        return self.status_manager.show_scrapers_status()
    
    def show_resources_monitoring(self):
        """Show resources monitoring"""
        return self.status_manager.show_resources_monitoring()
    
    def show_logs_audit(self):
        """Show logs audit"""
        return self.status_manager.show_logs_audit()
    
    def show_health_check(self):
        """Show health check"""
        return self.status_manager.show_health_check()
    
    def show_realtime_dashboard(self):
        """Show realtime dashboard"""
        return self.status_manager.show_realtime_dashboard()
    
    def show_performance_metrics(self):
        """Show performance metrics"""
        return self.status_manager.show_performance_metrics()
    
    def show_table_details(self, table_name: str = None):
        """Show table details"""
        return self.status_manager.show_table_details(table_name)
    
    # Enhanced functionality
    def get_status_statistics(self) -> Dict[str, Any]:
        """Get comprehensive status statistics"""
        return self.status_manager.get_manager_statistics()
    
    def get_quick_overview(self) -> Dict[str, Any]:
        """Get quick system overview"""
        return self.status_manager.get_quick_system_overview()
    
    def export_status_report(self, format: str = 'json') -> str:
        """Export status report"""
        return self.status_manager.export_status_report(format)
    
    def start_monitoring(self):
        """Start system monitoring"""
        return self.status_manager.start_monitoring()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        return self.status_manager.stop_monitoring()


# Legacy wrapper for backward compatibility
class StatusMenusLegacy(StatusMenus):
    """Legacy wrapper to maintain backward compatibility"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__(session_stats, data_dir)
        
        # Statistics tracking for legacy support
        self.stats = {
            'menu_accesses': 0,
            'status_checks': 0,
            'errors': 0,
            'last_check': None
        }
    
    def _general_status(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_general_status()
    
    def _database_status(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_database_status()
    
    def _scrapers_status(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_scrapers_status()
    
    def _resources_monitoring(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_resources_monitoring()
    
    def _logs_audit(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_logs_audit()
    
    def _health_check(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_health_check()
    
    def _realtime_dashboard(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_realtime_dashboard()
    
    def _performance_metrics(self):
        """Legacy method - redirect to modular system"""
        self.stats['menu_accesses'] += 1
        return self.show_performance_metrics()
    
    def _test_connectivity(self) -> bool:
        """Legacy connectivity test"""
        return self.status_manager.system_status.test_connectivity()


# Export both new and legacy interfaces
__all__ = ['StatusMenus', 'StatusMenusLegacy']