import random
from typing import Dict, Any


class BrowserConfig:
    """Configurações para tornar o navegador mais humano"""
    
    @staticmethod
    def get_viewport():
        """Retorna viewport aleatório de resoluções comuns"""
        viewports = [
            {"width": 1920, "height": 1080},  # Full HD
            {"width": 1366, "height": 768},   # Laptop comum
            {"width": 1440, "height": 900},   # MacBook
            {"width": 1536, "height": 864},   # Surface
            {"width": 1600, "height": 900},   # Desktop
        ]
        return random.choice(viewports)
    
    @staticmethod
    def get_user_agent():
        """Retorna user agent aleatório"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def get_browser_context_options() -> Dict[str, Any]:
        """Retorna opções completas para o contexto do navegador"""
        viewport = BrowserConfig.get_viewport()
        
        return {
            "viewport": viewport,
            "user_agent": BrowserConfig.get_user_agent(),
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
            "permissions": ["geolocation"],
            "geolocation": {"latitude": -21.1767, "longitude": -47.8208},  # São Paulo
            "color_scheme": "light",
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False,
            "java_script_enabled": True,
            "accept_downloads": False,
            "extra_http_headers": {
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        }
    
    @staticmethod
    def get_launch_options(headless: bool = False) -> Dict[str, Any]:
        """Retorna opções para lançar o navegador"""
        return {
            "headless": headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=IsolateOrigins",
                "--disable-site-isolation-trials",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--start-maximized",
            ],
            "ignore_default_args": ["--enable-automation"],
        }