#!/usr/bin/env python3
"""
Network Configuration - HTTP/HTTPS, proxy, and connectivity settings
"""

import requests
import time
from typing import Dict, Any
from pathlib import Path

from .config_base import ConfigBase


class NetworkConfig(ConfigBase):
    """Network configuration management"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Configuração de Rede", session_stats, data_dir)
    
    def show_network_menu(self):
        """Show network configuration menu"""
        current_config = {
            "Timeout HTTP": "HTTP_TIMEOUT",
            "User-Agent": "USER_AGENT",
            "Proxy HTTP": "HTTP_PROXY",
            "Proxy HTTPS": "HTTPS_PROXY",
            "Delay mínimo": "MIN_DELAY",
            "Delay máximo": "MAX_DELAY"
        }
        
        options = [
            "1. ⏱️ Configurar timeout",
            "2. 🌐 Configurar User-Agent",
            "3. 🔄 Configurar proxy",
            "4. ⏳ Configurar delays",
            "5. 🧪 Testar conectividade",
            "6. 📊 Verificar status de rede",
            "7. 🔧 Configurações avançadas"
        ]
        
        self._show_config_menu("🌐 CONFIGURAÇÕES DE REDE", options, current_config)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._configure_timeout()
        elif choice == "2":
            self._configure_user_agent()
        elif choice == "3":
            self._configure_proxy()
        elif choice == "4":
            self._configure_delays()
        elif choice == "5":
            self._test_connectivity()
        elif choice == "6":
            self._check_network_status()
        elif choice == "7":
            self._advanced_network_config()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _configure_timeout(self):
        """Configure HTTP timeout settings"""
        print("\n⏱️ CONFIGURAR TIMEOUT")
        print("═" * 25)
        
        current_timeout = self._get_setting("HTTP_TIMEOUT", 30)
        current_connect_timeout = self._get_setting("CONNECT_TIMEOUT", 10)
        current_read_timeout = self._get_setting("READ_TIMEOUT", 30)
        
        print(f"Timeout HTTP atual: {current_timeout}s")
        print(f"Timeout de conexão atual: {current_connect_timeout}s")
        print(f"Timeout de leitura atual: {current_read_timeout}s")
        
        new_timeout = self._validate_numeric_input("\n⏱️ Novo timeout HTTP (5-300s): ", 5, 300)
        if new_timeout is None:
            new_timeout = current_timeout
        
        new_connect_timeout = self._validate_numeric_input("🔗 Novo timeout de conexão (3-60s): ", 3, 60)
        if new_connect_timeout is None:
            new_connect_timeout = current_connect_timeout
        
        new_read_timeout = self._validate_numeric_input("📖 Novo timeout de leitura (5-300s): ", 5, 300)
        if new_read_timeout is None:
            new_read_timeout = current_read_timeout
        
        if self._confirm_action("atualizar configurações de timeout"):
            success = True
            if new_timeout != current_timeout:
                success &= self._update_settings("HTTP_TIMEOUT", new_timeout)
            if new_connect_timeout != current_connect_timeout:
                success &= self._update_settings("CONNECT_TIMEOUT", new_connect_timeout)
            if new_read_timeout != current_read_timeout:
                success &= self._update_settings("READ_TIMEOUT", new_read_timeout)
            
            if success:
                self.show_success("Configurações de timeout atualizadas!")
    
    def _configure_user_agent(self):
        """Configure User-Agent settings"""
        print("\n🌐 CONFIGURAR USER-AGENT")
        print("═" * 30)
        
        current_user_agent = self._get_setting("USER_AGENT", "iFoodScraper/1.0")
        print(f"User-Agent atual: {current_user_agent}")
        
        predefined_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "iFoodScraper/1.0"
        ]
        
        print("\n📋 User-Agents predefinidos:")
        for i, agent in enumerate(predefined_agents, 1):
            print(f"  {i}. {agent[:60]}...")
        
        choice = self._validate_numeric_input("\n🌐 Escolha um User-Agent (1-4) ou 0 para personalizado: ", 0, 4)
        
        if choice == 0:
            custom_agent = input("\n🌐 Digite o User-Agent personalizado: ").strip()
            if custom_agent:
                new_user_agent = custom_agent
            else:
                self.show_error("User-Agent não pode ser vazio")
                return
        elif choice and 1 <= choice <= 4:
            new_user_agent = predefined_agents[choice - 1]
        else:
            return
        
        if self._confirm_action(f"alterar User-Agent para: {new_user_agent[:50]}..."):
            if self._update_settings("USER_AGENT", new_user_agent):
                self.show_success("User-Agent atualizado!")
    
    def _configure_proxy(self):
        """Configure proxy settings"""
        print("\n🔄 CONFIGURAR PROXY")
        print("═" * 25)
        
        current_http_proxy = self._get_env_var("HTTP_PROXY", "")
        current_https_proxy = self._get_env_var("HTTPS_PROXY", "")
        
        print(f"Proxy HTTP atual: {current_http_proxy if current_http_proxy else 'Não configurado'}")
        print(f"Proxy HTTPS atual: {current_https_proxy if current_https_proxy else 'Não configurado'}")
        
        print("\n📋 Opções:")
        print("  1. Configurar proxy HTTP")
        print("  2. Configurar proxy HTTPS")
        print("  3. Remover proxy")
        print("  4. Testar proxy")
        
        choice = self._validate_numeric_input("\n🔄 Escolha uma opção (1-4): ", 1, 4)
        
        if choice == 1:
            self._configure_http_proxy()
        elif choice == 2:
            self._configure_https_proxy()
        elif choice == 3:
            self._remove_proxy()
        elif choice == 4:
            self._test_proxy()
    
    def _configure_http_proxy(self):
        """Configure HTTP proxy"""
        proxy_url = input("\n🔄 Digite a URL do proxy HTTP (ex: http://proxy.example.com:8080): ").strip()
        
        if not proxy_url:
            self.show_error("URL do proxy não pode ser vazia")
            return
        
        if self._confirm_action(f"configurar proxy HTTP: {proxy_url}"):
            if self._update_env_file("HTTP_PROXY", proxy_url):
                self.show_success("Proxy HTTP configurado!")
    
    def _configure_https_proxy(self):
        """Configure HTTPS proxy"""
        proxy_url = input("\n🔄 Digite a URL do proxy HTTPS (ex: https://proxy.example.com:8080): ").strip()
        
        if not proxy_url:
            self.show_error("URL do proxy não pode ser vazia")
            return
        
        if self._confirm_action(f"configurar proxy HTTPS: {proxy_url}"):
            if self._update_env_file("HTTPS_PROXY", proxy_url):
                self.show_success("Proxy HTTPS configurado!")
    
    def _remove_proxy(self):
        """Remove proxy configuration"""
        if self._confirm_action("remover configuração de proxy"):
            success = True
            success &= self._update_env_file("HTTP_PROXY", "")
            success &= self._update_env_file("HTTPS_PROXY", "")
            
            if success:
                self.show_success("Configuração de proxy removida!")
    
    def _test_proxy(self):
        """Test proxy configuration"""
        print("\n🧪 TESTAR PROXY")
        print("═" * 20)
        
        http_proxy = self._get_env_var("HTTP_PROXY", "")
        https_proxy = self._get_env_var("HTTPS_PROXY", "")
        
        if not http_proxy and not https_proxy:
            self.show_warning("Nenhum proxy configurado")
            return
        
        proxies = {}
        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        
        try:
            self.show_info("Testando proxy...")
            
            # Test HTTP connection
            response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                self.show_success(f"✅ Proxy funcionando! IP: {ip_info.get('origin', 'N/A')}")
            else:
                self.show_error(f"❌ Erro no teste: Status {response.status_code}")
                
        except requests.exceptions.ProxyError as e:
            self.show_error(f"❌ Erro de proxy: {str(e)}")
        except requests.exceptions.Timeout:
            self.show_error("❌ Timeout ao testar proxy")
        except Exception as e:
            self.show_error(f"❌ Erro inesperado: {str(e)}")
    
    def _configure_delays(self):
        """Configure request delays"""
        print("\n⏳ CONFIGURAR DELAYS")
        print("═" * 25)
        
        current_min_delay = self._get_setting("MIN_DELAY", 1.0)
        current_max_delay = self._get_setting("MAX_DELAY", 3.0)
        current_human_delay = self._get_setting("HUMAN_DELAY", 0.5)
        
        print(f"Delay mínimo atual: {current_min_delay}s")
        print(f"Delay máximo atual: {current_max_delay}s")
        print(f"Delay humano atual: {current_human_delay}s")
        
        try:
            new_min_delay = float(input(f"\n⏳ Novo delay mínimo (0.1-10.0s): ") or current_min_delay)
            if not 0.1 <= new_min_delay <= 10.0:
                self.show_error("Delay mínimo deve estar entre 0.1 e 10.0 segundos")
                return
            
            new_max_delay = float(input(f"⏳ Novo delay máximo ({new_min_delay}-20.0s): ") or current_max_delay)
            if not new_min_delay <= new_max_delay <= 20.0:
                self.show_error(f"Delay máximo deve estar entre {new_min_delay} e 20.0 segundos")
                return
            
            new_human_delay = float(input(f"👤 Novo delay humano (0.1-5.0s): ") or current_human_delay)
            if not 0.1 <= new_human_delay <= 5.0:
                self.show_error("Delay humano deve estar entre 0.1 e 5.0 segundos")
                return
        
        except ValueError:
            self.show_error("Por favor, insira valores numéricos válidos")
            return
        
        if self._confirm_action("atualizar configurações de delay"):
            success = True
            if new_min_delay != current_min_delay:
                success &= self._update_settings("MIN_DELAY", new_min_delay)
            if new_max_delay != current_max_delay:
                success &= self._update_settings("MAX_DELAY", new_max_delay)
            if new_human_delay != current_human_delay:
                success &= self._update_settings("HUMAN_DELAY", new_human_delay)
            
            if success:
                self.show_success("Configurações de delay atualizadas!")
    
    def _test_connectivity(self):
        """Test network connectivity"""
        print("\n🧪 TESTAR CONECTIVIDADE")
        print("═" * 30)
        
        test_urls = [
            ("Google", "https://www.google.com"),
            ("iFood", "https://www.ifood.com.br"),
            ("CloudFlare DNS", "https://1.1.1.1"),
            ("GitHub", "https://github.com")
        ]
        
        self.show_info("Testando conectividade com múltiplos serviços...")
        
        results = {}
        for name, url in test_urls:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                response_time = round((end_time - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    results[name] = {"status": "✅ OK", "time": f"{response_time}ms"}
                    print(f"  {name}: ✅ OK ({response_time}ms)")
                else:
                    results[name] = {"status": f"❌ Error {response.status_code}", "time": f"{response_time}ms"}
                    print(f"  {name}: ❌ Error {response.status_code}")
                    
            except requests.exceptions.Timeout:
                results[name] = {"status": "❌ Timeout", "time": ">10s"}
                print(f"  {name}: ❌ Timeout")
            except requests.exceptions.ConnectionError:
                results[name] = {"status": "❌ Connection Error", "time": "N/A"}
                print(f"  {name}: ❌ Connection Error")
            except Exception as e:
                results[name] = {"status": f"❌ {str(e)[:30]}", "time": "N/A"}
                print(f"  {name}: ❌ {str(e)[:30]}")
        
        # Summary
        successful_tests = sum(1 for result in results.values() if result["status"] == "✅ OK")
        total_tests = len(test_urls)
        
        print(f"\n📊 Resultado: {successful_tests}/{total_tests} testes bem-sucedidos")
        
        if successful_tests == total_tests:
            self.show_success("🎉 Conectividade perfeita!")
        elif successful_tests > 0:
            self.show_warning(f"⚠️ Conectividade parcial ({successful_tests}/{total_tests})")
        else:
            self.show_error("❌ Falha completa de conectividade")
    
    def _check_network_status(self):
        """Check network status and configuration"""
        print("\n📊 STATUS DE REDE")
        print("═" * 25)
        
        # Show current configuration
        print("📋 Configuração atual:")
        print(f"  HTTP Timeout: {self._get_setting('HTTP_TIMEOUT', 30)}s")
        print(f"  User-Agent: {self._get_setting('USER_AGENT', 'iFoodScraper/1.0')[:50]}...")
        print(f"  Proxy HTTP: {self._get_env_var('HTTP_PROXY', 'Não configurado')}")
        print(f"  Proxy HTTPS: {self._get_env_var('HTTPS_PROXY', 'Não configurado')}")
        print(f"  Delay mínimo: {self._get_setting('MIN_DELAY', 1.0)}s")
        print(f"  Delay máximo: {self._get_setting('MAX_DELAY', 3.0)}s")
        
        # Quick connectivity test
        print("\n🔍 Teste rápido de conectividade:")
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                print("  ✅ Conexão com internet: OK")
            else:
                print(f"  ❌ Problema de conexão: Status {response.status_code}")
        except:
            print("  ❌ Conexão com internet: FALHA")
    
    def _advanced_network_config(self):
        """Advanced network configuration options"""
        print("\n🔧 CONFIGURAÇÕES AVANÇADAS DE REDE")
        print("═" * 45)
        
        options = [
            "1. 🔄 Configurar retry automático",
            "2. 🕷️ Configurar rate limiting",
            "3. 📡 Configurar keep-alive",
            "4. 🔐 Configurar certificados SSL",
            "5. 📊 Monitoramento de rede"
        ]
        
        for option in options:
            print(f"  {option}")
        
        choice = self._validate_numeric_input("\n🔧 Escolha uma opção (1-5): ", 1, 5)
        
        if choice == 1:
            self._configure_retry()
        elif choice == 2:
            self._configure_rate_limiting()
        elif choice == 3:
            self._configure_keep_alive()
        elif choice == 4:
            self._configure_ssl()
        elif choice == 5:
            self._configure_network_monitoring()
    
    def _configure_retry(self):
        """Configure automatic retry settings"""
        print("\n🔄 CONFIGURAR RETRY AUTOMÁTICO")
        print("═" * 35)
        
        current_max_retries = self._get_setting("MAX_RETRIES", 3)
        current_retry_delay = self._get_setting("RETRY_DELAY", 2.0)
        
        print(f"Máximo de tentativas atual: {current_max_retries}")
        print(f"Delay entre tentativas atual: {current_retry_delay}s")
        
        new_max_retries = self._validate_numeric_input("🔄 Novo máximo de tentativas (1-10): ", 1, 10)
        if new_max_retries is None:
            return
        
        try:
            new_retry_delay = float(input("⏳ Novo delay entre tentativas (0.5-30.0s): ") or current_retry_delay)
            if not 0.5 <= new_retry_delay <= 30.0:
                self.show_error("Delay deve estar entre 0.5 e 30.0 segundos")
                return
        except ValueError:
            self.show_error("Por favor, insira um valor numérico válido")
            return
        
        if self._confirm_action("atualizar configurações de retry"):
            success = True
            if new_max_retries != current_max_retries:
                success &= self._update_settings("MAX_RETRIES", new_max_retries)
            if new_retry_delay != current_retry_delay:
                success &= self._update_settings("RETRY_DELAY", new_retry_delay)
            
            if success:
                self.show_success("Configurações de retry atualizadas!")
    
    def _configure_rate_limiting(self):
        """Configure rate limiting"""
        print("\n🕷️ CONFIGURAR RATE LIMITING")
        print("═" * 35)
        
        current_requests_per_minute = self._get_setting("REQUESTS_PER_MINUTE", 60)
        current_concurrent_requests = self._get_setting("CONCURRENT_REQUESTS", 5)
        
        print(f"Requests por minuto atual: {current_requests_per_minute}")
        print(f"Requests simultâneos atual: {current_concurrent_requests}")
        
        new_requests_per_minute = self._validate_numeric_input("🕷️ Novo limite de requests por minuto (1-300): ", 1, 300)
        if new_requests_per_minute is None:
            return
        
        new_concurrent_requests = self._validate_numeric_input("🔄 Novo limite de requests simultâneos (1-20): ", 1, 20)
        if new_concurrent_requests is None:
            return
        
        if self._confirm_action("atualizar configurações de rate limiting"):
            success = True
            if new_requests_per_minute != current_requests_per_minute:
                success &= self._update_settings("REQUESTS_PER_MINUTE", new_requests_per_minute)
            if new_concurrent_requests != current_concurrent_requests:
                success &= self._update_settings("CONCURRENT_REQUESTS", new_concurrent_requests)
            
            if success:
                self.show_success("Configurações de rate limiting atualizadas!")
    
    def _configure_keep_alive(self):
        """Configure HTTP keep-alive settings"""
        current_keep_alive = self._get_setting("HTTP_KEEP_ALIVE", True)
        
        print(f"\n📡 HTTP Keep-Alive atual: {'Ativado' if current_keep_alive else 'Desativado'}")
        
        new_keep_alive = self._validate_boolean_input("📡 Ativar HTTP Keep-Alive? (s/n): ")
        if new_keep_alive is None:
            return
        
        if new_keep_alive != current_keep_alive:
            if self._update_settings("HTTP_KEEP_ALIVE", new_keep_alive):
                status = "ativado" if new_keep_alive else "desativado"
                self.show_success(f"HTTP Keep-Alive {status}!")
    
    def _configure_ssl(self):
        """Configure SSL/TLS settings"""
        print("\n🔐 CONFIGURAR CERTIFICADOS SSL")
        print("═" * 35)
        
        current_verify_ssl = self._get_setting("VERIFY_SSL", True)
        print(f"Verificação SSL atual: {'Ativada' if current_verify_ssl else 'Desativada'}")
        
        new_verify_ssl = self._validate_boolean_input("🔐 Verificar certificados SSL? (s/n): ")
        if new_verify_ssl is None:
            return
        
        if new_verify_ssl != current_verify_ssl:
            if self._update_settings("VERIFY_SSL", new_verify_ssl):
                status = "ativada" if new_verify_ssl else "desativada"
                self.show_success(f"Verificação SSL {status}!")
                
                if not new_verify_ssl:
                    self.show_warning("⚠️ Desativar verificação SSL pode ser um risco de segurança!")
    
    def _configure_network_monitoring(self):
        """Configure network monitoring"""
        print("\n📊 MONITORAMENTO DE REDE")
        print("═" * 30)
        
        current_monitor_enabled = self._get_setting("NETWORK_MONITORING", False)
        current_monitor_interval = self._get_setting("MONITOR_INTERVAL", 60)
        
        print(f"Monitoramento atual: {'Ativado' if current_monitor_enabled else 'Desativado'}")
        print(f"Intervalo atual: {current_monitor_interval}s")
        
        new_monitor_enabled = self._validate_boolean_input("📊 Ativar monitoramento de rede? (s/n): ")
        if new_monitor_enabled is None:
            return
        
        if new_monitor_enabled:
            new_monitor_interval = self._validate_numeric_input("⏱️ Intervalo de monitoramento (30-3600s): ", 30, 3600)
            if new_monitor_interval is None:
                return
        else:
            new_monitor_interval = current_monitor_interval
        
        if self._confirm_action("atualizar configurações de monitoramento"):
            success = True
            if new_monitor_enabled != current_monitor_enabled:
                success &= self._update_settings("NETWORK_MONITORING", new_monitor_enabled)
            if new_monitor_interval != current_monitor_interval:
                success &= self._update_settings("MONITOR_INTERVAL", new_monitor_interval)
            
            if success:
                status = "ativado" if new_monitor_enabled else "desativado"
                self.show_success(f"Monitoramento de rede {status}!")
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """Get network configuration statistics"""
        stats = self.get_base_statistics()
        
        # Test basic connectivity
        try:
            response = requests.get("https://www.google.com", timeout=5)
            stats['internet_connectivity'] = response.status_code == 200
            stats['connectivity_response_time'] = response.elapsed.total_seconds()
        except:
            stats['internet_connectivity'] = False
            stats['connectivity_response_time'] = None
        
        # Configuration status
        stats.update({
            'proxy_configured': bool(self._get_env_var("HTTP_PROXY") or self._get_env_var("HTTPS_PROXY")),
            'timeout_configured': self._get_setting("HTTP_TIMEOUT", 30),
            'user_agent_configured': bool(self._get_setting("USER_AGENT")),
            'delays_configured': {
                'min_delay': self._get_setting("MIN_DELAY", 1.0),
                'max_delay': self._get_setting("MAX_DELAY", 3.0)
            }
        })
        
        return stats