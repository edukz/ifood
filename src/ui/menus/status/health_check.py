#!/usr/bin/env python3
"""
Health Check - System health verification and monitoring
"""

import os
from typing import Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime

from .status_base import StatusBase


class HealthCheck(StatusBase):
    """System health verification and monitoring"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Verificação de Saúde", session_stats, data_dir)
    
    def show_health_check(self):
        """Show comprehensive system health check"""
        print("\n🔄 VERIFICAÇÃO DE SAÚDE DO SISTEMA")
        print("═" * 50)
        
        health_score = 0
        max_score = 100
        issues = []
        
        try:
            # Perform all health checks
            checks = self._perform_comprehensive_health_checks()
            
            # Display results
            self._display_health_results(checks)
            
            # Calculate overall score
            health_score, issues = self._calculate_health_score(checks)
            
            # Show final result
            self._show_final_health_result(health_score, max_score, issues)
            
        except Exception as e:
            self.show_error(f"Erro na verificação de saúde: {e}")
    
    def _perform_comprehensive_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """Perform comprehensive health checks"""
        checks = {}
        
        # Database connection check (25 points)
        checks['database'] = self._check_database_connection()
        
        # System resources check (20 points)
        checks['resources'] = self._check_system_resources()
        
        # Dependencies check (15 points)
        checks['dependencies'] = self._check_dependencies()
        
        # Configuration files check (10 points)
        checks['configuration'] = self._check_configuration_files()
        
        # Directories check (10 points)
        checks['directories'] = self._check_directories()
        
        # Connectivity check (10 points)
        checks['connectivity'] = self._check_connectivity()
        
        # Log files check (10 points)
        checks['logs'] = self._check_log_files()
        
        return checks
    
    def _check_database_connection(self) -> Dict[str, Any]:
        """Check database connection health"""
        print("🔍 Verificando conexão com banco de dados...")
        
        try:
            with self.db.get_cursor() as (cursor, _):
                cursor.execute("SELECT 1")
                
                # Additional database checks
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0] if cursor.fetchone() else "Unknown"
                
                cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                result = cursor.fetchone()
                connections = int(result[1]) if result else 0
                
                print("  ✅ Conexão com banco: OK")
                
                return {
                    'passed': True,
                    'score': 25,
                    'details': f"Versão: {version}, Conexões: {connections}",
                    'recommendations': []
                }
                
        except Exception as e:
            print(f"  ❌ Conexão com banco: FALHA - {e}")
            return {
                'passed': False,
                'score': 0,
                'details': f"Erro: {e}",
                'recommendations': [
                    "Verifique as configurações do banco no arquivo .env",
                    "Certifique-se de que o MySQL está rodando",
                    "Verifique as credenciais de acesso"
                ]
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources health"""
        print("🔍 Verificando recursos do sistema...")
        
        try:
            resources = self.get_system_resources()
            
            if not resources:
                return {
                    'passed': False,
                    'score': 0,
                    'details': "Erro ao obter recursos do sistema",
                    'recommendations': ["Verifique se o psutil está instalado"]
                }
            
            cpu_percent = resources['cpu']['percent']
            memory_percent = resources['memory']['percent']
            disk_percent = resources['disk']['percent']
            
            issues = []
            recommendations = []
            
            if memory_percent > 90:
                issues.append(f"Memória crítica: {memory_percent:.1f}%")
                recommendations.append("Feche aplicações desnecessárias")
                recommendations.append("Considere aumentar a RAM")
            elif memory_percent > 80:
                issues.append(f"Memória alta: {memory_percent:.1f}%")
                recommendations.append("Monitore o uso de memória")
            
            if cpu_percent > 90:
                issues.append(f"CPU crítica: {cpu_percent:.1f}%")
                recommendations.append("Reduza o número de workers paralelos")
            elif cpu_percent > 80:
                issues.append(f"CPU alta: {cpu_percent:.1f}%")
                recommendations.append("Monitore processos que consomem CPU")
            
            if disk_percent > 95:
                issues.append(f"Disco crítico: {disk_percent:.1f}%")
                recommendations.append("Limpe arquivos temporários urgentemente")
            elif disk_percent > 90:
                issues.append(f"Disco cheio: {disk_percent:.1f}%")
                recommendations.append("Limpe arquivos desnecessários")
                recommendations.append("Execute limpeza de logs")
            
            if issues:
                print(f"  ⚠️ Recursos: {', '.join(issues)}")
                score = 10 if any("crítica" in issue or "crítico" in issue for issue in issues) else 15
            else:
                print("  ✅ Recursos do sistema: OK")
                score = 20
            
            return {
                'passed': len(issues) == 0,
                'score': score,
                'details': f"CPU: {cpu_percent:.1f}%, Mem: {memory_percent:.1f}%, Disco: {disk_percent:.1f}%",
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"  ❌ Recursos do sistema: ERRO - {e}")
            return {
                'passed': False,
                'score': 0,
                'details': f"Erro: {e}",
                'recommendations': ["Verifique se o psutil está instalado"]
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check required dependencies"""
        print("🔍 Verificando dependências...")
        
        required_deps = [
            'mysql.connector',
            'requests',
            'beautifulsoup4',
            'playwright',
            'selenium',
            'lxml',
            'tabulate'
        ]
        
        missing_deps = []
        working_deps = []
        
        for dep in required_deps:
            try:
                __import__(dep)
                working_deps.append(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"  ⚠️ Dependências faltando: {', '.join(missing_deps)}")
            score = 5 if len(missing_deps) > 3 else 10
            recommendations = [
                "Execute: pip install -r requirements.txt",
                f"Instale dependências faltando: {', '.join(missing_deps)}"
            ]
        else:
            print("  ✅ Dependências: OK")
            score = 15
            recommendations = []
        
        return {
            'passed': len(missing_deps) == 0,
            'score': score,
            'details': f"Funcionando: {len(working_deps)}, Faltando: {len(missing_deps)}",
            'recommendations': recommendations
        }
    
    def _check_configuration_files(self) -> Dict[str, Any]:
        """Check configuration files"""
        print("🔍 Verificando arquivos de configuração...")
        
        config_files = [
            ('.env', 'Variáveis de ambiente'),
            ('config/settings.json', 'Configurações do sistema'),
            ('requirements.txt', 'Dependências Python')
        ]
        
        missing_configs = []
        existing_configs = []
        
        for config_file, description in config_files:
            if Path(config_file).exists():
                existing_configs.append((config_file, description))
            else:
                missing_configs.append((config_file, description))
        
        if missing_configs:
            missing_list = [f"{file} ({desc})" for file, desc in missing_configs]
            print(f"  ⚠️ Arquivos de config faltando: {', '.join([f[0] for f in missing_configs])}")
            score = 5
            recommendations = [
                f"Crie o arquivo: {config_file}" for config_file, _ in missing_configs
            ]
        else:
            print("  ✅ Arquivos de configuração: OK")
            score = 10
            recommendations = []
        
        return {
            'passed': len(missing_configs) == 0,
            'score': score,
            'details': f"Existentes: {len(existing_configs)}, Faltando: {len(missing_configs)}",
            'recommendations': recommendations
        }
    
    def _check_directories(self) -> Dict[str, Any]:
        """Check required directories"""
        print("🔍 Verificando diretórios...")
        
        required_dirs = [
            ('logs', 'Arquivos de log'),
            ('data', 'Dados extraídos'),
            ('cache', 'Cache do sistema'),
            ('config', 'Configurações')
        ]
        
        missing_dirs = []
        created_dirs = []
        
        for dir_name, description in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(dir_name)
                    print(f"  ✅ Diretório criado: {dir_name}")
                except Exception:
                    missing_dirs.append((dir_name, description))
            else:
                print(f"  ✅ Diretório existe: {dir_name}")
        
        if missing_dirs:
            print(f"  ⚠️ Diretórios não criados: {', '.join([d[0] for d in missing_dirs])}")
            score = 5
            recommendations = [
                f"Crie o diretório: {dir_name}" for dir_name, _ in missing_dirs
            ]
        else:
            score = 10
            recommendations = []
        
        return {
            'passed': len(missing_dirs) == 0,
            'score': score,
            'details': f"Criados: {len(created_dirs)}, Faltando: {len(missing_dirs)}",
            'recommendations': recommendations
        }
    
    def _check_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity"""
        print("🔍 Verificando conectividade...")
        
        test_sites = [
            ('www.google.com', 'Google'),
            ('www.ifood.com.br', 'iFood'),
            ('github.com', 'GitHub')
        ]
        
        successful_tests = 0
        failed_tests = []
        
        for site, name in test_sites:
            if self.test_connectivity(site):
                successful_tests += 1
            else:
                failed_tests.append(name)
        
        if successful_tests == len(test_sites):
            print("  ✅ Conectividade: OK")
            score = 10
            recommendations = []
        elif successful_tests > 0:
            print(f"  ⚠️ Conectividade: Parcial ({successful_tests}/{len(test_sites)})")
            score = 5
            recommendations = [
                "Verifique sua conexão com a internet",
                "Verifique configurações de proxy/firewall"
            ]
        else:
            print("  ❌ Conectividade: FALHA")
            score = 0
            recommendations = [
                "Verifique sua conexão com a internet",
                "Verifique configurações de rede",
                "Verifique proxy/firewall"
            ]
        
        return {
            'passed': successful_tests == len(test_sites),
            'score': score,
            'details': f"Sucessos: {successful_tests}/{len(test_sites)}",
            'recommendations': recommendations
        }
    
    def _check_log_files(self) -> Dict[str, Any]:
        """Check log files health"""
        print("🔍 Verificando logs...")
        
        log_file = Path("logs") / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not log_file.exists():
            print("  ⚠️ Logs: Arquivo do dia não encontrado")
            return {
                'passed': False,
                'score': 5,
                'details': "Arquivo de log do dia não encontrado",
                'recommendations': ["Execute o sistema para gerar logs"]
            }
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            error_count = content.count(' - ERROR - ')
            critical_count = content.count(' - CRITICAL - ')
            warning_count = content.count(' - WARNING - ')
            
            if critical_count > 0:
                print(f"  ❌ Logs: {critical_count} erros críticos encontrados")
                score = 0
                recommendations = [
                    "Investigue os erros críticos imediatamente",
                    "Verifique a configuração do sistema"
                ]
            elif error_count > 10:
                print(f"  ⚠️ Logs: {error_count} erros encontrados")
                score = 5
                recommendations = [
                    "Investigue os erros frequentes",
                    "Considere implementar retry automático"
                ]
            elif warning_count > 20:
                print(f"  ⚠️ Logs: {warning_count} avisos encontrados")
                score = 7
                recommendations = [
                    "Revise os avisos nos logs",
                    "Otimize configurações se necessário"
                ]
            else:
                print("  ✅ Logs: OK")
                score = 10
                recommendations = []
            
            return {
                'passed': critical_count == 0 and error_count <= 10,
                'score': score,
                'details': f"Erros: {error_count}, Críticos: {critical_count}, Avisos: {warning_count}",
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"  ❌ Logs: ERRO - {e}")
            return {
                'passed': False,
                'score': 0,
                'details': f"Erro ao ler logs: {e}",
                'recommendations': ["Verifique permissões do arquivo de log"]
            }
    
    def _display_health_results(self, checks: Dict[str, Dict[str, Any]]):
        """Display health check results in a table"""
        print(f"\n📊 RESULTADOS DETALHADOS:")
        
        headers = ["Verificação", "Status", "Score", "Detalhes"]
        data = []
        
        for check_name, check_info in checks.items():
            status = "✅ PASSOU" if check_info['passed'] else "❌ FALHOU"
            score = f"{check_info['score']}/25" if check_name == 'database' else f"{check_info['score']}/20" if check_name == 'resources' else f"{check_info['score']}/15" if check_name == 'dependencies' else f"{check_info['score']}/10"
            
            data.append([
                check_name.title(),
                status,
                score,
                check_info['details'][:50] + "..." if len(check_info['details']) > 50 else check_info['details']
            ])
        
        self.show_table(headers, data)
    
    def _calculate_health_score(self, checks: Dict[str, Dict[str, Any]]) -> Tuple[int, List[str]]:
        """Calculate overall health score"""
        total_score = sum(check['score'] for check in checks.values())
        max_score = 100
        
        all_issues = []
        for check_name, check_info in checks.items():
            if not check_info['passed']:
                all_issues.append(f"{check_name.title()}: {check_info['details']}")
        
        return total_score, all_issues
    
    def _show_final_health_result(self, health_score: int, max_score: int, issues: List[str]):
        """Show final health result"""
        print(f"\n🎯 RESULTADO DA VERIFICAÇÃO:")
        print(f"  Pontuação: {health_score}/{max_score}")
        
        if health_score >= 90:
            status = "🟢 EXCELENTE"
        elif health_score >= 80:
            status = "🟡 BOM"
        elif health_score >= 70:
            status = "🟠 REGULAR"
        else:
            status = "🔴 CRÍTICO"
        
        print(f"  Status: {status}")
        
        if issues:
            print(f"\n⚠️ PROBLEMAS ENCONTRADOS ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"    {i}. {issue}")
            
            # Show consolidated recommendations
            self._show_consolidated_recommendations(health_score)
        else:
            print("\n✅ NENHUM PROBLEMA ENCONTRADO")
            print("  Sistema operando normalmente!")
    
    def _show_consolidated_recommendations(self, health_score: int):
        """Show consolidated recommendations"""
        print(f"\n💡 RECOMENDAÇÕES:")
        
        if health_score < 50:
            print("  🚨 AÇÃO URGENTE NECESSÁRIA:")
            print("  • Resolva os problemas críticos imediatamente")
            print("  • Verifique configurações básicas do sistema")
            print("  • Considere reiniciar o sistema após correções")
        elif health_score < 75:
            print("  ⚠️ AÇÃO RECOMENDADA:")
            print("  • Resolva os problemas encontrados")
            print("  • Monitore o sistema mais frequentemente")
            print("  • Considere otimizações de performance")
        else:
            print("  ✅ MANUTENÇÃO PREVENTIVA:")
            print("  • Continue monitorando o sistema")
            print("  • Execute verificações periódicas")
            print("  • Mantenha backups atualizados")
    
    def get_health_statistics(self) -> Dict[str, Any]:
        """Get health check statistics"""
        stats = self.get_base_statistics()
        
        # Perform health checks
        checks = self._perform_comprehensive_health_checks()
        
        # Calculate score
        health_score, issues = self._calculate_health_score(checks)
        
        # Add health-specific statistics
        stats['health_check'] = {
            'overall_score': health_score,
            'max_score': 100,
            'status': 'excellent' if health_score >= 90 else 'good' if health_score >= 80 else 'regular' if health_score >= 70 else 'critical',
            'issues_count': len(issues),
            'checks_passed': sum(1 for check in checks.values() if check['passed']),
            'total_checks': len(checks)
        }
        
        # Add individual check results
        stats['individual_checks'] = {
            name: {
                'passed': check['passed'],
                'score': check['score'],
                'details': check['details']
            }
            for name, check in checks.items()
        }
        
        return stats