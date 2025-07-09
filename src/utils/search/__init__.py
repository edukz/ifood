#!/usr/bin/env python3
"""
Search Module - Sistema modular de otimização de busca e análise de dados
"""

from .database_manager import SearchDatabaseManager
from .query_engine import SearchQueryEngine
from .analytics_engine import SearchAnalyticsEngine

__all__ = ['SearchDatabaseManager', 'SearchQueryEngine', 'SearchAnalyticsEngine']