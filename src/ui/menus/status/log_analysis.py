#!/usr/bin/env python3
"""
Log Analysis - Log analysis and auditing
"""

import re
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta

from .status_base import StatusBase


class LogAnalysis(StatusBase):
    """Log analysis and auditing"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Análise de Logs", session_stats, data_dir)
    
    def show_logs_audit(self):
        """Show comprehensive logs audit"""
        print("\n📋 LOGS E AUDITORIA")
        print("═" * 50)
        
        logs_dir = Path("logs")
        
        if not logs_dir.exists():
            print("❌ Diretório de logs não encontrado")
            return
        
        # List log files
        self._show_log_files(logs_dir)
        
        # Analyze current log
        self._analyze_current_log(logs_dir)
        
        # Show temporal analysis
        self._show_temporal_analysis(logs_dir)
        
        # Show component analysis
        self._show_component_analysis(logs_dir)
        
        # Show error analysis
        self._show_error_analysis(logs_dir)
        
        # Show performance analysis
        self._show_performance_analysis(logs_dir)
    
    def _show_log_files(self, logs_dir: Path):
        """List all log files"""
        log_files = list(logs_dir.glob("*.log"))
        print(f"📁 ARQUIVOS DE LOG ({len(log_files)} encontrados):")
        
        if not log_files:
            print("  Nenhum arquivo de log encontrado")
            return
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for log_file in log_files:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            print(f"  📄 {log_file.name} - {size_mb:.2f} MB - {mtime.strftime('%d/%m/%Y %H:%M')}")
    
    def _analyze_current_log(self, logs_dir: Path):
        """Analyze current day's log"""
        today_log = logs_dir / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not today_log.exists():
            print("\n❌ Log do dia atual não encontrado")
            return
        
        print(f"\n📊 ANÁLISE DO LOG ATUAL ({today_log.name}):")
        
        try:
            with open(today_log, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Count by log level
            levels = {
                'INFO': content.count(' - INFO - '),
                'WARNING': content.count(' - WARNING - '),
                'ERROR': content.count(' - ERROR - '),
                'DEBUG': content.count(' - DEBUG - '),
                'CRITICAL': content.count(' - CRITICAL - ')
            }
            
            print(f"  Total de linhas: {len(lines)}")
            for level, count in levels.items():
                if count > 0:
                    print(f"  {level}: {count} entradas")
            
            # Show recent entries by level
            self._show_recent_entries_by_level(lines)
            
        except Exception as e:
            self.show_error(f"Erro ao analisar log atual: {e}")
    
    def _show_recent_entries_by_level(self, lines: List[str]):
        """Show recent log entries by level"""
        print(f"\n📋 ÚLTIMAS ENTRADAS POR NÍVEL:")
        
        for level in ['ERROR', 'WARNING', 'INFO']:
            level_lines = [line for line in lines if f' - {level} - ' in line]
            if level_lines:
                print(f"  {level} (últimas 3):")
                for line in level_lines[-3:]:
                    if line.strip():
                        # Extract timestamp and message
                        parts = line.split(' - ')
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            message = ' - '.join(parts[2:])
                            print(f"    {timestamp}: {message[:60]}...")
    
    def _show_temporal_analysis(self, logs_dir: Path):
        """Show temporal analysis of logs"""
        print(f"\n⏰ ANÁLISE TEMPORAL:")
        
        today_log = logs_dir / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not today_log.exists():
            print("  Nenhum log para análise temporal")
            return
        
        try:
            with open(today_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Group by hour
            hourly_activity = {}
            for line in lines:
                if ' - ' in line:
                    timestamp_str = line.split(' - ')[0]
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        hour = timestamp.hour
                        hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
                    except ValueError:
                        continue
            
            if hourly_activity:
                print("  Atividade por hora:")
                for hour in sorted(hourly_activity.keys()):
                    bar = '█' * min(hourly_activity[hour] // 10, 20)
                    print(f"    {hour:02d}:00 - {hourly_activity[hour]:4d} {bar}")
            
            # Show peak hours
            if hourly_activity:
                peak_hour = max(hourly_activity.items(), key=lambda x: x[1])
                print(f"  🔥 Pico de atividade: {peak_hour[0]:02d}:00 ({peak_hour[1]} entradas)")
                
        except Exception as e:
            self.show_error(f"Erro na análise temporal: {e}")
    
    def _show_component_analysis(self, logs_dir: Path):
        """Show component analysis"""
        print(f"\n🔧 ANÁLISE DE COMPONENTES:")
        
        today_log = logs_dir / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not today_log.exists():
            print("  Nenhum log para análise de componentes")
            return
        
        try:
            with open(today_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            components = {}
            for line in lines:
                if ' - ' in line:
                    parts = line.split(' - ')
                    if len(parts) >= 2:
                        component = parts[1]
                        components[component] = components.get(component, 0) + 1
            
            # Top 10 most active components
            top_components = sorted(components.items(), key=lambda x: x[1], reverse=True)[:10]
            
            print("  Top 10 componentes mais ativos:")
            for component, count in top_components:
                print(f"    {component}: {count} entradas")
                
        except Exception as e:
            self.show_error(f"Erro na análise de componentes: {e}")
    
    def _show_error_analysis(self, logs_dir: Path):
        """Show error analysis"""
        print(f"\n🚨 ANÁLISE DE ERROS:")
        
        today_log = logs_dir / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not today_log.exists():
            print("  Nenhum log para análise de erros")
            return
        
        try:
            with open(today_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            error_lines = [line for line in lines if ' - ERROR - ' in line]
            
            if not error_lines:
                print("  ✅ Nenhum erro encontrado")
                return
            
            print(f"  Total de erros: {len(error_lines)}")
            
            # Group errors by type
            error_types = {}
            error_patterns = {}
            
            for error_line in error_lines:
                # Extract error type
                if ':' in error_line:
                    error_msg = error_line.split(':')[-1].strip()
                    error_type = error_msg.split()[0] if error_msg else 'Unknown'
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                
                # Extract error patterns
                self._extract_error_patterns(error_line, error_patterns)
            
            # Show most common error types
            print("  Tipos de erro mais comuns:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {error_type}: {count} ocorrências")
            
            # Show error patterns
            if error_patterns:
                print("  Padrões de erro identificados:")
                for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"    {pattern}: {count} ocorrências")
            
            # Show recent errors
            print("  Últimos 3 erros:")
            for error in error_lines[-3:]:
                parts = error.split(' - ')
                if len(parts) >= 3:
                    timestamp = parts[0]
                    message = ' - '.join(parts[2:])
                    print(f"    {timestamp}: {message[:60]}...")
            
            # Error timeline
            self._show_error_timeline(error_lines)
            
        except Exception as e:
            self.show_error(f"Erro na análise de erros: {e}")
    
    def _extract_error_patterns(self, error_line: str, error_patterns: Dict[str, int]):
        """Extract common error patterns"""
        patterns = [
            (r'Connection.*refused', 'Connection Refused'),
            (r'Timeout.*exceeded', 'Timeout'),
            (r'HTTP.*404', 'Not Found'),
            (r'HTTP.*500', 'Server Error'),
            (r'Permission.*denied', 'Permission Denied'),
            (r'File.*not.*found', 'File Not Found'),
            (r'Database.*error', 'Database Error'),
            (r'Network.*error', 'Network Error')
        ]
        
        for pattern, name in patterns:
            if re.search(pattern, error_line, re.IGNORECASE):
                error_patterns[name] = error_patterns.get(name, 0) + 1
    
    def _show_error_timeline(self, error_lines: List[str]):
        """Show error timeline"""
        print("  Timeline de erros (últimas 24h):")
        
        error_times = []
        for line in error_lines:
            timestamp_str = line.split(' - ')[0]
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                error_times.append(timestamp)
            except ValueError:
                continue
        
        if len(error_times) > 1:
            # Calculate intervals between errors
            intervals = []
            for i in range(1, len(error_times)):
                interval = (error_times[i] - error_times[i-1]).total_seconds()
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                print(f"    Intervalo médio entre erros: {self.format_duration(avg_interval)}")
                
                # Show error frequency
                recent_errors = [t for t in error_times if t > datetime.now() - timedelta(hours=1)]
                if recent_errors:
                    print(f"    Erros na última hora: {len(recent_errors)}")
    
    def _show_performance_analysis(self, logs_dir: Path):
        """Show performance analysis from logs"""
        print(f"\n⚡ ANÁLISE DE PERFORMANCE:")
        
        today_log = logs_dir / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not today_log.exists():
            print("  Nenhum log para análise de performance")
            return
        
        try:
            with open(today_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Look for timing metrics
            time_metrics = []
            for line in lines:
                if 'tempo' in line.lower() or 'segundos' in line.lower() or 'ms' in line.lower():
                    time_metrics.append(line)
            
            if time_metrics:
                print(f"  Métricas de tempo encontradas: {len(time_metrics)}")
                print("  Últimas 5 métricas:")
                for metric in time_metrics[-5:]:
                    parts = metric.split(' - ')
                    if len(parts) >= 3:
                        timestamp = parts[0]
                        message = ' - '.join(parts[2:])
                        print(f"    {timestamp}: {message[:60]}...")
            
            # Extract performance numbers
            self._extract_performance_numbers(lines)
            
        except Exception as e:
            self.show_error(f"Erro na análise de performance: {e}")
    
    def _extract_performance_numbers(self, lines: List[str]):
        """Extract performance numbers from logs"""
        performance_data = {
            'response_times': [],
            'throughput': [],
            'success_rates': []
        }
        
        for line in lines:
            # Extract response times
            time_match = re.search(r'(\d+\.?\d*)\s*(ms|segundos|s)', line.lower())
            if time_match:
                time_value = float(time_match.group(1))
                unit = time_match.group(2)
                if unit in ['ms']:
                    performance_data['response_times'].append(time_value)
                elif unit in ['segundos', 's']:
                    performance_data['response_times'].append(time_value * 1000)
            
            # Extract throughput data
            throughput_match = re.search(r'(\d+)\s*itens/segundo', line.lower())
            if throughput_match:
                performance_data['throughput'].append(float(throughput_match.group(1)))
        
        # Show performance statistics
        if performance_data['response_times']:
            avg_response = sum(performance_data['response_times']) / len(performance_data['response_times'])
            print(f"  Tempo médio de resposta: {avg_response:.2f}ms")
            
            if len(performance_data['response_times']) > 1:
                min_response = min(performance_data['response_times'])
                max_response = max(performance_data['response_times'])
                print(f"  Faixa de resposta: {min_response:.2f}ms - {max_response:.2f}ms")
        
        if performance_data['throughput']:
            avg_throughput = sum(performance_data['throughput']) / len(performance_data['throughput'])
            print(f"  Throughput médio: {avg_throughput:.2f} itens/segundo")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get log analysis statistics"""
        stats = self.get_base_statistics()
        
        # Add log-specific statistics
        stats['log_analysis'] = self._get_log_analysis_stats()
        stats['error_analysis'] = self._get_error_analysis_stats()
        stats['performance_analysis'] = self._get_performance_analysis_stats()
        
        return stats
    
    def _get_log_analysis_stats(self) -> Dict[str, Any]:
        """Get log analysis statistics"""
        logs_dir = Path("logs")
        
        if not logs_dir.exists():
            return {'error': 'Logs directory not found'}
        
        log_files = list(logs_dir.glob("*.log"))
        total_size = sum(f.stat().st_size for f in log_files)
        
        return {
            'total_files': len(log_files),
            'total_size': total_size,
            'latest_file': max(log_files, key=lambda x: x.stat().st_mtime).name if log_files else None
        }
    
    def _get_error_analysis_stats(self) -> Dict[str, Any]:
        """Get error analysis statistics"""
        today_log = Path("logs") / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not today_log.exists():
            return {'error': 'No log file for today'}
        
        try:
            with open(today_log, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'error_count': content.count(' - ERROR - '),
                'warning_count': content.count(' - WARNING - '),
                'critical_count': content.count(' - CRITICAL - '),
                'total_lines': len(content.split('\n'))
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_performance_analysis_stats(self) -> Dict[str, Any]:
        """Get performance analysis statistics"""
        today_log = Path("logs") / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not today_log.exists():
            return {'error': 'No log file for today'}
        
        try:
            with open(today_log, 'r', encoding='utf-8') as f:
                content = f.read()
            
            time_metrics_count = len(re.findall(r'\d+\.?\d*\s*(ms|segundos|s)', content.lower()))
            
            return {
                'time_metrics_found': time_metrics_count,
                'performance_entries': content.count('performance'),
                'throughput_entries': content.count('throughput')
            }
        except Exception as e:
            return {'error': str(e)}