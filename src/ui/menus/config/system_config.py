#!/usr/bin/env python3
"""
System Configuration - Logging, cache, security, and advanced system settings
"""

import os
import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .config_base import ConfigBase


class SystemConfig(ConfigBase):
    """System configuration management"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Configuração do Sistema", session_stats, data_dir)
    
    def show_system_menu(self):
        """Show system configuration menu"""
        current_config = {
            "Nível de log": "LOG_LEVEL",
            "Cache habilitado": "CACHE_ENABLED",
            "Segurança": "SECURITY_ENABLED",
            "Monitoramento": "MONITORING_ENABLED",
            "Webhooks": "WEBHOOKS_ENABLED"
        }
        
        options = [
            "1. 📝 Configurar logging",
            "2. 🗄️ Configurar cache",
            "3. 🔒 Configurar segurança",
            "4. 📊 Configurar monitoramento",
            "5. 🔗 Configurar webhooks",
            "6. ⚙️ Configurações avançadas",
            "7. 🧹 Limpeza do sistema"
        ]
        
        self._show_config_menu("⚙️ CONFIGURAÇÕES DO SISTEMA", options, current_config)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._configure_logging()
        elif choice == "2":
            self._configure_cache()
        elif choice == "3":
            self._configure_security()
        elif choice == "4":
            self._configure_monitoring()
        elif choice == "5":
            self._configure_webhooks()
        elif choice == "6":
            self._configure_advanced()
        elif choice == "7":
            self._system_cleanup()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _configure_logging(self):
        """Configure logging settings"""
        print("\n📝 CONFIGURAR LOGGING")
        print("═" * 26)
        
        current_log_level = self._get_setting("LOG_LEVEL", "INFO")
        current_log_file = self._get_setting("LOG_FILE", "logs/app.log")
        current_log_rotation = self._get_setting("LOG_ROTATION", True)
        current_log_max_size = self._get_setting("LOG_MAX_SIZE_MB", 10)
        current_log_backup_count = self._get_setting("LOG_BACKUP_COUNT", 5)
        
        print(f"Nível de log atual: {current_log_level}")
        print(f"Arquivo de log atual: {current_log_file}")
        print(f"Rotação de log atual: {'Ativada' if current_log_rotation else 'Desativada'}")
        print(f"Tamanho máximo atual: {current_log_max_size}MB")
        print(f"Backups de log atual: {current_log_backup_count}")
        
        # Log level
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        print("\n📝 Níveis de log disponíveis:")
        for i, level in enumerate(log_levels, 1):
            print(f"  {i}. {level}")
        
        level_choice = self._validate_numeric_input("📝 Escolha o nível de log (1-5): ", 1, 5)
        if level_choice is None:
            return
        
        new_log_level = log_levels[level_choice - 1]
        
        # Log file
        new_log_file = input(f"\n📁 Novo arquivo de log (atual: {current_log_file}): ").strip()
        if not new_log_file:
            new_log_file = current_log_file
        
        # Log rotation
        new_log_rotation = self._validate_boolean_input("🔄 Ativar rotação de log? (s/n): ")
        if new_log_rotation is None:
            return
        
        if new_log_rotation:
            new_log_max_size = self._validate_numeric_input("📏 Tamanho máximo por arquivo (1-100MB): ", 1, 100)
            if new_log_max_size is None:
                return
            
            new_log_backup_count = self._validate_numeric_input("🗂️ Número de backups (1-20): ", 1, 20)
            if new_log_backup_count is None:
                return
        else:
            new_log_max_size = current_log_max_size
            new_log_backup_count = current_log_backup_count
        
        if self._confirm_action("atualizar configurações de logging"):
            success = True
            if new_log_level != current_log_level:
                success &= self._update_settings("LOG_LEVEL", new_log_level)
            if new_log_file != current_log_file:
                success &= self._update_settings("LOG_FILE", new_log_file)
            if new_log_rotation != current_log_rotation:
                success &= self._update_settings("LOG_ROTATION", new_log_rotation)
            if new_log_max_size != current_log_max_size:
                success &= self._update_settings("LOG_MAX_SIZE_MB", new_log_max_size)
            if new_log_backup_count != current_log_backup_count:
                success &= self._update_settings("LOG_BACKUP_COUNT", new_log_backup_count)
            
            if success:
                self.show_success("Configurações de logging atualizadas!")
                
                # Create log directory if it doesn't exist
                log_path = Path(new_log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _configure_cache(self):
        """Configure cache settings"""
        print("\n🗄️ CONFIGURAR CACHE")
        print("═" * 23)
        
        current_cache_enabled = self._get_setting("CACHE_ENABLED", True)
        current_cache_type = self._get_setting("CACHE_TYPE", "file")
        current_cache_ttl = self._get_setting("CACHE_TTL_SECONDS", 3600)
        current_cache_max_size = self._get_setting("CACHE_MAX_SIZE_MB", 100)
        current_cache_cleanup_interval = self._get_setting("CACHE_CLEANUP_INTERVAL_HOURS", 24)
        
        print(f"Cache atual: {'Ativado' if current_cache_enabled else 'Desativado'}")
        print(f"Tipo de cache atual: {current_cache_type}")
        print(f"TTL atual: {current_cache_ttl}s")
        print(f"Tamanho máximo atual: {current_cache_max_size}MB")
        print(f"Intervalo de limpeza atual: {current_cache_cleanup_interval}h")
        
        new_cache_enabled = self._validate_boolean_input("\n🗄️ Ativar cache? (s/n): ")
        if new_cache_enabled is None:
            return
        
        if new_cache_enabled:
            # Cache type
            cache_types = ["file", "memory", "redis"]
            print("\n🗄️ Tipos de cache disponíveis:")
            for i, cache_type in enumerate(cache_types, 1):
                print(f"  {i}. {cache_type}")
            
            type_choice = self._validate_numeric_input("🗄️ Escolha o tipo de cache (1-3): ", 1, 3)
            if type_choice is None:
                return
            
            new_cache_type = cache_types[type_choice - 1]
            
            # TTL
            new_cache_ttl = self._validate_numeric_input("⏱️ TTL do cache (60-86400s): ", 60, 86400)
            if new_cache_ttl is None:
                return
            
            # Max size
            new_cache_max_size = self._validate_numeric_input("📏 Tamanho máximo (10-1000MB): ", 10, 1000)
            if new_cache_max_size is None:
                return
            
            # Cleanup interval
            new_cache_cleanup_interval = self._validate_numeric_input("🧹 Intervalo de limpeza (1-168h): ", 1, 168)
            if new_cache_cleanup_interval is None:
                return
        else:
            new_cache_type = current_cache_type
            new_cache_ttl = current_cache_ttl
            new_cache_max_size = current_cache_max_size
            new_cache_cleanup_interval = current_cache_cleanup_interval
        
        if self._confirm_action("atualizar configurações de cache"):
            success = True
            if new_cache_enabled != current_cache_enabled:
                success &= self._update_settings("CACHE_ENABLED", new_cache_enabled)
            if new_cache_type != current_cache_type:
                success &= self._update_settings("CACHE_TYPE", new_cache_type)
            if new_cache_ttl != current_cache_ttl:
                success &= self._update_settings("CACHE_TTL_SECONDS", new_cache_ttl)
            if new_cache_max_size != current_cache_max_size:
                success &= self._update_settings("CACHE_MAX_SIZE_MB", new_cache_max_size)
            if new_cache_cleanup_interval != current_cache_cleanup_interval:
                success &= self._update_settings("CACHE_CLEANUP_INTERVAL_HOURS", new_cache_cleanup_interval)
            
            if success:
                status = "ativado" if new_cache_enabled else "desativado"
                self.show_success(f"Cache {status}!")
    
    def _configure_security(self):
        """Configure security settings"""
        print("\n🔒 CONFIGURAR SEGURANÇA")
        print("═" * 26)
        
        current_security_enabled = self._get_setting("SECURITY_ENABLED", True)
        current_rate_limiting = self._get_setting("RATE_LIMITING", True)
        current_ip_whitelist = self._get_setting("IP_WHITELIST", [])
        current_api_key_required = self._get_setting("API_KEY_REQUIRED", False)
        current_encrypt_logs = self._get_setting("ENCRYPT_LOGS", False)
        
        print(f"Segurança atual: {'Ativada' if current_security_enabled else 'Desativada'}")
        print(f"Rate limiting atual: {'Ativado' if current_rate_limiting else 'Desativado'}")
        print(f"IP whitelist atual: {len(current_ip_whitelist)} IPs")
        print(f"API key obrigatória atual: {'Sim' if current_api_key_required else 'Não'}")
        print(f"Criptografia de logs atual: {'Ativada' if current_encrypt_logs else 'Desativada'}")
        
        new_security_enabled = self._validate_boolean_input("\n🔒 Ativar segurança? (s/n): ")
        if new_security_enabled is None:
            return
        
        if new_security_enabled:
            new_rate_limiting = self._validate_boolean_input("🚦 Ativar rate limiting? (s/n): ")
            if new_rate_limiting is None:
                return
            
            # IP whitelist
            configure_whitelist = self._validate_boolean_input("🌐 Configurar IP whitelist? (s/n): ")
            if configure_whitelist:
                print("\n📋 IPs atuais no whitelist:")
                for ip in current_ip_whitelist:
                    print(f"  - {ip}")
                
                whitelist_input = input("\n🌐 Digite os IPs separados por vírgula (deixe vazio para manter atual): ").strip()
                if whitelist_input:
                    new_ip_whitelist = [ip.strip() for ip in whitelist_input.split(",")]
                else:
                    new_ip_whitelist = current_ip_whitelist
            else:
                new_ip_whitelist = current_ip_whitelist
            
            new_api_key_required = self._validate_boolean_input("🔑 Exigir API key? (s/n): ")
            if new_api_key_required is None:
                return
            
            new_encrypt_logs = self._validate_boolean_input("🔐 Criptografar logs? (s/n): ")
            if new_encrypt_logs is None:
                return
        else:
            new_rate_limiting = False
            new_ip_whitelist = []
            new_api_key_required = False
            new_encrypt_logs = False
        
        if self._confirm_action("atualizar configurações de segurança"):
            success = True
            if new_security_enabled != current_security_enabled:
                success &= self._update_settings("SECURITY_ENABLED", new_security_enabled)
            if new_rate_limiting != current_rate_limiting:
                success &= self._update_settings("RATE_LIMITING", new_rate_limiting)
            if new_ip_whitelist != current_ip_whitelist:
                success &= self._update_settings("IP_WHITELIST", new_ip_whitelist)
            if new_api_key_required != current_api_key_required:
                success &= self._update_settings("API_KEY_REQUIRED", new_api_key_required)
            if new_encrypt_logs != current_encrypt_logs:
                success &= self._update_settings("ENCRYPT_LOGS", new_encrypt_logs)
            
            if success:
                status = "ativada" if new_security_enabled else "desativada"
                self.show_success(f"Segurança {status}!")
                
                if new_api_key_required and new_security_enabled:
                    self.show_info("💡 Lembre-se de configurar a API key nas variáveis de ambiente!")
    
    def _configure_monitoring(self):
        """Configure monitoring settings"""
        print("\n📊 CONFIGURAR MONITORAMENTO")
        print("═" * 32)
        
        current_monitoring_enabled = self._get_setting("MONITORING_ENABLED", False)
        current_metrics_endpoint = self._get_setting("METRICS_ENDPOINT", "http://localhost:8080/metrics")
        current_health_check_interval = self._get_setting("HEALTH_CHECK_INTERVAL_SECONDS", 30)
        current_alert_on_errors = self._get_setting("ALERT_ON_ERRORS", True)
        current_performance_monitoring = self._get_setting("PERFORMANCE_MONITORING", True)
        
        print(f"Monitoramento atual: {'Ativado' if current_monitoring_enabled else 'Desativado'}")
        print(f"Endpoint de métricas atual: {current_metrics_endpoint}")
        print(f"Intervalo de health check atual: {current_health_check_interval}s")
        print(f"Alertas de erro atual: {'Ativados' if current_alert_on_errors else 'Desativados'}")
        print(f"Monitoramento de performance atual: {'Ativado' if current_performance_monitoring else 'Desativado'}")
        
        new_monitoring_enabled = self._validate_boolean_input("\n📊 Ativar monitoramento? (s/n): ")
        if new_monitoring_enabled is None:
            return
        
        if new_monitoring_enabled:
            new_metrics_endpoint = input(f"\n📡 Endpoint de métricas (atual: {current_metrics_endpoint}): ").strip()
            if not new_metrics_endpoint:
                new_metrics_endpoint = current_metrics_endpoint
            
            new_health_check_interval = self._validate_numeric_input("💓 Intervalo de health check (10-300s): ", 10, 300)
            if new_health_check_interval is None:
                return
            
            new_alert_on_errors = self._validate_boolean_input("🚨 Alertar sobre erros? (s/n): ")
            if new_alert_on_errors is None:
                return
            
            new_performance_monitoring = self._validate_boolean_input("⚡ Monitorar performance? (s/n): ")
            if new_performance_monitoring is None:
                return
        else:
            new_metrics_endpoint = current_metrics_endpoint
            new_health_check_interval = current_health_check_interval
            new_alert_on_errors = False
            new_performance_monitoring = False
        
        if self._confirm_action("atualizar configurações de monitoramento"):
            success = True
            if new_monitoring_enabled != current_monitoring_enabled:
                success &= self._update_settings("MONITORING_ENABLED", new_monitoring_enabled)
            if new_metrics_endpoint != current_metrics_endpoint:
                success &= self._update_settings("METRICS_ENDPOINT", new_metrics_endpoint)
            if new_health_check_interval != current_health_check_interval:
                success &= self._update_settings("HEALTH_CHECK_INTERVAL_SECONDS", new_health_check_interval)
            if new_alert_on_errors != current_alert_on_errors:
                success &= self._update_settings("ALERT_ON_ERRORS", new_alert_on_errors)
            if new_performance_monitoring != current_performance_monitoring:
                success &= self._update_settings("PERFORMANCE_MONITORING", new_performance_monitoring)
            
            if success:
                status = "ativado" if new_monitoring_enabled else "desativado"
                self.show_success(f"Monitoramento {status}!")
    
    def _configure_webhooks(self):
        """Configure webhook settings"""
        print("\n🔗 CONFIGURAR WEBHOOKS")
        print("═" * 25)
        
        current_webhooks_enabled = self._get_setting("WEBHOOKS_ENABLED", False)
        current_webhook_urls = self._get_setting("WEBHOOK_URLS", [])
        current_webhook_events = self._get_setting("WEBHOOK_EVENTS", ["scraping_completed", "error_occurred"])
        current_webhook_timeout = self._get_setting("WEBHOOK_TIMEOUT_SECONDS", 10)
        current_webhook_retries = self._get_setting("WEBHOOK_RETRIES", 3)
        
        print(f"Webhooks atual: {'Ativados' if current_webhooks_enabled else 'Desativados'}")
        print(f"URLs configuradas atual: {len(current_webhook_urls)}")
        print(f"Eventos configurados atual: {len(current_webhook_events)}")
        print(f"Timeout atual: {current_webhook_timeout}s")
        print(f"Tentativas atual: {current_webhook_retries}")
        
        new_webhooks_enabled = self._validate_boolean_input("\n🔗 Ativar webhooks? (s/n): ")
        if new_webhooks_enabled is None:
            return
        
        if new_webhooks_enabled:
            # Configure URLs
            print("\n📋 URLs atuais:")
            for i, url in enumerate(current_webhook_urls, 1):
                print(f"  {i}. {url}")
            
            configure_urls = self._validate_boolean_input("\n🔗 Configurar URLs? (s/n): ")
            if configure_urls:
                urls_input = input("📝 Digite as URLs separadas por vírgula: ").strip()
                if urls_input:
                    new_webhook_urls = [url.strip() for url in urls_input.split(",")]
                else:
                    new_webhook_urls = current_webhook_urls
            else:
                new_webhook_urls = current_webhook_urls
            
            # Configure events
            available_events = [
                "scraping_started", "scraping_completed", "scraping_failed",
                "error_occurred", "warning_occurred", "restaurant_processed",
                "products_extracted", "system_startup", "system_shutdown"
            ]
            
            print("\n📋 Eventos disponíveis:")
            for i, event in enumerate(available_events, 1):
                print(f"  {i}. {event}")
            
            configure_events = self._validate_boolean_input("\n🔔 Configurar eventos? (s/n): ")
            if configure_events:
                events_input = input("📝 Digite os números dos eventos separados por vírgula: ").strip()
                if events_input:
                    try:
                        event_indices = [int(x.strip()) - 1 for x in events_input.split(",")]
                        new_webhook_events = [available_events[i] for i in event_indices if 0 <= i < len(available_events)]
                    except ValueError:
                        self.show_error("Formato inválido para eventos")
                        return
                else:
                    new_webhook_events = current_webhook_events
            else:
                new_webhook_events = current_webhook_events
            
            new_webhook_timeout = self._validate_numeric_input("⏱️ Timeout para webhooks (1-60s): ", 1, 60)
            if new_webhook_timeout is None:
                return
            
            new_webhook_retries = self._validate_numeric_input("🔄 Número de tentativas (1-10): ", 1, 10)
            if new_webhook_retries is None:
                return
        else:
            new_webhook_urls = []
            new_webhook_events = []
            new_webhook_timeout = current_webhook_timeout
            new_webhook_retries = current_webhook_retries
        
        if self._confirm_action("atualizar configurações de webhooks"):
            success = True
            if new_webhooks_enabled != current_webhooks_enabled:
                success &= self._update_settings("WEBHOOKS_ENABLED", new_webhooks_enabled)
            if new_webhook_urls != current_webhook_urls:
                success &= self._update_settings("WEBHOOK_URLS", new_webhook_urls)
            if new_webhook_events != current_webhook_events:
                success &= self._update_settings("WEBHOOK_EVENTS", new_webhook_events)
            if new_webhook_timeout != current_webhook_timeout:
                success &= self._update_settings("WEBHOOK_TIMEOUT_SECONDS", new_webhook_timeout)
            if new_webhook_retries != current_webhook_retries:
                success &= self._update_settings("WEBHOOK_RETRIES", new_webhook_retries)
            
            if success:
                status = "ativados" if new_webhooks_enabled else "desativados"
                self.show_success(f"Webhooks {status}!")
    
    def _configure_advanced(self):
        """Configure advanced system settings"""
        print("\n⚙️ CONFIGURAÇÕES AVANÇADAS")
        print("═" * 35)
        
        options = [
            "1. 🔧 Configurar modo de desenvolvimento",
            "2. 📈 Configurar profiling",
            "3. 🌍 Configurar internacionalização",
            "4. 🔌 Configurar plugins",
            "5. 🎛️ Configurar variáveis de ambiente"
        ]
        
        for option in options:
            print(f"  {option}")
        
        choice = self._validate_numeric_input("\n⚙️ Escolha uma opção (1-5): ", 1, 5)
        
        if choice == 1:
            self._configure_development_mode()
        elif choice == 2:
            self._configure_profiling()
        elif choice == 3:
            self._configure_internationalization()
        elif choice == 4:
            self._configure_plugins()
        elif choice == 5:
            self._configure_environment_variables()
    
    def _configure_development_mode(self):
        """Configure development mode settings"""
        print("\n🔧 MODO DE DESENVOLVIMENTO")
        print("═" * 32)
        
        current_dev_mode = self._get_setting("DEVELOPMENT_MODE", False)
        current_hot_reload = self._get_setting("HOT_RELOAD", False)
        current_debug_toolbar = self._get_setting("DEBUG_TOOLBAR", False)
        
        print(f"Modo desenvolvimento atual: {'Ativado' if current_dev_mode else 'Desativado'}")
        print(f"Hot reload atual: {'Ativado' if current_hot_reload else 'Desativado'}")
        print(f"Debug toolbar atual: {'Ativado' if current_debug_toolbar else 'Desativado'}")
        
        new_dev_mode = self._validate_boolean_input("\n🔧 Ativar modo de desenvolvimento? (s/n): ")
        if new_dev_mode is None:
            return
        
        if new_dev_mode:
            new_hot_reload = self._validate_boolean_input("🔄 Ativar hot reload? (s/n): ")
            if new_hot_reload is None:
                return
            
            new_debug_toolbar = self._validate_boolean_input("🛠️ Ativar debug toolbar? (s/n): ")
            if new_debug_toolbar is None:
                return
        else:
            new_hot_reload = False
            new_debug_toolbar = False
        
        if self._confirm_action("atualizar configurações de desenvolvimento"):
            success = True
            if new_dev_mode != current_dev_mode:
                success &= self._update_settings("DEVELOPMENT_MODE", new_dev_mode)
            if new_hot_reload != current_hot_reload:
                success &= self._update_settings("HOT_RELOAD", new_hot_reload)
            if new_debug_toolbar != current_debug_toolbar:
                success &= self._update_settings("DEBUG_TOOLBAR", new_debug_toolbar)
            
            if success:
                status = "ativado" if new_dev_mode else "desativado"
                self.show_success(f"Modo de desenvolvimento {status}!")
    
    def _configure_profiling(self):
        """Configure profiling settings"""
        current_profiling = self._get_setting("PROFILING_ENABLED", False)
        
        print(f"\n📈 Profiling atual: {'Ativado' if current_profiling else 'Desativado'}")
        
        new_profiling = self._validate_boolean_input("📈 Ativar profiling? (s/n): ")
        if new_profiling is None:
            return
        
        if new_profiling != current_profiling:
            if self._update_settings("PROFILING_ENABLED", new_profiling):
                status = "ativado" if new_profiling else "desativado"
                self.show_success(f"Profiling {status}!")
    
    def _configure_internationalization(self):
        """Configure internationalization settings"""
        current_language = self._get_setting("LANGUAGE", "pt_BR")
        current_timezone = self._get_setting("TIMEZONE", "America/Sao_Paulo")
        
        print(f"\n🌍 Idioma atual: {current_language}")
        print(f"🕒 Fuso horário atual: {current_timezone}")
        
        languages = ["pt_BR", "en_US", "es_ES"]
        print("\n🌍 Idiomas disponíveis:")
        for i, lang in enumerate(languages, 1):
            print(f"  {i}. {lang}")
        
        lang_choice = self._validate_numeric_input("🌍 Escolha o idioma (1-3): ", 1, 3)
        if lang_choice is None:
            return
        
        new_language = languages[lang_choice - 1]
        
        new_timezone = input(f"\n🕒 Novo fuso horário (atual: {current_timezone}): ").strip()
        if not new_timezone:
            new_timezone = current_timezone
        
        if self._confirm_action("atualizar configurações de internacionalização"):
            success = True
            if new_language != current_language:
                success &= self._update_settings("LANGUAGE", new_language)
            if new_timezone != current_timezone:
                success &= self._update_settings("TIMEZONE", new_timezone)
            
            if success:
                self.show_success("Configurações de internacionalização atualizadas!")
    
    def _configure_plugins(self):
        """Configure plugin settings"""
        current_plugins_enabled = self._get_setting("PLUGINS_ENABLED", True)
        current_plugin_dir = self._get_setting("PLUGIN_DIR", "plugins")
        current_enabled_plugins = self._get_setting("ENABLED_PLUGINS", [])
        
        print(f"\n🔌 Plugins atual: {'Ativados' if current_plugins_enabled else 'Desativados'}")
        print(f"📁 Diretório de plugins atual: {current_plugin_dir}")
        print(f"🔧 Plugins habilitados atual: {len(current_enabled_plugins)}")
        
        new_plugins_enabled = self._validate_boolean_input("🔌 Ativar sistema de plugins? (s/n): ")
        if new_plugins_enabled is None:
            return
        
        if new_plugins_enabled:
            new_plugin_dir = input(f"\n📁 Diretório de plugins (atual: {current_plugin_dir}): ").strip()
            if not new_plugin_dir:
                new_plugin_dir = current_plugin_dir
            
            # Create plugin directory if it doesn't exist
            Path(new_plugin_dir).mkdir(parents=True, exist_ok=True)
        else:
            new_plugin_dir = current_plugin_dir
        
        if self._confirm_action("atualizar configurações de plugins"):
            success = True
            if new_plugins_enabled != current_plugins_enabled:
                success &= self._update_settings("PLUGINS_ENABLED", new_plugins_enabled)
            if new_plugin_dir != current_plugin_dir:
                success &= self._update_settings("PLUGIN_DIR", new_plugin_dir)
            
            if success:
                status = "ativados" if new_plugins_enabled else "desativados"
                self.show_success(f"Sistema de plugins {status}!")
    
    def _configure_environment_variables(self):
        """Configure environment variables"""
        print("\n🎛️ VARIÁVEIS DE AMBIENTE")
        print("═" * 32)
        
        print("📝 Opções:")
        print("  1. Visualizar variáveis")
        print("  2. Adicionar variável")
        print("  3. Remover variável")
        print("  4. Exportar variáveis")
        
        choice = self._validate_numeric_input("🎛️ Escolha uma opção (1-4): ", 1, 4)
        
        if choice == 1:
            self._view_environment_variables()
        elif choice == 2:
            self._add_environment_variable()
        elif choice == 3:
            self._remove_environment_variable()
        elif choice == 4:
            self._export_environment_variables()
    
    def _view_environment_variables(self):
        """View current environment variables"""
        print("\n📋 VARIÁVEIS DE AMBIENTE")
        print("═" * 32)
        
        if not self.env_file.exists():
            self.show_warning("Arquivo .env não encontrado")
            return
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        print(f"  {line_num:2d}. {line}")
        except Exception as e:
            self.show_error(f"Erro ao ler arquivo .env: {e}")
    
    def _add_environment_variable(self):
        """Add new environment variable"""
        var_name = input("\n🏷️ Nome da variável: ").strip().upper()
        if not var_name:
            self.show_error("Nome da variável não pode ser vazio")
            return
        
        var_value = input("💎 Valor da variável: ").strip()
        if not var_value:
            self.show_error("Valor da variável não pode ser vazio")
            return
        
        if self._confirm_action(f"adicionar variável {var_name}"):
            if self._update_env_file(var_name, var_value):
                self.show_success(f"Variável {var_name} adicionada!")
    
    def _remove_environment_variable(self):
        """Remove environment variable"""
        var_name = input("\n🏷️ Nome da variável para remover: ").strip().upper()
        if not var_name:
            return
        
        if self._confirm_action(f"remover variável {var_name}"):
            if self._update_env_file(var_name, ""):
                self.show_success(f"Variável {var_name} removida!")
    
    def _export_environment_variables(self):
        """Export environment variables to file"""
        export_file = input("\n📁 Arquivo para exportar (ex: env_backup.txt): ").strip()
        if not export_file:
            return
        
        if self._confirm_action(f"exportar variáveis para {export_file}"):
            try:
                if self.env_file.exists():
                    with open(self.env_file, 'r', encoding='utf-8') as source:
                        with open(export_file, 'w', encoding='utf-8') as target:
                            target.write(f"# Backup das variáveis de ambiente - {datetime.now()}\n")
                            target.write(source.read())
                    
                    self.show_success(f"Variáveis exportadas para {export_file}")
                else:
                    self.show_error("Arquivo .env não encontrado")
            except Exception as e:
                self.show_error(f"Erro ao exportar: {e}")
    
    def _system_cleanup(self):
        """System cleanup operations"""
        print("\n🧹 LIMPEZA DO SISTEMA")
        print("═" * 26)
        
        options = [
            "1. 🗑️ Limpar logs antigos",
            "2. 🗄️ Limpar cache",
            "3. 📁 Limpar arquivos temporários",
            "4. 🔄 Limpar dados de sessão",
            "5. 🧹 Limpeza completa"
        ]
        
        for option in options:
            print(f"  {option}")
        
        choice = self._validate_numeric_input("\n🧹 Escolha uma opção (1-5): ", 1, 5)
        
        if choice == 1:
            self._cleanup_logs()
        elif choice == 2:
            self._cleanup_cache()
        elif choice == 3:
            self._cleanup_temp_files()
        elif choice == 4:
            self._cleanup_session_data()
        elif choice == 5:
            self._full_cleanup()
    
    def _cleanup_logs(self):
        """Clean up old log files"""
        logs_dir = Path(self._get_setting("LOGS_DIR", "logs"))
        retention_days = self._get_setting("LOG_RETENTION_DAYS", 30)
        
        if not logs_dir.exists():
            self.show_warning("Diretório de logs não encontrado")
            return
        
        if self._confirm_action(f"limpar logs com mais de {retention_days} dias"):
            try:
                from datetime import datetime, timedelta
                
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                removed_count = 0
                
                for log_file in logs_dir.rglob("*.log*"):
                    if log_file.is_file():
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            log_file.unlink()
                            removed_count += 1
                
                self.show_success(f"Removidos {removed_count} arquivos de log antigos!")
                
            except Exception as e:
                self.show_error(f"Erro ao limpar logs: {e}")
    
    def _cleanup_cache(self):
        """Clean up cache files"""
        cache_dir = Path(self._get_setting("CACHE_DIR", "cache"))
        
        if not cache_dir.exists():
            self.show_warning("Diretório de cache não encontrado")
            return
        
        if self._confirm_action("limpar todos os arquivos de cache"):
            try:
                import shutil
                
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
                
                self.show_success("Cache limpo com sucesso!")
                
            except Exception as e:
                self.show_error(f"Erro ao limpar cache: {e}")
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        temp_dirs = ["tmp", "temp", ".tmp"]
        
        if self._confirm_action("limpar arquivos temporários"):
            try:
                removed_count = 0
                
                for temp_dir in temp_dirs:
                    temp_path = Path(temp_dir)
                    if temp_path.exists():
                        for temp_file in temp_path.rglob("*"):
                            if temp_file.is_file():
                                temp_file.unlink()
                                removed_count += 1
                
                self.show_success(f"Removidos {removed_count} arquivos temporários!")
                
            except Exception as e:
                self.show_error(f"Erro ao limpar arquivos temporários: {e}")
    
    def _cleanup_session_data(self):
        """Clean up session data"""
        if self._confirm_action("limpar dados de sessão"):
            try:
                # Reset session stats
                self.session_stats = {
                    'restaurants_scraped': 0,
                    'products_categorized': 0,
                    'errors': 0,
                    'session_start': datetime.now().isoformat()
                }
                
                self.show_success("Dados de sessão limpos!")
                
            except Exception as e:
                self.show_error(f"Erro ao limpar dados de sessão: {e}")
    
    def _full_cleanup(self):
        """Perform full system cleanup"""
        if self._confirm_action("executar limpeza completa do sistema"):
            self.show_info("Executando limpeza completa...")
            
            try:
                self._cleanup_logs()
                self._cleanup_cache()
                self._cleanup_temp_files()
                self._cleanup_session_data()
                
                self.show_success("🎉 Limpeza completa do sistema concluída!")
                
            except Exception as e:
                self.show_error(f"Erro durante limpeza completa: {e}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system configuration statistics"""
        stats = self.get_base_statistics()
        
        # Configuration status
        stats.update({
            'log_level': self._get_setting("LOG_LEVEL", "INFO"),
            'cache_enabled': self._get_setting("CACHE_ENABLED", True),
            'security_enabled': self._get_setting("SECURITY_ENABLED", True),
            'monitoring_enabled': self._get_setting("MONITORING_ENABLED", False),
            'webhooks_enabled': self._get_setting("WEBHOOKS_ENABLED", False),
            'development_mode': self._get_setting("DEVELOPMENT_MODE", False),
            'plugins_enabled': self._get_setting("PLUGINS_ENABLED", True),
            'language': self._get_setting("LANGUAGE", "pt_BR"),
            'timezone': self._get_setting("TIMEZONE", "America/Sao_Paulo")
        })
        
        # Log file size
        log_file = Path(self._get_setting("LOG_FILE", "logs/app.log"))
        if log_file.exists():
            stats['log_file_size'] = log_file.stat().st_size
        else:
            stats['log_file_size'] = 0
        
        # Cache size
        cache_dir = Path(self._get_setting("CACHE_DIR", "cache"))
        if cache_dir.exists():
            stats['cache_size'] = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
        else:
            stats['cache_size'] = 0
        
        return stats