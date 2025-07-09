#!/usr/bin/env python3
"""
Scraper Status - Scraper monitoring and dependencies
"""

import os
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .status_base import StatusBase


class ScraperStatus(StatusBase):
    """Scraper monitoring and dependencies"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Status dos Scrapers", session_stats, data_dir)
    
    def show_scrapers_status(self):
        """Show comprehensive scrapers status"""
        print("\n🔍 STATUS DOS SCRAPERS")
        print("═" * 50)
        
        # Scrapers configuration
        self._show_scrapers_config()
        
        # Scrapers health
        self._show_scrapers_health()
        
        # Dependencies check
        self._show_dependencies_check()
        
        # Connectivity test
        self._show_connectivity_test()
        
        # Recent scraping activity
        self._show_recent_activity()
    
    def _show_scrapers_config(self):
        """Display scrapers configuration"""
        print("\n⚙️ CONFIGURAÇÕES ATUAIS:")
        
        try:
            from src.config.settings import SETTINGS
            scraping_config = SETTINGS.get('scraping', {})
            
            print(f"  Timeout: {scraping_config.get('timeout', 30)} segundos")
            print(f"  Delay: {scraping_config.get('delay', 1)} segundos")
            print(f"  Workers: {scraping_config.get('max_workers', 3)}")
            print(f"  Modo headless: {scraping_config.get('headless', True)}")
            print(f"  Retry habilitado: {scraping_config.get('retry', {}).get('enabled', True)}")
            print(f"  Max retries: {scraping_config.get('retry', {}).get('max_retries', 3)}")
            
        except Exception as e:
            self.show_error(f"Erro ao obter configurações: {e}")
    
    def _show_scrapers_health(self):
        """Display scrapers health status"""
        print("\n🏥 SAÚDE DOS SCRAPERS:")
        
        try:
            # Check for recent errors in logs
            error_count = 0
            warning_count = 0
            
            log_file = Path("logs") / f"ifood_scraper_{datetime.now().strftime('%Y%m%d')}.log"
            
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        error_count = content.count('ERROR')
                        warning_count = content.count('WARNING')
                    
                    if error_count == 0 and warning_count == 0:
                        print("  ✅ Nenhum erro ou aviso encontrado")
                    else:
                        print(f"  ⚠️ Erros encontrados: {error_count}")
                        print(f"  ⚠️ Avisos encontrados: {warning_count}")
                        
                except Exception as e:
                    print(f"  ❌ Erro ao analisar logs: {e}")
            else:
                print("  ℹ️ Nenhum log encontrado para hoje")
            
        except Exception as e:
            self.show_error(f"Erro ao verificar saúde dos scrapers: {e}")
    
    def _show_dependencies_check(self):
        """Check scraper dependencies"""
        print("\n📦 VERIFICAÇÃO DE DEPENDÊNCIAS:")
        
        required_deps = [
            ('requests', 'HTTP requests'),
            ('beautifulsoup4', 'HTML parsing'),
            ('playwright', 'Browser automation'),
            ('selenium', 'Web driver'),
            ('lxml', 'XML/HTML processing'),
            ('fake_useragent', 'User agent rotation')
        ]
        
        missing_deps = []
        working_deps = []
        
        for dep, description in required_deps:
            try:
                __import__(dep)
                working_deps.append((dep, description))
            except ImportError:
                missing_deps.append((dep, description))
        
        # Show working dependencies
        if working_deps:
            print("  ✅ Dependências funcionais:")
            for dep, desc in working_deps:
                print(f"    • {dep}: {desc}")
        
        # Show missing dependencies
        if missing_deps:
            print("  ❌ Dependências faltando:")
            for dep, desc in missing_deps:
                print(f"    • {dep}: {desc}")
        
        # Check browser availability
        self._check_browser_availability()
    
    def _check_browser_availability(self):
        """Check browser availability for scraping"""
        print("\n🌐 VERIFICAÇÃO DE BROWSERS:")
        
        browsers = [
            ('Chrome', 'chrome'),
            ('Firefox', 'firefox'),
            ('Safari', 'safari'),
            ('Edge', 'msedge')
        ]
        
        available_browsers = []
        
        for browser_name, browser_cmd in browsers:
            try:
                # Try to import playwright and check browser
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    if browser_name.lower() == 'chrome':
                        browser = p.chromium.launch(headless=True)
                    elif browser_name.lower() == 'firefox':
                        browser = p.firefox.launch(headless=True)
                    else:
                        continue
                    
                    browser.close()
                    available_browsers.append(browser_name)
                    print(f"  ✅ {browser_name}: Disponível")
                    
            except Exception:
                print(f"  ❌ {browser_name}: Não disponível")
        
        if not available_browsers:
            print("  ⚠️ Nenhum browser disponível para scraping")
    
    def _show_connectivity_test(self):
        """Test connectivity for scraping"""
        print("\n🌐 TESTE DE CONECTIVIDADE:")
        
        test_urls = [
            ('iFood', 'https://www.ifood.com.br'),
            ('Google', 'https://www.google.com'),
            ('GitHub', 'https://github.com')
        ]
        
        connectivity_results = []
        
        for site_name, url in test_urls:
            try:
                import requests
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    connectivity_results.append((site_name, True, response.elapsed.total_seconds()))
                    print(f"  ✅ {site_name}: OK ({response.elapsed.total_seconds():.2f}s)")
                else:
                    connectivity_results.append((site_name, False, 0))
                    print(f"  ❌ {site_name}: Erro {response.status_code}")
                    
            except Exception as e:
                connectivity_results.append((site_name, False, 0))
                print(f"  ❌ {site_name}: {e}")
        
        # Calculate average response time
        successful_tests = [result for result in connectivity_results if result[1]]
        if successful_tests:
            avg_response_time = sum(result[2] for result in successful_tests) / len(successful_tests)
            print(f"  ⏱️ Tempo médio de resposta: {avg_response_time:.2f}s")
    
    def _show_recent_activity(self):
        """Show recent scraping activity"""
        print("\n📈 ATIVIDADE RECENTE:")
        
        try:
            # Session statistics
            print("  📊 Estatísticas da sessão:")
            print(f"    • Categorias extraídas: {self.session_stats.get('categories_extracted', 0)}")
            print(f"    • Restaurantes extraídos: {self.session_stats.get('restaurants_extracted', 0)}")
            print(f"    • Produtos extraídos: {self.session_stats.get('products_extracted', 0)}")
            print(f"    • Erros encontrados: {self.session_stats.get('errors', 0)}")
            
            # Calculate session duration
            session_start = self.session_stats.get('session_start')
            if session_start:
                if isinstance(session_start, str):
                    session_start = datetime.fromisoformat(session_start)
                
                duration = datetime.now() - session_start
                print(f"    • Duração da sessão: {self.format_duration(duration.total_seconds())}")
            
            # Recent database updates
            self._show_recent_database_updates()
            
        except Exception as e:
            self.show_error(f"Erro ao obter atividade recente: {e}")
    
    def _show_recent_database_updates(self):
        """Show recent database updates"""
        print("\n  📊 Atualizações recentes no banco:")
        
        try:
            # Check recent restaurants
            recent_restaurants = self.safe_execute_query("""
                SELECT COUNT(*) as count 
                FROM restaurants 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
            """, fetch_one=True)
            
            if recent_restaurants:
                print(f"    • Restaurantes nas últimas 24h: {recent_restaurants[0]}")
            
            # Check recent products
            recent_products = self.safe_execute_query("""
                SELECT COUNT(*) as count 
                FROM products 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
            """, fetch_one=True)
            
            if recent_products:
                print(f"    • Produtos nas últimas 24h: {recent_products[0]}")
            
            # Check recent categories
            recent_categories = self.safe_execute_query("""
                SELECT COUNT(*) as count 
                FROM categories 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
            """, fetch_one=True)
            
            if recent_categories:
                print(f"    • Categorias nas últimas 24h: {recent_categories[0]}")
                
        except Exception as e:
            self.show_error(f"Erro ao obter atualizações do banco: {e}")
    
    def get_scraper_statistics(self) -> Dict[str, Any]:
        """Get scraper status statistics"""
        stats = self.get_base_statistics()
        
        # Add scraper-specific statistics
        stats['scraper_config'] = self._get_scraper_config()
        stats['dependencies_status'] = self._get_dependencies_status()
        stats['connectivity_status'] = self._get_connectivity_status()
        stats['recent_activity'] = self._get_recent_activity_stats()
        
        return stats
    
    def _get_scraper_config(self) -> Dict[str, Any]:
        """Get scraper configuration"""
        try:
            from src.config.settings import SETTINGS
            return SETTINGS.get('scraping', {})
        except Exception:
            return {}
    
    def _get_dependencies_status(self) -> Dict[str, bool]:
        """Get dependencies status"""
        required_deps = ['requests', 'beautifulsoup4', 'playwright', 'selenium', 'lxml']
        
        status = {}
        for dep in required_deps:
            try:
                __import__(dep)
                status[dep] = True
            except ImportError:
                status[dep] = False
        
        return status
    
    def _get_connectivity_status(self) -> Dict[str, Any]:
        """Get connectivity status"""
        return {
            'internet_available': self.test_connectivity(),
            'ifood_reachable': self.test_connectivity('www.ifood.com.br', 443),
            'last_check': datetime.now().isoformat()
        }
    
    def _get_recent_activity_stats(self) -> Dict[str, Any]:
        """Get recent activity statistics"""
        return {
            'categories_extracted': self.session_stats.get('categories_extracted', 0),
            'restaurants_extracted': self.session_stats.get('restaurants_extracted', 0),
            'products_extracted': self.session_stats.get('products_extracted', 0),
            'errors': self.session_stats.get('errors', 0),
            'session_start': self.session_stats.get('session_start', datetime.now().isoformat())
        }