#!/usr/bin/env python3
"""
Sistema de Arquivos - Interface compatível com a estrutura modular
"""

from typing import Dict, List, Any
from pathlib import Path

from tools.archive_manager import ArchiveManager
from .archive import ArchiveMenus as ModularArchiveMenus


class ArchiveMenus:
    """Interface compatível para o sistema de arquivos modular"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path, 
                 archive_manager: ArchiveManager):
        # Usar a implementação modular
        self.modular_archive = ModularArchiveMenus(session_stats, data_dir, archive_manager)
    
    def menu_file_management(self):
        """Menu principal de gerenciamento de arquivos"""
        return self.modular_archive.menu_file_management()
    
    def _cleanup_files(self):
        """Delegado para limpeza de arquivos"""
        return self.modular_archive._cleanup_files()
    
    def _compress_files(self):
        """Delegado para compactação"""
        return self.modular_archive._compress_files()
    
    def _remove_unnecessary_files(self):
        """Delegado para remoção de arquivos desnecessários"""
        return self.modular_archive._remove_unnecessary_files()