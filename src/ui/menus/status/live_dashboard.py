#!/usr/bin/env python3
"""
Live Dashboard - Real-time monitoring dashboard
"""

import os
import time
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .status_base import StatusBase


class LiveDashboard(StatusBase):
    """Real-time monitoring dashboard"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Dashboard em Tempo Real", session_stats, data_dir)
        self.is_running = False
    
    def show_realtime_dashboard(self):
        """Show real-time dashboard"""
        print("\n📊 DASHBOARD EM TEMPO REAL")
        print("═" * 50)
        print("Pressione Ctrl+C para sair")
        
        self.is_running = True
        
        try:
            while self.is_running:
                # Clear screen (works on most terminals)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Show dashboard header
                self._show_dashboard_header()
                
                # Show system resources
                self._show_system_resources_live()
                
                # Show database status
                self._show_database_status_live()
                
                # Show session statistics
                self._show_session_statistics_live()
                
                # Show current process
                self._show_current_process_live()
                
                # Show alerts
                self._show_alerts_live()
                
                # Show controls
                self._show_dashboard_controls()
                
                # Wait 5 seconds before next update
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n\n📊 Dashboard encerrado pelo usuário")
            self.is_running = False
        except Exception as e:
            self.show_error(f"Erro no dashboard: {e}")
            self.is_running = False
    
    def _show_dashboard_header(self):
        """Show dashboard header with current time"""
        print("📊 DASHBOARD EM TEMPO REAL")
        print("═" * 50)
        print(f"Atualizado em: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Status: {'🟢 Ativo' if self.is_running else '🔴 Inativo'}")
    
    def _show_system_resources_live(self):
        """Show system resources in real-time"""
        print(f"\n🖥️ RECURSOS DO SISTEMA:")
        
        try:
            resources = self.get_system_resources()
            
            if resources:
                # CPU
                cpu_percent = resources['cpu']['percent']
                cpu_status = self._get_status_indicator(cpu_percent, 80, 60)
                print(f"  CPU: {cpu_percent:5.1f}% {cpu_status}")
                
                # Memory
                memory_percent = resources['memory']['percent']
                memory_status = self._get_status_indicator(memory_percent, 80, 60)
                memory_used = self.format_bytes(resources['memory']['used'])
                memory_total = self.format_bytes(resources['memory']['total'])
                print(f"  Memória: {memory_percent:5.1f}% {memory_status} ({memory_used}/{memory_total})")
                
                # Disk
                disk_percent = resources['disk']['percent']
                disk_status = self._get_status_indicator(disk_percent, 90, 80)
                disk_free = self.format_bytes(resources['disk']['free'])
                print(f"  Disco: {disk_percent:5.1f}% {disk_status} ({disk_free} livre)")
                
                # Network
                network = resources['network']
                print(f"  Rede: ↑{self.format_bytes(network['bytes_sent'])} ↓{self.format_bytes(network['bytes_recv'])}")
                
        except Exception as e:
            print(f"  ❌ Erro ao obter recursos: {e}")
    
    def _show_database_status_live(self):
        """Show database status in real-time"""
        print(f"\n💾 STATUS DO BANCO:")
        
        try:
            with self.db.get_cursor() as (cursor, _):
                # Check connection
                cursor.execute("SELECT 1")
                print(f"  Status: 🟢 Online")
                
                # Get counts
                cursor.execute("SELECT COUNT(*) FROM restaurants")
                restaurants = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM products")
                products = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM categories WHERE is_active = TRUE")
                categories = cursor.fetchone()[0]
                
                # Show counts
                print(f"  🏪 Restaurantes: {restaurants:,}")
                print(f"  🍕 Produtos: {products:,}")
                print(f"  🏷️ Categorias: {categories:,}")
                
                # Show connections
                cursor.execute("SHOW PROCESSLIST")
                connections = len(cursor.fetchall())
                print(f"  🔗 Conexões: {connections}")
                
        except Exception as e:
            print(f"  Status: 🔴 Offline - {e}")
    
    def _show_session_statistics_live(self):
        """Show session statistics in real-time"""
        print(f"\n📊 SESSÃO ATUAL:")
        
        try:
            # Session data
            categories_extracted = self.session_stats.get('categories_extracted', 0)
            restaurants_extracted = self.session_stats.get('restaurants_extracted', 0)
            products_extracted = self.session_stats.get('products_extracted', 0)
            errors = self.session_stats.get('errors', 0)
            
            print(f"  🏷️ Categorias extraídas: {categories_extracted:,}")
            print(f"  🏪 Restaurantes extraídos: {restaurants_extracted:,}")
            print(f"  🍕 Produtos extraídos: {products_extracted:,}")
            print(f"  ❌ Erros encontrados: {errors:,}")
            
            # Calculate session duration
            session_start = self.session_stats.get('session_start')
            if session_start:
                if isinstance(session_start, str):
                    session_start = datetime.fromisoformat(session_start)
                
                duration = datetime.now() - session_start
                print(f"  ⏱️ Duração: {self.format_duration(duration.total_seconds())}")
                
                # Calculate throughput
                total_extracted = categories_extracted + restaurants_extracted + products_extracted
                if duration.total_seconds() > 0:
                    throughput = total_extracted / duration.total_seconds()
                    print(f"  ⚡ Throughput: {throughput:.2f} itens/segundo")
                    
        except Exception as e:
            print(f"  ❌ Erro ao obter estatísticas: {e}")
    
    def _show_current_process_live(self):
        """Show current process information in real-time"""
        print(f"\n🎯 PROCESSO ATUAL:")
        
        try:
            process_info = self.get_process_info()
            
            if 'error' not in process_info:
                print(f"  PID: {process_info.get('pid', 'N/A')}")
                print(f"  CPU: {process_info.get('cpu_percent', 0):.1f}%")
                print(f"  Memória: {process_info.get('memory_rss', 0) / (1024**2):.1f} MB")
                print(f"  Threads: {process_info.get('threads', 0)}")
                print(f"  Arquivos abertos: {process_info.get('open_files', 0)}")
                
                uptime = process_info.get('uptime')
                if uptime:
                    print(f"  Uptime: {self.format_duration(uptime.total_seconds())}")
            else:
                print(f"  ❌ Erro ao obter informações do processo")
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def _show_alerts_live(self):
        """Show system alerts in real-time"""
        print(f"\n⚠️ ALERTAS:")
        
        try:
            alerts = []
            
            # Check system resources
            resources = self.get_system_resources()
            if resources:
                cpu_percent = resources['cpu']['percent']
                memory_percent = resources['memory']['percent']
                disk_percent = resources['disk']['percent']
                
                if cpu_percent > 80:
                    alerts.append("🔴 CPU alta")
                elif cpu_percent > 60:
                    alerts.append("🟡 CPU moderada")
                
                if memory_percent > 80:
                    alerts.append("🔴 Memória alta")
                elif memory_percent > 60:
                    alerts.append("🟡 Memória moderada")
                
                if disk_percent > 90:
                    alerts.append("🔴 Disco cheio")
                elif disk_percent > 80:
                    alerts.append("🟡 Disco quase cheio")
            
            # Check database connection
            try:
                with self.db.get_cursor() as (cursor, _):
                    cursor.execute("SELECT 1")
            except Exception:
                alerts.append("🔴 Banco de dados offline")
            
            # Check connectivity
            if not self.test_connectivity():
                alerts.append("🔴 Sem conectividade")
            
            # Check recent errors
            recent_errors = self._check_recent_errors()
            if recent_errors > 5:
                alerts.append(f"🔴 {recent_errors} erros recentes")
            elif recent_errors > 0:
                alerts.append(f"🟡 {recent_errors} erros recentes")
            
            # Display alerts
            if alerts:
                for alert in alerts:
                    print(f"  {alert}")
            else:
                print(f"  ✅ SISTEMA NORMAL")
                
        except Exception as e:
            print(f"  ❌ Erro ao verificar alertas: {e}")
    
    def _show_dashboard_controls(self):
        """Show dashboard controls"""
        print(f"\n💡 Controles:")
        print(f"  Ctrl+C: Sair do dashboard")
        print(f"  Atualização automática a cada 5 segundos")
    
    def _get_status_indicator(self, value: float, critical: float, warning: float) -> str:
        """Get status indicator based on value and thresholds"""
        if value >= critical:
            return "🔴"
        elif value >= warning:
            return "🟡"
        else:
            return "🟢"
    
    def _check_recent_errors(self) -> int:
        """Check for recent errors in logs"""
        try:
            log_file = Path("logs") / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
            
            if not log_file.exists():
                return 0
            
            # Read last 100 lines to check for recent errors
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check last 100 lines for errors
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            error_count = 0
            
            for line in recent_lines:
                if ' - ERROR - ' in line:
                    error_count += 1
            
            return error_count
            
        except Exception:
            return 0
    
    def start_dashboard(self):
        """Start the dashboard"""
        self.is_running = True
        self.show_realtime_dashboard()
    
    def stop_dashboard(self):
        """Stop the dashboard"""
        self.is_running = False
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        stats = self.get_base_statistics()
        
        # Add dashboard-specific statistics
        stats['dashboard_status'] = {
            'is_running': self.is_running,
            'last_update': datetime.now().isoformat(),
            'update_interval': 5  # seconds
        }
        
        # Add current alerts
        stats['current_alerts'] = self._get_current_alerts()
        
        return stats
    
    def _get_current_alerts(self) -> List[str]:
        """Get current system alerts"""
        alerts = []
        
        try:
            # Check system resources
            resources = self.get_system_resources()
            if resources:
                if resources['cpu']['percent'] > 80:
                    alerts.append("High CPU usage")
                if resources['memory']['percent'] > 80:
                    alerts.append("High memory usage")
                if resources['disk']['percent'] > 90:
                    alerts.append("Disk almost full")
            
            # Check database connection
            try:
                with self.db.get_cursor() as (cursor, _):
                    cursor.execute("SELECT 1")
            except Exception:
                alerts.append("Database offline")
            
            # Check connectivity
            if not self.test_connectivity():
                alerts.append("No internet connectivity")
            
            # Check recent errors
            recent_errors = self._check_recent_errors()
            if recent_errors > 5:
                alerts.append(f"{recent_errors} recent errors")
            
        except Exception as e:
            alerts.append(f"Error checking alerts: {e}")
        
        return alerts