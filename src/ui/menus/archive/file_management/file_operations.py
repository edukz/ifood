#!/usr/bin/env python3
"""
Operações básicas de arquivos
"""

import os
import shutil
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

from tools.archive_manager import ArchiveManager
from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu
from .file_search import FileSearch


class FileOperations(BaseMenu):
    """Operações básicas de gerenciamento de arquivos"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path, 
                 archive_manager: ArchiveManager):
        super().__init__("Operações de Arquivo", session_stats, data_dir)
        self.archive_manager = archive_manager
        self.db = get_database_manager()
        self.file_search = FileSearch(session_stats, data_dir, archive_manager)
    
    def manage_data_files(self):
        """Gerenciar arquivos de dados"""
        print("\n📁 GERENCIAMENTO DE ARQUIVOS DE DADOS")
        print("=" * 50)
        
        # Analisar estrutura atual
        print("📊 ESTRUTURA ATUAL DE ARQUIVOS:")
        
        try:
            # Verificar diretórios principais
            main_dirs = ["data", "logs", "cache", "archive", "temp"]
            for dir_name in main_dirs:
                dir_path = Path(dir_name)
                if dir_path.exists():
                    file_count = len(list(dir_path.rglob("*")))
                    size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
                    print(f"  📁 {dir_name}/: {file_count} arquivos, {self._format_size(size)}")
                else:
                    print(f"  📁 {dir_name}/: Não existe")
            
            # Opções de gerenciamento
            options = [
                "1. 📋 Listar arquivos detalhadamente",
                "2. 🔍 Buscar arquivos específicos",
                "3. 📦 Mover arquivos para arquivo",
                "4. 🗑️ Deletar arquivos",
                "5. 💾 Salvar lista de arquivos",
                "6. 🧹 Remover arquivos desnecessários"
            ]
            
            self.show_menu("📁 OPÇÕES DE GERENCIAMENTO", options)
            choice = self.get_user_choice(6)
            
            if choice == "1":
                self._list_files_detailed()
            elif choice == "2":
                self.file_search.search_specific_files()
            elif choice == "3":
                self._move_files_to_archive()
            elif choice == "4":
                self._delete_files()
            elif choice == "5":
                self._save_file_list()
            elif choice == "6":
                self._remove_unnecessary_files()
            
        except Exception as e:
            self.show_error(f"Erro no gerenciamento de arquivos: {e}")
        
        self.pause()
    
    def _list_files_detailed(self):
        """Listar arquivos detalhadamente"""
        print("\n📋 LISTAGEM DETALHADA DE ARQUIVOS")
        print("-" * 50)
        
        try:
            # Escolher diretório
            directories = ["data", "logs", "cache", "archive", "temp"]
            dir_choice = self._get_directory_choice(directories)
            
            if dir_choice:
                dir_path = Path(dir_choice)
                if dir_path.exists():
                    files = list(dir_path.rglob("*"))
                    files = [f for f in files if f.is_file()]
                    
                    if files:
                        print(f"\n📁 Arquivos em {dir_choice}:")
                        for file in files[:20]:  # Limitar a 20 arquivos
                            stat = file.stat()
                            size = self._format_size(stat.st_size)
                            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                            print(f"  📄 {file.name} ({size}) - {modified}")
                        
                        if len(files) > 20:
                            print(f"  ... e mais {len(files) - 20} arquivos")
                    else:
                        print(f"  📁 Diretório {dir_choice} está vazio")
                else:
                    print(f"  ❌ Diretório {dir_choice} não existe")
            
        except Exception as e:
            self.show_error(f"Erro na listagem: {e}")
    
    def _move_files_to_archive(self):
        """Mover arquivos para arquivo"""
        print("\n📦 MOVER ARQUIVOS PARA ARQUIVO")
        print("-" * 50)
        
        try:
            # Criar diretório de arquivo se não existir
            archive_dir = Path("archive")
            archive_dir.mkdir(exist_ok=True)
            
            # Critérios para arquivamento
            criteria_options = [
                "1. 📅 Arquivos mais antigos que X dias",
                "2. 📊 Arquivos maiores que X MB",
                "3. 🏷️ Arquivos de tipo específico",
                "4. 📁 Arquivos de diretório específico"
            ]
            
            self.show_menu("📦 CRITÉRIOS DE ARQUIVAMENTO", criteria_options)
            choice = self.get_user_choice(4)
            
            if choice == "1":
                self._archive_by_age()
            elif choice == "2":
                self._archive_by_size()
            elif choice == "3":
                self._archive_by_type()
            elif choice == "4":
                self._archive_by_directory()
            
        except Exception as e:
            self.show_error(f"Erro no arquivamento: {e}")
    
    def _delete_files(self):
        """Deletar arquivos"""
        print("\n🗑️ DELETAR ARQUIVOS")
        print("-" * 50)
        
        try:
            # Verificar arquivos temporários
            temp_dirs = ["temp", "cache", "logs"]
            files_to_delete = []
            
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    temp_files = list(temp_path.rglob("*"))
                    temp_files = [f for f in temp_files if f.is_file()]
                    files_to_delete.extend(temp_files)
            
            if files_to_delete:
                print(f"📋 Encontrados {len(files_to_delete)} arquivos temporários:")
                for file in files_to_delete[:10]:  # Mostrar apenas 10
                    size = self._format_size(file.stat().st_size)
                    print(f"  🗑️ {file} ({size})")
                
                if len(files_to_delete) > 10:
                    print(f"  ... e mais {len(files_to_delete) - 10} arquivos")
                
                # Confirmar deleção
                confirm = input("\n⚠️ Deletar estes arquivos? (s/N): ").strip().lower()
                if confirm in ['s', 'sim']:
                    deleted_count = 0
                    for file in files_to_delete:
                        try:
                            file.unlink()
                            deleted_count += 1
                        except Exception as e:
                            print(f"❌ Erro ao deletar {file}: {e}")
                    
                    print(f"✅ {deleted_count} arquivos deletados com sucesso")
                else:
                    print("❌ Operação cancelada")
            else:
                print("📋 Nenhum arquivo temporário encontrado")
            
        except Exception as e:
            self.show_error(f"Erro na deleção: {e}")
    
    def _save_file_list(self):
        """Salvar lista de arquivos"""
        print("\n💾 SALVAR LISTA DE ARQUIVOS")
        print("-" * 50)
        
        try:
            # Escolher diretório
            directories = ["data", "logs", "cache", "archive"]
            dir_choice = self._get_directory_choice(directories)
            
            if dir_choice:
                dir_path = Path(dir_choice)
                if dir_path.exists():
                    files = list(dir_path.rglob("*"))
                    files = [f for f in files if f.is_file()]
                    
                    # Salvar lista
                    output_file = Path(f"file_list_{dir_choice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"Lista de arquivos - {dir_choice}\n")
                        f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Total de arquivos: {len(files)}\n")
                        f.write("-" * 50 + "\n\n")
                        
                        for file in files:
                            stat = file.stat()
                            size = self._format_size(stat.st_size)
                            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                            f.write(f"{file} ({size}) - {modified}\n")
                    
                    print(f"✅ Lista salva em: {output_file}")
                else:
                    print(f"❌ Diretório {dir_choice} não existe")
            
        except Exception as e:
            self.show_error(f"Erro ao salvar lista: {e}")
    
    def _remove_unnecessary_files(self):
        """Remover arquivos desnecessários"""
        print("\n🧹 REMOVER ARQUIVOS DESNECESSÁRIOS")
        print("-" * 50)
        
        try:
            # Padrões de arquivos desnecessários
            patterns = [
                "*.tmp", "*.temp", "*.log", "*.bak", "*.old",
                "*.cache", "*.swp", "*.~*", ".DS_Store", "Thumbs.db"
            ]
            
            found_files = []
            for pattern in patterns:
                files = list(Path(".").rglob(pattern))
                found_files.extend(files)
            
            if found_files:
                print(f"📋 Encontrados {len(found_files)} arquivos desnecessários:")
                total_size = 0
                for file in found_files[:10]:  # Mostrar apenas 10
                    size = file.stat().st_size
                    total_size += size
                    print(f"  🗑️ {file} ({self._format_size(size)})")
                
                if len(found_files) > 10:
                    print(f"  ... e mais {len(found_files) - 10} arquivos")
                
                print(f"\n📊 Espaço total a ser liberado: {self._format_size(total_size)}")
                
                # Confirmar remoção
                confirm = input("\n⚠️ Remover estes arquivos? (s/N): ").strip().lower()
                if confirm in ['s', 'sim']:
                    removed_count = 0
                    freed_space = 0
                    
                    for file in found_files:
                        try:
                            size = file.stat().st_size
                            file.unlink()
                            removed_count += 1
                            freed_space += size
                        except Exception as e:
                            print(f"❌ Erro ao remover {file}: {e}")
                    
                    print(f"✅ {removed_count} arquivos removidos")
                    print(f"💾 Espaço liberado: {self._format_size(freed_space)}")
                else:
                    print("❌ Operação cancelada")
            else:
                print("📋 Nenhum arquivo desnecessário encontrado")
            
        except Exception as e:
            self.show_error(f"Erro na remoção: {e}")
    
    def search_files(self):
        """Buscar arquivos"""
        self.file_search.search_files()
    
    # Métodos auxiliares
    def _get_directory_choice(self, directories: List[str]) -> str:
        """Obter escolha de diretório"""
        print("\n📁 Escolha o diretório:")
        for i, dir_name in enumerate(directories, 1):
            print(f"  {i}. {dir_name}")
        
        try:
            choice = int(input("\nEscolha: ").strip())
            if 1 <= choice <= len(directories):
                return directories[choice - 1]
        except ValueError:
            pass
        
        return ""
    
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
    
    def _archive_by_age(self):
        """Arquivar por idade"""
        print("📅 Arquivar arquivos por idade - Funcionalidade em desenvolvimento")
    
    def _archive_by_size(self):
        """Arquivar por tamanho"""
        print("📊 Arquivar arquivos por tamanho - Funcionalidade em desenvolvimento")
    
    def _archive_by_type(self):
        """Arquivar por tipo"""
        print("🏷️ Arquivar arquivos por tipo - Funcionalidade em desenvolvimento")
    
    def _archive_by_directory(self):
        """Arquivar por diretório"""
        print("📁 Arquivar arquivos por diretório - Funcionalidade em desenvolvimento")