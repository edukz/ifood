#!/usr/bin/env python3
"""
Reports Module - Modular reporting system for iFood scraper
"""

from .reports_base import ReportsBase
from .categories_report import CategoriesReport
from .restaurants_report import RestaurantsReport
from .products_report import ProductsReport
from .price_analysis import PriceAnalysis
from .performance_report import PerformanceReport
from .custom_report import CustomReport
from .export_manager import ExportManager
from .reports_manager import ReportsManager

__all__ = [
    'ReportsBase',
    'CategoriesReport',
    'RestaurantsReport', 
    'ProductsReport',
    'PriceAnalysis',
    'PerformanceReport',
    'CustomReport',
    'ExportManager',
    'ReportsManager'
]

__version__ = '3.0.0'