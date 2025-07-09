#!/usr/bin/env python3
"""
Menu Principal do Sistema de Arquivos
"""

from typing import Dict, List, Any
from pathlib import Path

from tools.archive_manager import ArchiveManager
from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu

# Importar módulos especializados
from .file_management.file_operations import FileOperations
from .archiving.archive_operations import ArchiveOperations
from .cleanup.cleanup_operations import CleanupOperations
from .organization.directory_organizer import DirectoryOrganizer
from .reports.space_analyzer import SpaceAnalyzer


class ArchiveMenus(BaseMenu):
    """Menu principal para gerenciamento de arquivos e dados"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path, 
                 archive_manager: ArchiveManager):
        super().__init__("Arquivo", session_stats, data_dir)
        self.archive_manager = archive_manager
        self.db = get_database_manager()
        
        # Inicializar módulos especializados
        self.file_ops = FileOperations(session_stats, data_dir, archive_manager)
        self.archive_ops = ArchiveOperations(session_stats, data_dir, archive_manager)
        self.cleanup_ops = CleanupOperations(session_stats, data_dir, archive_manager)
        self.organizer = DirectoryOrganizer(session_stats, data_dir, archive_manager)
        self.analyzer = SpaceAnalyzer(session_stats, data_dir, archive_manager)
    
    def menu_file_management(self):
        """Menu principal de gerenciamento de arquivos"""
        options = [
            "1. 📁 Gerenciar arquivos de dados",
            "2. 🗂️ Arquivar dados antigos",
            "3. 📦 Compactar arquivos",
            "4. 🔄 Restaurar arquivos",
            "5. 🧹 Limpeza de arquivos",
            "6. 📊 Análise de uso de espaço",
            "7. 🔍 Buscar arquivos",
            "8. 📋 Organizar diretórios"
        ]
        
        self.show_menu("📁 GERENCIAMENTO DE ARQUIVOS", options)
        choice = self.get_user_choice(8)
        
        if choice == "1":
            self.file_ops.manage_data_files()
        elif choice == "2":
            self.archive_ops.archive_old_data()
        elif choice == "3":
            self.archive_ops.compress_files()
        elif choice == "4":
            self.archive_ops.restore_files()
        elif choice == "5":
            self.cleanup_ops.cleanup_files()
        elif choice == "6":
            self.analyzer.space_analysis()
        elif choice == "7":
            self.file_ops.search_files()
        elif choice == "8":
            self.organizer.organize_directories()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    # Métodos auxiliares delegados
    def _cleanup_files(self):
        """Delegado para limpeza de arquivos"""
        self.cleanup_ops.cleanup_files()
    
    def _compress_files(self):
        """Delegado para compactação"""
        self.archive_ops.compress_files()
    
    def _remove_unnecessary_files(self):
        """Delegado para remoção de arquivos desnecessários"""
        self.cleanup_ops.remove_unnecessary_files()