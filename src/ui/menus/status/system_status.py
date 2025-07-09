#!/usr/bin/env python3
"""
System Status - System resources and health monitoring
"""

import os
import platform
import psutil
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta

from .status_base import StatusBase


class SystemStatus(StatusBase):
    """System resources and health monitoring"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Status do Sistema", session_stats, data_dir)
    
    def show_general_status(self):
        """Show general system status overview"""
        print("\n📊 STATUS GERAL DO SISTEMA")
        print("═" * 50)
        
        # System information
        self._show_system_info()
        
        # Session information
        self._show_session_info()
        
        # Quick resource overview
        self._show_resource_overview()
        
        # System health summary
        self._show_health_summary()
    
    def _show_system_info(self):
        """Display system information"""
        print("\n🖥️ Informações do Sistema:")
        
        try:
            print(f"  Sistema Operacional: {platform.system()} {platform.release()}")
            print(f"  Versão Python: {platform.python_version()}")
            print(f"  Arquitetura: {platform.machine()}")
            print(f"  Processador: {platform.processor() or 'N/A'}")
            print(f"  Hostname: {platform.node()}")
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            print(f"  Uptime: {self._format_timedelta(uptime)}")
            
        except Exception as e:
            self.show_error(f"Erro ao obter informações do sistema: {e}")
    
    def _show_session_info(self):
        """Display current session information"""
        print("\n📈 Informações da Sessão:")
        
        try:
            session_start = self.session_stats.get('session_start', datetime.now())
            if isinstance(session_start, str):
                session_start = datetime.fromisoformat(session_start)
            
            duration = datetime.now() - session_start
            
            print(f"  Início: {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Duração: {self._format_timedelta(duration)}")
            print(f"  Restaurantes processados: {self.session_stats.get('restaurants_scraped', 0)}")
            print(f"  Produtos categorizados: {self.session_stats.get('products_categorized', 0)}")
            print(f"  Erros encontrados: {self.session_stats.get('errors', 0)}")
            
        except Exception as e:
            self.show_error(f"Erro ao exibir informações da sessão: {e}")
    
    def _show_resource_overview(self):
        """Display quick resource overview"""
        print("\n💻 Recursos do Sistema:")
        
        resources = self.get_system_resources()
        
        if resources:
            # CPU
            cpu_data = resources.get('cpu', {})
            cpu_percent = cpu_data.get('percent', 0)
            cpu_status = self.format_status_indicator(cpu_percent, {'critical': 80, 'warning': 60})
            print(f"  CPU: {cpu_status} ({cpu_data.get('count', 0)} núcleos)")
            
            # Memory
            memory_data = resources.get('memory', {})
            memory_percent = memory_data.get('percent', 0)
            memory_status = self.format_status_indicator(memory_percent, {'critical': 85, 'warning': 70})
            memory_used = self.format_bytes(memory_data.get('used', 0))
            memory_total = self.format_bytes(memory_data.get('total', 0))
            print(f"  Memória: {memory_status} ({memory_used}/{memory_total})")
            
            # Disk
            disk_data = resources.get('disk', {})
            disk_percent = disk_data.get('percent', 0)
            disk_status = self.format_status_indicator(disk_percent, {'critical': 90, 'warning': 75})
            disk_free = self.format_bytes(disk_data.get('free', 0))
            print(f"  Disco: {disk_status} ({disk_free} livre)")
    
    def _show_health_summary(self):
        """Display system health summary"""
        print("\n🏥 Saúde do Sistema:")
        
        health_checks = self._perform_health_checks()
        score, status = self.calculate_health_score(health_checks)
        
        # Show score with appropriate indicator
        if score >= 90:
            indicator = self.indicators['healthy']
        elif score >= 70:
            indicator = self.indicators['warning_level']
        else:
            indicator = self.indicators['critical']
        
        print(f"  Score geral: {indicator} {score:.1f}% - {status}")
        
        # Show failed checks
        failed_checks = [check for check, passed in health_checks.items() if not passed]
        if failed_checks:
            print(f"  {self.indicators['warning']} Verificações falhadas: {', '.join(failed_checks)}")
    
    def show_resources_monitoring(self):
        """Show detailed resources monitoring"""
        print("\n💻 MONITORAMENTO DE RECURSOS")
        print("═" * 50)
        
        # CPU details
        self._show_cpu_details()
        
        # Memory details
        self._show_memory_details()
        
        # Disk details
        self._show_disk_details()
        
        # Network details
        self._show_network_details()
        
        # Process details
        self._show_process_details()
    
    def _show_cpu_details(self):
        """Display detailed CPU information"""
        print("\n🔲 CPU:")
        
        try:
            # Overall CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"  Uso total: {self.format_status_indicator(cpu_percent, {'critical': 80, 'warning': 60})}")
            
            # Per-core usage
            per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
            if per_cpu:
                print("  Uso por núcleo:")
                for i, percent in enumerate(per_cpu):
                    status = self.format_status_indicator(percent, {'critical': 90, 'warning': 70})
                    print(f"    Núcleo {i}: {status}")
            
            # CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                print(f"  Frequência: {freq.current:.0f} MHz (min: {freq.min:.0f}, max: {freq.max:.0f})")
            
            # Load average (Unix-like systems)
            if hasattr(os, 'getloadavg'):
                load1, load5, load15 = os.getloadavg()
                print(f"  Load average: {load1:.2f}, {load5:.2f}, {load15:.2f}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter detalhes da CPU: {e}")
    
    def _show_memory_details(self):
        """Display detailed memory information"""
        print("\n💾 Memória:")
        
        try:
            # Virtual memory
            vm = psutil.virtual_memory()
            print(f"  Total: {self.format_bytes(vm.total)}")
            print(f"  Disponível: {self.format_bytes(vm.available)}")
            print(f"  Usado: {self.format_bytes(vm.used)} ({vm.percent}%)")
            print(f"  Livre: {self.format_bytes(vm.free)}")
            
            # Swap memory
            swap = psutil.swap_memory()
            if swap.total > 0:
                print(f"\n  Swap:")
                print(f"    Total: {self.format_bytes(swap.total)}")
                print(f"    Usado: {self.format_bytes(swap.used)} ({swap.percent}%)")
                print(f"    Livre: {self.format_bytes(swap.free)}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter detalhes da memória: {e}")
    
    def _show_disk_details(self):
        """Display detailed disk information"""
        print("\n💿 Disco:")
        
        try:
            # Disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                if partition.mountpoint:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        print(f"\n  Partição: {partition.device}")
                        print(f"    Ponto de montagem: {partition.mountpoint}")
                        print(f"    Sistema de arquivos: {partition.fstype}")
                        print(f"    Total: {self.format_bytes(usage.total)}")
                        print(f"    Usado: {self.format_bytes(usage.used)} ({usage.percent}%)")
                        print(f"    Livre: {self.format_bytes(usage.free)}")
                    except PermissionError:
                        print(f"    {self.indicators['error']} Sem permissão para acessar")
                        
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                print(f"\n  I/O do Disco:")
                print(f"    Leituras: {disk_io.read_count} ({self.format_bytes(disk_io.read_bytes)})")
                print(f"    Escritas: {disk_io.write_count} ({self.format_bytes(disk_io.write_bytes)})")
                
        except Exception as e:
            self.show_error(f"Erro ao obter detalhes do disco: {e}")
    
    def _show_network_details(self):
        """Display detailed network information"""
        print("\n🌐 Rede:")
        
        try:
            # Network I/O
            net_io = psutil.net_io_counters()
            print(f"  Bytes enviados: {self.format_bytes(net_io.bytes_sent)}")
            print(f"  Bytes recebidos: {self.format_bytes(net_io.bytes_recv)}")
            print(f"  Pacotes enviados: {net_io.packets_sent:,}")
            print(f"  Pacotes recebidos: {net_io.packets_recv:,}")
            print(f"  Erros entrada: {net_io.errin}")
            print(f"  Erros saída: {net_io.errout}")
            
            # Test connectivity
            connectivity = self.test_connectivity()
            status = self.indicators['success'] if connectivity else self.indicators['error']
            print(f"\n  Conectividade Internet: {status}")
            
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            if interfaces:
                print("\n  Interfaces de rede:")
                for name, addrs in interfaces.items():
                    print(f"    {name}:")
                    for addr in addrs:
                        if addr.family.name == 'AF_INET':  # IPv4
                            print(f"      IPv4: {addr.address}")
                        elif addr.family.name == 'AF_INET6':  # IPv6
                            print(f"      IPv6: {addr.address}")
                            
        except Exception as e:
            self.show_error(f"Erro ao obter detalhes da rede: {e}")
    
    def _show_process_details(self):
        """Display current process details"""
        print("\n🔄 Processo Atual:")
        
        process_info = self.get_process_info()
        
        if 'error' not in process_info:
            print(f"  PID: {process_info.get('pid', 'N/A')}")
            print(f"  Nome: {process_info.get('name', 'N/A')}")
            print(f"  CPU: {process_info.get('cpu_percent', 0):.1f}%")
            print(f"  Memória RSS: {self.format_bytes(process_info.get('memory_rss', 0))}")
            print(f"  Memória VMS: {self.format_bytes(process_info.get('memory_vms', 0))}")
            print(f"  Threads: {process_info.get('threads', 0)}")
            print(f"  Arquivos abertos: {process_info.get('open_files', 0)}")
            print(f"  Conexões: {process_info.get('connections', 0)}")
            
            uptime = process_info.get('uptime')
            if uptime:
                print(f"  Uptime: {self._format_timedelta(uptime)}")
    
    def show_health_check(self):
        """Show detailed system health check"""
        print("\n🏥 VERIFICAÇÃO DE SAÚDE DO SISTEMA")
        print("═" * 50)
        
        checks = self._perform_detailed_health_checks()
        
        # Display each check
        headers = ["Verificação", "Status", "Detalhes"]
        data = []
        
        for check_name, check_info in checks.items():
            status = self.indicators['success'] if check_info['passed'] else self.indicators['error']
            data.append([check_name, status, check_info.get('details', '')])
        
        self.show_table(headers, data)
        
        # Calculate and show overall score
        score, status = self.calculate_health_score({k: v['passed'] for k, v in checks.items()})
        
        print(f"\n📊 Score de Saúde: {score:.1f}% - {status}")
        
        # Show recommendations
        self._show_health_recommendations(checks)
    
    def _perform_health_checks(self) -> Dict[str, bool]:
        """Perform basic health checks"""
        checks = {}
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        checks['CPU'] = cpu_percent < 80
        
        # Memory check
        memory = psutil.virtual_memory()
        checks['Memória'] = memory.percent < 85
        
        # Disk check
        disk = psutil.disk_usage('/')
        checks['Disco'] = disk.percent < 90
        
        # Database check
        db_info = self.get_database_info()
        checks['Banco de Dados'] = db_info.get('connected', False)
        
        # Connectivity check
        checks['Conectividade'] = self.test_connectivity()
        
        return checks
    
    def _perform_detailed_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """Perform detailed health checks"""
        checks = {}
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        checks['CPU'] = {
            'passed': cpu_percent < 80,
            'value': cpu_percent,
            'details': f"{cpu_percent:.1f}% de uso"
        }
        
        # Memory check
        memory = psutil.virtual_memory()
        checks['Memória'] = {
            'passed': memory.percent < 85,
            'value': memory.percent,
            'details': f"{memory.percent:.1f}% de uso, {self.format_bytes(memory.available)} disponível"
        }
        
        # Disk check
        disk = psutil.disk_usage('/')
        checks['Disco'] = {
            'passed': disk.percent < 90,
            'value': disk.percent,
            'details': f"{disk.percent:.1f}% de uso, {self.format_bytes(disk.free)} livre"
        }
        
        # Swap check
        swap = psutil.swap_memory()
        checks['Swap'] = {
            'passed': swap.percent < 50 if swap.total > 0 else True,
            'value': swap.percent,
            'details': f"{swap.percent:.1f}% de uso" if swap.total > 0 else "Não configurado"
        }
        
        # Database check
        db_info = self.get_database_info()
        checks['Banco de Dados'] = {
            'passed': db_info.get('connected', False),
            'value': db_info.get('connected', False),
            'details': f"{db_info.get('tables', 0)} tabelas, {self.format_bytes(db_info.get('size', 0))}"
        }
        
        # Connectivity check
        connectivity = self.test_connectivity()
        checks['Conectividade Internet'] = {
            'passed': connectivity,
            'value': connectivity,
            'details': "Conexão OK" if connectivity else "Sem conexão"
        }
        
        # Process limits check
        process = psutil.Process()
        open_files = len(process.open_files())
        checks['Limites do Processo'] = {
            'passed': open_files < 1000,
            'value': open_files,
            'details': f"{open_files} arquivos abertos"
        }
        
        # Log space check
        logs_dir = Path(self.session_stats.get('logs_dir', 'logs'))
        if logs_dir.exists():
            log_size = sum(f.stat().st_size for f in logs_dir.rglob('*') if f.is_file())
            checks['Espaço de Logs'] = {
                'passed': log_size < 1024 * 1024 * 1024,  # 1GB
                'value': log_size,
                'details': f"{self.format_bytes(log_size)} usado"
            }
        
        return checks
    
    def _show_health_recommendations(self, checks: Dict[str, Dict[str, Any]]):
        """Show health recommendations based on checks"""
        recommendations = []
        
        for check_name, check_info in checks.items():
            if not check_info['passed']:
                if check_name == 'CPU' and check_info['value'] > 80:
                    recommendations.append("🔧 CPU alta: Considere reduzir o número de workers paralelos")
                elif check_name == 'Memória' and check_info['value'] > 85:
                    recommendations.append("🔧 Memória alta: Feche aplicações desnecessárias ou aumente a RAM")
                elif check_name == 'Disco' and check_info['value'] > 90:
                    recommendations.append("🔧 Disco cheio: Limpe arquivos temporários ou logs antigos")
                elif check_name == 'Swap' and check_info['value'] > 50:
                    recommendations.append("🔧 Swap alto: Sistema com pouca memória RAM disponível")
                elif check_name == 'Banco de Dados' and not check_info['value']:
                    recommendations.append("🔧 Banco offline: Verifique a conexão com o banco de dados")
                elif check_name == 'Conectividade Internet' and not check_info['value']:
                    recommendations.append("🔧 Sem internet: Verifique sua conexão de rede")
                elif check_name == 'Espaço de Logs' and check_info['value'] > 1024 * 1024 * 1024:
                    recommendations.append("🔧 Logs grandes: Execute limpeza de logs antigos")
        
        if recommendations:
            print("\n💡 Recomendações:")
            for rec in recommendations:
                print(f"  {rec}")
        else:
            print(f"\n{self.indicators['success']} Sistema saudável! Nenhuma recomendação no momento.")
    
    def _format_timedelta(self, td: timedelta) -> str:
        """Format timedelta to human-readable string"""
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system status statistics"""
        stats = self.get_base_statistics()
        
        # Add system-specific statistics
        stats['health_checks'] = self._perform_health_checks()
        stats['health_score'] = self.calculate_health_score(stats['health_checks'])[0]
        
        # System info
        stats['system_info'] = {
            'platform': platform.system(),
            'release': platform.release(),
            'python_version': platform.python_version(),
            'architecture': platform.machine(),
            'hostname': platform.node()
        }
        
        return stats