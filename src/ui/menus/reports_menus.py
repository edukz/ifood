#!/usr/bin/env python3
"""
Sistema de Relatórios - Interface unificada para sistema modular de relatórios
Refatorado para usar arquitetura modular v3.0
"""

from typing import Dict, Any
from pathlib import Path

from src.ui.base_menu import BaseMenu
from .reports import ReportsManager


class ReportsMenus(BaseMenu):
    """Interface unificada para sistema modular de relatórios"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Relatórios", session_stats, data_dir)
        self.reports_manager = ReportsManager(session_stats, data_dir)
    
    def menu_reports(self):
        """Menu principal de relatórios - delegado para o ReportsManager"""
        self.reports_manager.menu_reports()
    
    def _categories_report(self):
        """Relatório detalhado de categorias - delegado para CategoriesReport"""
        self.reports_manager.generate_categories_report()
        self.pause()
    
    def _restaurants_report(self):
        """Relatório detalhado de restaurantes - delegado para RestaurantsReport"""
        self.reports_manager.generate_restaurants_report()
        self.pause()
    
    def _products_report(self):
        """Relatório detalhado de produtos - delegado para ProductsReport"""
        self.reports_manager.generate_products_report()
        self.pause()
    
    def _price_analysis(self):
        """Análise detalhada de preços - delegado para PriceAnalysis"""
        self.reports_manager.generate_price_analysis()
        self.pause()
    
    def _performance_report(self):
        """Relatório de performance do sistema - delegado para PerformanceReport"""
        self.reports_manager.generate_performance_report()
        self.pause()
    
    def _custom_report(self):
        """Relatório personalizado - delegado para CustomReport"""
        self.reports_manager.generate_custom_report()
        self.pause()
    
    def _export_data(self):
        """Exportar dados - delegado para ExportManager"""
        self.reports_manager.show_export_menu()
        self.pause()
    
    # Backward compatibility methods - all functionality moved to specialized modules
    # These methods are kept for any external code that might call them directly
    
    def get_reports_statistics(self) -> Dict[str, Any]:
        """Get comprehensive reports statistics"""
        return self.reports_manager.get_manager_statistics()
    
    def export_all_reports(self, format: str = 'json') -> Dict[str, str]:
        """Export all reports in specified format"""
        return self.reports_manager.export_all_reports(format)
    
    def get_quick_overview(self) -> Dict[str, Any]:
        """Get quick overview of all data"""
        return self.reports_manager.get_quick_overview()
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        return self.reports_manager.generate_executive_summary()