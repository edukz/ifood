#!/usr/bin/env python3
"""
Analisador de espaço
"""

from typing import Dict, List, Any
from pathlib import Path

from tools.archive_manager import ArchiveManager
from src.ui.base_menu import BaseMenu


class SpaceAnalyzer(BaseMenu):
    """Analisador de uso de espaço em disco"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path, 
                 archive_manager: ArchiveManager):
        super().__init__("Análise de Espaço", session_stats, data_dir)
        self.archive_manager = archive_manager
    
    def space_analysis(self):
        """Análise de uso de espaço"""
        print("\n📊 ANÁLISE DE USO DE ESPAÇO")
        print("=" * 50)
        
        try:
            # Analisar diretórios principais
            directories = ["data", "logs", "cache", "archive", "temp"]
            
            print("📁 USO DE ESPAÇO POR DIRETÓRIO:")
            total_size = 0
            
            for dir_name in directories:
                dir_path = Path(dir_name)
                if dir_path.exists():
                    size = self._get_directory_size(dir_path)
                    total_size += size
                    file_count = len(list(dir_path.rglob("*")))
                    print(f"  📁 {dir_name}: {self._format_size(size)} ({file_count} arquivos)")
                else:
                    print(f"  📁 {dir_name}: Não existe")
            
            print(f"\n📊 TOTAL GERAL: {self._format_size(total_size)}")
            
            # Maiores arquivos
            print("\n🔍 MAIORES ARQUIVOS:")
            large_files = self._find_large_files()
            for file in large_files[:10]:
                size = self._format_size(file.stat().st_size)
                print(f"  📄 {file.name}: {size}")
            
        except Exception as e:
            self.show_error(f"Erro na análise: {e}")
        
        self.pause()
    
    def _get_directory_size(self, path: Path) -> int:
        """Obter tamanho total de um diretório"""
        total_size = 0
        try:
            for file in path.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
        except Exception:
            pass
        return total_size
    
    def _find_large_files(self, min_size_mb: int = 1) -> List[Path]:
        """Encontrar arquivos grandes"""
        min_size = min_size_mb * 1024 * 1024
        large_files = []
        
        for file in Path(".").rglob("*"):
            if file.is_file():
                try:
                    if file.stat().st_size >= min_size:
                        large_files.append(file)
                except Exception:
                    pass
        
        # Ordenar por tamanho (maior primeiro)
        large_files.sort(key=lambda f: f.stat().st_size, reverse=True)
        return large_files
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatar tamanho de arquivo"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"