#!/usr/bin/env python3
"""
Reports Base - Base class for all report modules with common functionality
"""

import csv
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
# Optional import
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    def tabulate(data, headers=None, **kwargs):
        """Fallback function for when tabulate is not available"""
        if not data:
            return "Nenhum dado disponível"
        
        result = []
        if headers:
            result.append("\t".join(str(h) for h in headers))
            result.append("-" * 50)
        
        for row in data:
            if isinstance(row, dict):
                result.append("\t".join(str(row.get(h, '')) for h in (headers or row.keys())))
            else:
                result.append("\t".join(str(cell) for cell in row))
        
        return "\n".join(result)

from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu


class ReportsBase(BaseMenu):
    """Base class for report modules with common functionality"""
    
    def __init__(self, title: str, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__(title, session_stats, data_dir)
        self.db = get_database_manager()
        
        # Report formatting options
        self.table_format = 'grid'
        self.date_format = '%d/%m/%Y %H:%M'
        self.float_precision = 2
    
    def safe_execute_query(self, query: str, params: Tuple = None, fetch_one: bool = False) -> Optional[Any]:
        """
        Safely execute database query with error handling
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_one: Whether to fetch one or all results
            
        Returns:
            Query result or None if error
        """
        try:
            with self.db.get_cursor() as (cursor, _):
                cursor.execute(query, params or ())
                
                if fetch_one:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
                    
        except Exception as e:
            self.show_error(f"Erro na consulta SQL: {e}")
            return None
    
    def format_table(self, data: List[List[Any]], headers: List[str], title: str = None) -> None:
        """
        Format and display data in a table
        
        Args:
            data: Table data
            headers: Column headers
            title: Optional table title
        """
        if title:
            print(f"\n{title}:")
        
        if data:
            print(tabulate(data, headers=headers, tablefmt=self.table_format))
        else:
            print("Nenhum dado disponível")
    
    def format_currency(self, value: float) -> str:
        """Format currency values"""
        if value is None:
            return "N/A"
        return f"R$ {value:.{self.float_precision}f}"
    
    def format_percentage(self, value: float) -> str:
        """Format percentage values"""
        if value is None:
            return "N/A"
        return f"{value:.1f}%"
    
    def format_date(self, date_value: datetime) -> str:
        """Format date values"""
        if date_value is None:
            return "N/A"
        return date_value.strftime(self.date_format)
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str, fieldnames: List[str] = None) -> Path:
        """
        Export data to CSV file
        
        Args:
            data: Data to export
            filename: Base filename (timestamp will be added)
            fieldnames: CSV field names (auto-detected if None)
            
        Returns:
            Path to the created file
        """
        if not data:
            raise ValueError("No data to export")
        
        # Auto-detect fieldnames if not provided
        if not fieldnames:
            fieldnames = list(data[0].keys())
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        full_filename = f"{filename}_{timestamp}.csv"
        filepath = self.data_dir / full_filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Convert dict-like objects to regular dicts
                writer.writerow(dict(row))
        
        return filepath
    
    def export_to_json(self, data: Any, filename: str) -> Path:
        """
        Export data to JSON file
        
        Args:
            data: Data to export
            filename: Base filename (timestamp will be added)
            
        Returns:
            Path to the created file
        """
        # Add timestamp to filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        full_filename = f"{filename}_{timestamp}.json"
        filepath = self.data_dir / full_filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return filepath
    
    def build_dynamic_query(self, base_query: str, conditions: Dict[str, Any], 
                           allowed_fields: Dict[str, str] = None) -> Tuple[str, List[Any]]:
        """
        Build dynamic query with conditions
        
        Args:
            base_query: Base SQL query
            conditions: Filter conditions
            allowed_fields: Mapping of condition keys to SQL field names
            
        Returns:
            Tuple of (query, parameters)
        """
        where_clauses = []
        params = []
        
        if not allowed_fields:
            allowed_fields = {}
        
        for key, value in conditions.items():
            if value and key in allowed_fields:
                field_name = allowed_fields[key]
                where_clauses.append(f"{field_name} LIKE %s")
                params.append(f"%{value}%")
        
        if where_clauses:
            # Check if WHERE already exists in the query
            if 'WHERE' in base_query.upper():
                base_query += " AND " + " AND ".join(where_clauses)
            else:
                base_query += " WHERE " + " AND ".join(where_clauses)
        
        return base_query, params
    
    def calculate_statistics(self, data: List[Dict[str, Any]], numeric_fields: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Calculate basic statistics for numeric fields
        
        Args:
            data: Data to analyze
            numeric_fields: List of numeric field names
            
        Returns:
            Dictionary with statistics for each field
        """
        stats = {}
        
        for field in numeric_fields:
            values = [row[field] for row in data if row.get(field) is not None and row[field] > 0]
            
            if values:
                stats[field] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'total': sum(values)
                }
            else:
                stats[field] = {
                    'count': 0,
                    'min': 0,
                    'max': 0,
                    'avg': 0,
                    'total': 0
                }
        
        return stats
    
    def get_top_items(self, table: str, field: str, count_field: str = None, 
                     limit: int = 10, where_clause: str = None) -> List[Dict[str, Any]]:
        """
        Get top items by count from a table
        
        Args:
            table: Table name
            field: Field to group by
            count_field: Field to count (defaults to *)
            limit: Number of results to return
            where_clause: Optional WHERE clause
            
        Returns:
            List of top items with counts
        """
        count_expr = f"COUNT({count_field})" if count_field else "COUNT(*)"
        
        query = f"""
            SELECT {field}, {count_expr} as count
            FROM {table}
        """
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        query += f"""
            GROUP BY {field}
            ORDER BY count DESC
            LIMIT {limit}
        """
        
        return self.safe_execute_query(query) or []
    
    def get_date_range_data(self, table: str, date_field: str = 'created_at', 
                           days: int = 7) -> List[Dict[str, Any]]:
        """
        Get data grouped by date for the last N days
        
        Args:
            table: Table name
            date_field: Date field name
            days: Number of days to look back
            
        Returns:
            List of data grouped by date
        """
        query = f"""
            SELECT 
                DATE({date_field}) as date,
                COUNT(*) as count
            FROM {table}
            WHERE {date_field} >= DATE_SUB(NOW(), INTERVAL {days} DAY)
            GROUP BY DATE({date_field})
            ORDER BY date DESC
        """
        
        return self.safe_execute_query(query) or []
    
    def print_section_header(self, title: str):
        """Print a formatted section header"""
        print(f"\n{title}")
        print("═" * 50)
    
    def print_subsection_header(self, title: str):
        """Print a formatted subsection header"""
        print(f"\n{title}:")
    
    def get_base_statistics(self) -> Dict[str, Any]:
        """Get base statistics for reports"""
        return {
            'timestamp': datetime.now().isoformat(),
            'session_stats': self.session_stats,
            'report_generated_by': 'iFood Scraper Report System v3.0'
        }