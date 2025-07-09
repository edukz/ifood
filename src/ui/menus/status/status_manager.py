#!/usr/bin/env python3
"""
Status Manager - Central manager for all status monitoring modules
"""

from typing import Dict, Any
from pathlib import Path

from .system_status import SystemStatus
from .database_status import DatabaseStatus
from .scraper_status import ScraperStatus
from .log_analysis import LogAnalysis
from .performance_status import PerformanceStatus
from .live_dashboard import LiveDashboard
from .health_check import HealthCheck


class StatusManager:
    """Central manager for all status monitoring modules"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        self.session_stats = session_stats
        self.data_dir = data_dir
        
        # Initialize all status modules
        self.system_status = SystemStatus(session_stats, data_dir)
        self.database_status = DatabaseStatus(session_stats, data_dir)
        self.scraper_status = ScraperStatus(session_stats, data_dir)
        self.log_analysis = LogAnalysis(session_stats, data_dir)
        self.performance_status = PerformanceStatus(session_stats, data_dir)
        self.live_dashboard = LiveDashboard(session_stats, data_dir)
        self.health_check = HealthCheck(session_stats, data_dir)
    
    def menu_system_status(self):
        """Main system status menu"""
        options = [
            "1. 📊 Status geral do sistema",
            "2. 💾 Status do banco de dados",
            "3. 🔍 Status dos scrapers",
            "4. 📈 Monitoramento de recursos",
            "5. 📋 Logs e auditoria",
            "6. 🔄 Saúde do sistema",
            "7. 📊 Dashboard em tempo real",
            "8. 🎯 Métricas de performance"
        ]
        
        from src.ui.base_menu import BaseMenu
        menu = BaseMenu("Status do Sistema", self.session_stats, self.data_dir)
        menu.show_menu("📊 STATUS DO SISTEMA", options)
        choice = menu.get_user_choice(8)
        
        if choice == "1":
            self.system_status.show_general_status()
        elif choice == "2":
            self.database_status.show_database_status()
        elif choice == "3":
            self.scraper_status.show_scrapers_status()
        elif choice == "4":
            self.system_status.show_resources_monitoring()
        elif choice == "5":
            self.log_analysis.show_logs_audit()
        elif choice == "6":
            self.health_check.show_health_check()
        elif choice == "7":
            self.live_dashboard.show_realtime_dashboard()
        elif choice == "8":
            self.performance_status.show_performance_metrics()
        elif choice == "0":
            return
        else:
            menu.show_invalid_option()
    
    def show_general_status(self):
        """Show general system status"""
        self.system_status.show_general_status()
    
    def show_database_status(self):
        """Show database status"""
        self.database_status.show_database_status()
    
    def show_scrapers_status(self):
        """Show scrapers status"""
        self.scraper_status.show_scrapers_status()
    
    def show_resources_monitoring(self):
        """Show resources monitoring"""
        self.system_status.show_resources_monitoring()
    
    def show_logs_audit(self):
        """Show logs audit"""
        self.log_analysis.show_logs_audit()
    
    def show_health_check(self):
        """Show health check"""
        self.health_check.show_health_check()
    
    def show_realtime_dashboard(self):
        """Show realtime dashboard"""
        self.live_dashboard.show_realtime_dashboard()
    
    def show_performance_metrics(self):
        """Show performance metrics"""
        self.performance_status.show_performance_metrics()
    
    def show_table_details(self, table_name: str = None):
        """Show table details"""
        self.database_status.show_table_details(table_name)
    
    def get_manager_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all modules"""
        return {
            'system_status': self.system_status.get_system_statistics(),
            'database_status': self.database_status.get_database_statistics(),
            'scraper_status': self.scraper_status.get_scraper_statistics(),
            'log_analysis': self.log_analysis.get_log_statistics(),
            'performance_status': self.performance_status.get_performance_statistics(),
            'dashboard_status': self.live_dashboard.get_dashboard_statistics(),
            'health_check': self.health_check.get_health_statistics(),
            'manager_info': {
                'total_modules': 7,
                'active_modules': self._count_active_modules(),
                'session_stats': self.session_stats
            }
        }
    
    def _count_active_modules(self) -> int:
        """Count active modules"""
        # For now, all modules are considered active
        # In a real implementation, you might have logic to determine active modules
        return 7
    
    def get_quick_system_overview(self) -> Dict[str, Any]:
        """Get quick system overview"""
        try:
            # Get basic system info
            system_resources = self.system_status.get_system_resources()
            
            # Get database info
            database_info = self.database_status.get_database_info()
            
            # Get health score
            health_stats = self.health_check.get_health_statistics()
            
            return {
                'system_resources': {
                    'cpu_percent': system_resources.get('cpu', {}).get('percent', 0),
                    'memory_percent': system_resources.get('memory', {}).get('percent', 0),
                    'disk_percent': system_resources.get('disk', {}).get('percent', 0)
                },
                'database_connected': database_info.get('connected', False),
                'health_score': health_stats.get('health_check', {}).get('overall_score', 0),
                'session_stats': self.session_stats
            }
        except Exception as e:
            return {
                'error': str(e),
                'system_resources': {'cpu_percent': 0, 'memory_percent': 0, 'disk_percent': 0},
                'database_connected': False,
                'health_score': 0
            }
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.live_dashboard.start_dashboard()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.live_dashboard.stop_dashboard()
    
    def export_status_report(self, format: str = 'json') -> str:
        """Export comprehensive status report"""
        try:
            stats = self.get_manager_statistics()
            
            if format.lower() == 'json':
                import json
                return json.dumps(stats, indent=2, default=str)
            else:
                # Simple text format
                report = []
                report.append("=== STATUS REPORT ===")
                report.append(f"Generated at: {stats['manager_info']['session_stats'].get('timestamp', 'Unknown')}")
                report.append("")
                
                # System overview
                system_stats = stats.get('system_status', {})
                if 'health_score' in system_stats:
                    report.append(f"System Health Score: {system_stats['health_score']}")
                
                # Database status
                db_stats = stats.get('database_status', {})
                if 'connection_healthy' in db_stats:
                    report.append(f"Database Status: {'Connected' if db_stats['connection_healthy'] else 'Disconnected'}")
                
                return "\n".join(report)
                
        except Exception as e:
            return f"Error generating report: {e}"