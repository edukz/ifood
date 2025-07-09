#!/usr/bin/env python3
"""
Scraping Configuration - Worker, retry, browser, and performance settings
"""

from typing import Dict, Any
from pathlib import Path

from .config_base import ConfigBase


class ScrapingConfig(ConfigBase):
    """Scraping configuration management"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Configuração de Scraping", session_stats, data_dir)
    
    def show_scraping_menu(self):
        """Show scraping configuration menu"""
        current_config = {
            "Workers": "MAX_WORKERS",
            "Retry máximo": "MAX_RETRIES",
            "Modo headless": "HEADLESS_MODE",
            "Debug mode": "DEBUG_MODE",
            "Coleta de métricas": "COLLECT_METRICS"
        }
        
        options = [
            "1. 👥 Configurar workers",
            "2. 🔄 Configurar retry",
            "3. 🌐 Configurar navegador",
            "4. 🐛 Configurar debug",
            "5. 📊 Configurar métricas",
            "6. ⚡ Configurar performance",
            "7. 🎯 Configurar filtros"
        ]
        
        self._show_config_menu("🕷️ CONFIGURAÇÕES DE SCRAPING", options, current_config)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._configure_workers()
        elif choice == "2":
            self._configure_retry()
        elif choice == "3":
            self._configure_browser()
        elif choice == "4":
            self._configure_debug()
        elif choice == "5":
            self._configure_metrics()
        elif choice == "6":
            self._configure_performance()
        elif choice == "7":
            self._configure_filters()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _configure_workers(self):
        """Configure worker settings"""
        print("\n👥 CONFIGURAR WORKERS")
        print("═" * 25)
        
        current_max_workers = self._get_setting("MAX_WORKERS", 3)
        current_parallel_restaurants = self._get_setting("PARALLEL_RESTAURANTS", 2)
        current_parallel_products = self._get_setting("PARALLEL_PRODUCTS", 1)
        
        print(f"Workers máximos atual: {current_max_workers}")
        print(f"Restaurantes paralelos atual: {current_parallel_restaurants}")
        print(f"Produtos paralelos atual: {current_parallel_products}")
        
        new_max_workers = self._validate_numeric_input("\n👥 Novo número máximo de workers (1-10): ", 1, 10)
        if new_max_workers is None:
            return
        
        new_parallel_restaurants = self._validate_numeric_input("🏪 Novo número de restaurantes paralelos (1-5): ", 1, 5)
        if new_parallel_restaurants is None:
            return
        
        new_parallel_products = self._validate_numeric_input("📦 Novo número de produtos paralelos (1-3): ", 1, 3)
        if new_parallel_products is None:
            return
        
        # Validate relationships
        if new_parallel_restaurants > new_max_workers:
            self.show_error("Restaurantes paralelos não pode ser maior que workers máximos")
            return
        
        if self._confirm_action("atualizar configurações de workers"):
            success = True
            if new_max_workers != current_max_workers:
                success &= self._update_settings("MAX_WORKERS", new_max_workers)
            if new_parallel_restaurants != current_parallel_restaurants:
                success &= self._update_settings("PARALLEL_RESTAURANTS", new_parallel_restaurants)
            if new_parallel_products != current_parallel_products:
                success &= self._update_settings("PARALLEL_PRODUCTS", new_parallel_products)
            
            if success:
                self.show_success("Configurações de workers atualizadas!")
    
    def _configure_retry(self):
        """Configure retry settings"""
        print("\n🔄 CONFIGURAR RETRY")
        print("═" * 23)
        
        current_max_retries = self._get_setting("MAX_RETRIES", 3)
        current_retry_delay = self._get_setting("RETRY_DELAY", 5.0)
        current_exponential_backoff = self._get_setting("EXPONENTIAL_BACKOFF", True)
        current_retry_on_timeout = self._get_setting("RETRY_ON_TIMEOUT", True)
        
        print(f"Máximo de tentativas atual: {current_max_retries}")
        print(f"Delay entre tentativas atual: {current_retry_delay}s")
        print(f"Backoff exponencial atual: {'Ativado' if current_exponential_backoff else 'Desativado'}")
        print(f"Retry em timeout atual: {'Ativado' if current_retry_on_timeout else 'Desativado'}")
        
        new_max_retries = self._validate_numeric_input("\n🔄 Novo máximo de tentativas (1-10): ", 1, 10)
        if new_max_retries is None:
            return
        
        try:
            new_retry_delay = float(input("⏳ Novo delay entre tentativas (0.5-60.0s): ") or current_retry_delay)
            if not 0.5 <= new_retry_delay <= 60.0:
                self.show_error("Delay deve estar entre 0.5 e 60.0 segundos")
                return
        except ValueError:
            self.show_error("Por favor, insira um valor numérico válido")
            return
        
        new_exponential_backoff = self._validate_boolean_input("📈 Ativar backoff exponencial? (s/n): ")
        if new_exponential_backoff is None:
            return
        
        new_retry_on_timeout = self._validate_boolean_input("⏱️ Tentar novamente em timeout? (s/n): ")
        if new_retry_on_timeout is None:
            return
        
        if self._confirm_action("atualizar configurações de retry"):
            success = True
            if new_max_retries != current_max_retries:
                success &= self._update_settings("MAX_RETRIES", new_max_retries)
            if new_retry_delay != current_retry_delay:
                success &= self._update_settings("RETRY_DELAY", new_retry_delay)
            if new_exponential_backoff != current_exponential_backoff:
                success &= self._update_settings("EXPONENTIAL_BACKOFF", new_exponential_backoff)
            if new_retry_on_timeout != current_retry_on_timeout:
                success &= self._update_settings("RETRY_ON_TIMEOUT", new_retry_on_timeout)
            
            if success:
                self.show_success("Configurações de retry atualizadas!")
    
    def _configure_browser(self):
        """Configure browser settings"""
        print("\n🌐 CONFIGURAR NAVEGADOR")
        print("═" * 28)
        
        current_headless = self._get_setting("HEADLESS_MODE", True)
        current_browser_type = self._get_setting("BROWSER_TYPE", "chromium")
        current_window_size = self._get_setting("WINDOW_SIZE", "1920x1080")
        current_disable_images = self._get_setting("DISABLE_IMAGES", False)
        current_disable_javascript = self._get_setting("DISABLE_JAVASCRIPT", False)
        
        print(f"Modo headless atual: {'Ativado' if current_headless else 'Desativado'}")
        print(f"Tipo de navegador atual: {current_browser_type}")
        print(f"Tamanho da janela atual: {current_window_size}")
        print(f"Desabilitar imagens atual: {'Sim' if current_disable_images else 'Não'}")
        print(f"Desabilitar JavaScript atual: {'Sim' if current_disable_javascript else 'Não'}")
        
        new_headless = self._validate_boolean_input("\n🌐 Ativar modo headless? (s/n): ")
        if new_headless is None:
            return
        
        # Browser type
        browsers = ["chromium", "firefox", "webkit"]
        print("\n🌐 Tipos de navegador disponíveis:")
        for i, browser in enumerate(browsers, 1):
            print(f"  {i}. {browser}")
        
        browser_choice = self._validate_numeric_input("🌐 Escolha o navegador (1-3): ", 1, 3)
        if browser_choice is None:
            return
        
        new_browser_type = browsers[browser_choice - 1]
        
        # Window size
        sizes = ["1920x1080", "1366x768", "1280x720", "1024x768"]
        print("\n📏 Tamanhos de janela disponíveis:")
        for i, size in enumerate(sizes, 1):
            print(f"  {i}. {size}")
        
        size_choice = self._validate_numeric_input("📏 Escolha o tamanho (1-4): ", 1, 4)
        if size_choice is None:
            return
        
        new_window_size = sizes[size_choice - 1]
        
        new_disable_images = self._validate_boolean_input("🖼️ Desabilitar carregamento de imagens? (s/n): ")
        if new_disable_images is None:
            return
        
        new_disable_javascript = self._validate_boolean_input("⚙️ Desabilitar JavaScript? (s/n): ")
        if new_disable_javascript is None:
            return
        
        if self._confirm_action("atualizar configurações do navegador"):
            success = True
            if new_headless != current_headless:
                success &= self._update_settings("HEADLESS_MODE", new_headless)
            if new_browser_type != current_browser_type:
                success &= self._update_settings("BROWSER_TYPE", new_browser_type)
            if new_window_size != current_window_size:
                success &= self._update_settings("WINDOW_SIZE", new_window_size)
            if new_disable_images != current_disable_images:
                success &= self._update_settings("DISABLE_IMAGES", new_disable_images)
            if new_disable_javascript != current_disable_javascript:
                success &= self._update_settings("DISABLE_JAVASCRIPT", new_disable_javascript)
            
            if success:
                self.show_success("Configurações do navegador atualizadas!")
    
    def _configure_debug(self):
        """Configure debug settings"""
        print("\n🐛 CONFIGURAR DEBUG")
        print("═" * 23)
        
        current_debug_mode = self._get_setting("DEBUG_MODE", False)
        current_save_screenshots = self._get_setting("SAVE_SCREENSHOTS", False)
        current_save_html = self._get_setting("SAVE_HTML", False)
        current_verbose_logging = self._get_setting("VERBOSE_LOGGING", False)
        
        print(f"Modo debug atual: {'Ativado' if current_debug_mode else 'Desativado'}")
        print(f"Salvar screenshots atual: {'Sim' if current_save_screenshots else 'Não'}")
        print(f"Salvar HTML atual: {'Sim' if current_save_html else 'Não'}")
        print(f"Logging verboso atual: {'Ativado' if current_verbose_logging else 'Desativado'}")
        
        new_debug_mode = self._validate_boolean_input("\n🐛 Ativar modo debug? (s/n): ")
        if new_debug_mode is None:
            return
        
        if new_debug_mode:
            new_save_screenshots = self._validate_boolean_input("📸 Salvar screenshots em erros? (s/n): ")
            if new_save_screenshots is None:
                return
            
            new_save_html = self._validate_boolean_input("📄 Salvar HTML em erros? (s/n): ")
            if new_save_html is None:
                return
            
            new_verbose_logging = self._validate_boolean_input("📝 Ativar logging verboso? (s/n): ")
            if new_verbose_logging is None:
                return
        else:
            new_save_screenshots = False
            new_save_html = False
            new_verbose_logging = False
        
        if self._confirm_action("atualizar configurações de debug"):
            success = True
            if new_debug_mode != current_debug_mode:
                success &= self._update_settings("DEBUG_MODE", new_debug_mode)
            if new_save_screenshots != current_save_screenshots:
                success &= self._update_settings("SAVE_SCREENSHOTS", new_save_screenshots)
            if new_save_html != current_save_html:
                success &= self._update_settings("SAVE_HTML", new_save_html)
            if new_verbose_logging != current_verbose_logging:
                success &= self._update_settings("VERBOSE_LOGGING", new_verbose_logging)
            
            if success:
                status = "ativado" if new_debug_mode else "desativado"
                self.show_success(f"Modo debug {status}!")
    
    def _configure_metrics(self):
        """Configure metrics collection settings"""
        print("\n📊 CONFIGURAR MÉTRICAS")
        print("═" * 26)
        
        current_collect_metrics = self._get_setting("COLLECT_METRICS", True)
        current_save_metrics = self._get_setting("SAVE_METRICS", True)
        current_metrics_interval = self._get_setting("METRICS_INTERVAL", 60)
        current_performance_tracking = self._get_setting("PERFORMANCE_TRACKING", True)
        
        print(f"Coleta de métricas atual: {'Ativada' if current_collect_metrics else 'Desativada'}")
        print(f"Salvar métricas atual: {'Sim' if current_save_metrics else 'Não'}")
        print(f"Intervalo de métricas atual: {current_metrics_interval}s")
        print(f"Rastreamento de performance atual: {'Ativado' if current_performance_tracking else 'Desativado'}")
        
        new_collect_metrics = self._validate_boolean_input("\n📊 Ativar coleta de métricas? (s/n): ")
        if new_collect_metrics is None:
            return
        
        if new_collect_metrics:
            new_save_metrics = self._validate_boolean_input("💾 Salvar métricas em arquivo? (s/n): ")
            if new_save_metrics is None:
                return
            
            new_metrics_interval = self._validate_numeric_input("⏱️ Intervalo de coleta (10-3600s): ", 10, 3600)
            if new_metrics_interval is None:
                return
            
            new_performance_tracking = self._validate_boolean_input("⚡ Ativar rastreamento de performance? (s/n): ")
            if new_performance_tracking is None:
                return
        else:
            new_save_metrics = False
            new_metrics_interval = current_metrics_interval
            new_performance_tracking = False
        
        if self._confirm_action("atualizar configurações de métricas"):
            success = True
            if new_collect_metrics != current_collect_metrics:
                success &= self._update_settings("COLLECT_METRICS", new_collect_metrics)
            if new_save_metrics != current_save_metrics:
                success &= self._update_settings("SAVE_METRICS", new_save_metrics)
            if new_metrics_interval != current_metrics_interval:
                success &= self._update_settings("METRICS_INTERVAL", new_metrics_interval)
            if new_performance_tracking != current_performance_tracking:
                success &= self._update_settings("PERFORMANCE_TRACKING", new_performance_tracking)
            
            if success:
                status = "ativada" if new_collect_metrics else "desativada"
                self.show_success(f"Coleta de métricas {status}!")
    
    def _configure_performance(self):
        """Configure performance settings"""
        print("\n⚡ CONFIGURAR PERFORMANCE")
        print("═" * 30)
        
        current_page_timeout = self._get_setting("PAGE_TIMEOUT", 30000)
        current_element_timeout = self._get_setting("ELEMENT_TIMEOUT", 10000)
        current_scroll_delay = self._get_setting("SCROLL_DELAY", 1.0)
        current_max_pages_per_restaurant = self._get_setting("MAX_PAGES_PER_RESTAURANT", 50)
        
        print(f"Timeout de página atual: {current_page_timeout}ms")
        print(f"Timeout de elemento atual: {current_element_timeout}ms")
        print(f"Delay de scroll atual: {current_scroll_delay}s")
        print(f"Máximo de páginas por restaurante atual: {current_max_pages_per_restaurant}")
        
        new_page_timeout = self._validate_numeric_input("\n⏱️ Novo timeout de página (5000-120000ms): ", 5000, 120000)
        if new_page_timeout is None:
            return
        
        new_element_timeout = self._validate_numeric_input("🔍 Novo timeout de elemento (1000-30000ms): ", 1000, 30000)
        if new_element_timeout is None:
            return
        
        try:
            new_scroll_delay = float(input("📜 Novo delay de scroll (0.1-10.0s): ") or current_scroll_delay)
            if not 0.1 <= new_scroll_delay <= 10.0:
                self.show_error("Delay deve estar entre 0.1 e 10.0 segundos")
                return
        except ValueError:
            self.show_error("Por favor, insira um valor numérico válido")
            return
        
        new_max_pages = self._validate_numeric_input("📄 Máximo de páginas por restaurante (1-200): ", 1, 200)
        if new_max_pages is None:
            return
        
        if self._confirm_action("atualizar configurações de performance"):
            success = True
            if new_page_timeout != current_page_timeout:
                success &= self._update_settings("PAGE_TIMEOUT", new_page_timeout)
            if new_element_timeout != current_element_timeout:
                success &= self._update_settings("ELEMENT_TIMEOUT", new_element_timeout)
            if new_scroll_delay != current_scroll_delay:
                success &= self._update_settings("SCROLL_DELAY", new_scroll_delay)
            if new_max_pages != current_max_pages_per_restaurant:
                success &= self._update_settings("MAX_PAGES_PER_RESTAURANT", new_max_pages)
            
            if success:
                self.show_success("Configurações de performance atualizadas!")
    
    def _configure_filters(self):
        """Configure scraping filters"""
        print("\n🎯 CONFIGURAR FILTROS")
        print("═" * 25)
        
        current_min_rating = self._get_setting("MIN_RATING", 0.0)
        current_max_distance = self._get_setting("MAX_DISTANCE_KM", 50.0)
        current_categories_filter = self._get_setting("CATEGORIES_FILTER", [])
        current_skip_closed = self._get_setting("SKIP_CLOSED_RESTAURANTS", True)
        
        print(f"Avaliação mínima atual: {current_min_rating}")
        print(f"Distância máxima atual: {current_max_distance}km")
        print(f"Filtro de categorias atual: {current_categories_filter or 'Nenhum'}")
        print(f"Pular fechados atual: {'Sim' if current_skip_closed else 'Não'}")
        
        try:
            new_min_rating = float(input("\n⭐ Nova avaliação mínima (0.0-5.0): ") or current_min_rating)
            if not 0.0 <= new_min_rating <= 5.0:
                self.show_error("Avaliação deve estar entre 0.0 e 5.0")
                return
        except ValueError:
            self.show_error("Por favor, insira um valor numérico válido")
            return
        
        try:
            new_max_distance = float(input("📍 Nova distância máxima (0.1-100.0km): ") or current_max_distance)
            if not 0.1 <= new_max_distance <= 100.0:
                self.show_error("Distância deve estar entre 0.1 e 100.0km")
                return
        except ValueError:
            self.show_error("Por favor, insira um valor numérico válido")
            return
        
        # Categories filter
        configure_categories = self._validate_boolean_input("🍽️ Configurar filtro de categorias? (s/n): ")
        if configure_categories:
            categories_input = input("📝 Digite as categorias separadas por vírgula (ex: pizza,hamburguer): ").strip()
            if categories_input:
                new_categories_filter = [cat.strip() for cat in categories_input.split(",")]
            else:
                new_categories_filter = []
        else:
            new_categories_filter = current_categories_filter
        
        new_skip_closed = self._validate_boolean_input("🚫 Pular restaurantes fechados? (s/n): ")
        if new_skip_closed is None:
            return
        
        if self._confirm_action("atualizar configurações de filtros"):
            success = True
            if new_min_rating != current_min_rating:
                success &= self._update_settings("MIN_RATING", new_min_rating)
            if new_max_distance != current_max_distance:
                success &= self._update_settings("MAX_DISTANCE_KM", new_max_distance)
            if new_categories_filter != current_categories_filter:
                success &= self._update_settings("CATEGORIES_FILTER", new_categories_filter)
            if new_skip_closed != current_skip_closed:
                success &= self._update_settings("SKIP_CLOSED_RESTAURANTS", new_skip_closed)
            
            if success:
                self.show_success("Configurações de filtros atualizadas!")
    
    def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get scraping configuration statistics"""
        stats = self.get_base_statistics()
        
        # Configuration status
        stats.update({
            'max_workers': self._get_setting("MAX_WORKERS", 3),
            'max_retries': self._get_setting("MAX_RETRIES", 3),
            'headless_mode': self._get_setting("HEADLESS_MODE", True),
            'debug_mode': self._get_setting("DEBUG_MODE", False),
            'collect_metrics': self._get_setting("COLLECT_METRICS", True),
            'browser_type': self._get_setting("BROWSER_TYPE", "chromium"),
            'performance_settings': {
                'page_timeout': self._get_setting("PAGE_TIMEOUT", 30000),
                'element_timeout': self._get_setting("ELEMENT_TIMEOUT", 10000),
                'scroll_delay': self._get_setting("SCROLL_DELAY", 1.0)
            },
            'filters': {
                'min_rating': self._get_setting("MIN_RATING", 0.0),
                'max_distance': self._get_setting("MAX_DISTANCE_KM", 50.0),
                'categories_filter': self._get_setting("CATEGORIES_FILTER", []),
                'skip_closed': self._get_setting("SKIP_CLOSED_RESTAURANTS", True)
            }
        })
        
        return stats