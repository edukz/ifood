#!/usr/bin/env python3
"""
Operações de arquivamento
"""

import shutil
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime, timedelta

from tools.archive_manager import ArchiveManager
from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu
from .compression import CompressionManager


class ArchiveOperations(BaseMenu):
    """Operações de arquivamento e backup"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path, 
                 archive_manager: ArchiveManager):
        super().__init__("Arquivamento", session_stats, data_dir)
        self.archive_manager = archive_manager
        self.db = get_database_manager()
        self.compression = CompressionManager(session_stats, data_dir, archive_manager)
    
    def archive_old_data(self):
        """Arquivar dados antigos"""
        print("\n🗂️ ARQUIVAR DADOS ANTIGOS")
        print("=" * 50)
        
        try:
            # Criar diretório de arquivo
            archive_dir = Path("archive")
            archive_dir.mkdir(exist_ok=True)
            
            # Verificar arquivos antigos
            old_files = self._find_old_files()
            
            if old_files:
                print(f"📋 Encontrados {len(old_files)} arquivos antigos:")
                total_size = 0
                
                for file in old_files[:10]:  # Mostrar apenas 10
                    size = file.stat().st_size
                    total_size += size
                    age_days = (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days
                    print(f"  📄 {file.name} ({self._format_size(size)}) - {age_days} dias")
                
                if len(old_files) > 10:
                    print(f"  ... e mais {len(old_files) - 10} arquivos")
                
                print(f"\n📊 Espaço total: {self._format_size(total_size)}")
                
                # Opções de arquivamento
                options = [
                    "1. 📦 Mover para pasta archive/",
                    "2. 🗜️ Compactar e arquivar",
                    "3. 🗑️ Deletar arquivos antigos",
                    "4. 📅 Configurar critérios de idade"
                ]
                
                self.show_menu("🗂️ OPÇÕES DE ARQUIVAMENTO", options)
                choice = self.get_user_choice(4)
                
                if choice == "1":
                    self._move_to_archive(old_files)
                elif choice == "2":
                    self._compress_and_archive(old_files)
                elif choice == "3":
                    self._delete_old_files(old_files)
                elif choice == "4":
                    self._configure_age_criteria()
                
            else:
                print("📋 Nenhum arquivo antigo encontrado")
                
        except Exception as e:
            self.show_error(f"Erro no arquivamento: {e}")
        
        self.pause()
    
    def compress_files(self):
        """Compactar arquivos"""
        self.compression.compress_files()
    
    def restore_files(self):
        """Restaurar arquivos"""
        print("\n🔄 RESTAURAR ARQUIVOS")
        print("=" * 50)
        
        try:
            archive_dir = Path("archive")
            if not archive_dir.exists():
                print("❌ Diretório de archive não encontrado")
                return
            
            # Listar arquivos no archive
            archived_files = list(archive_dir.rglob("*"))
            archived_files = [f for f in archived_files if f.is_file()]
            
            if archived_files:
                print(f"📋 Encontrados {len(archived_files)} arquivos no archive:")
                
                for i, file in enumerate(archived_files[:20], 1):
                    size = self._format_size(file.stat().st_size)
                    modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"  {i}. {file.name} ({size}) - {modified}")
                
                if len(archived_files) > 20:
                    print(f"  ... e mais {len(archived_files) - 20} arquivos")
                
                # Opções de restauração
                options = [
                    "1. 📂 Restaurar arquivo específico",
                    "2. 📁 Restaurar por tipo",
                    "3. 📅 Restaurar por data",
                    "4. 🔄 Restaurar tudo"
                ]
                
                self.show_menu("🔄 OPÇÕES DE RESTAURAÇÃO", options)
                choice = self.get_user_choice(4)
                
                if choice == "1":
                    self._restore_specific_file(archived_files)
                elif choice == "2":
                    self._restore_by_type(archived_files)
                elif choice == "3":
                    self._restore_by_date(archived_files)
                elif choice == "4":
                    self._restore_all(archived_files)
                
            else:
                print("📋 Nenhum arquivo encontrado no archive")
                
        except Exception as e:
            self.show_error(f"Erro na restauração: {e}")
        
        self.pause()
    
    def _find_old_files(self, days_old: int = 30) -> List[Path]:
        """Encontrar arquivos antigos"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        old_files = []
        
        # Diretórios para verificar
        search_dirs = ["data", "logs", "cache", "temp"]
        
        for search_dir in search_dirs:
            dir_path = Path(search_dir)
            if dir_path.exists():
                files = list(dir_path.rglob("*"))
                files = [f for f in files if f.is_file()]
                
                for file in files:
                    mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                    if mod_time < cutoff_date:
                        old_files.append(file)
        
        return old_files
    
    def _move_to_archive(self, files: List[Path]):
        """Mover arquivos para archive"""
        try:
            archive_dir = Path("archive")
            archive_dir.mkdir(exist_ok=True)
            
            moved_count = 0
            for file in files:
                try:
                    # Manter estrutura de diretórios
                    relative_path = file.relative_to(Path.cwd())
                    archive_path = archive_dir / relative_path
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.move(str(file), str(archive_path))
                    moved_count += 1
                    
                except Exception as e:
                    print(f"❌ Erro ao mover {file}: {e}")
            
            print(f"✅ {moved_count} arquivos movidos para archive")
            
        except Exception as e:
            self.show_error(f"Erro ao mover arquivos: {e}")
    
    def _compress_and_archive(self, files: List[Path]):
        """Compactar e arquivar"""
        try:
            archive_dir = Path("archive")
            archive_dir.mkdir(exist_ok=True)
            
            # Criar arquivo compactado
            archive_name = f"old_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            archive_path = archive_dir / archive_name
            
            self.compression.create_zip_archive(files, archive_path)
            
            # Remover arquivos originais após compactação
            confirm = input("🗑️ Remover arquivos originais após compactação? (s/N): ").strip().lower()
            if confirm in ['s', 'sim']:
                removed_count = 0
                for file in files:
                    try:
                        file.unlink()
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Erro ao remover {file}: {e}")
                
                print(f"✅ {removed_count} arquivos removidos")
            
        except Exception as e:
            self.show_error(f"Erro na compactação: {e}")
    
    def _delete_old_files(self, files: List[Path]):
        """Deletar arquivos antigos"""
        try:
            print(f"⚠️ Esta operação irá deletar {len(files)} arquivos permanentemente!")
            confirm = input("Tem certeza? Digite 'CONFIRMAR' para prosseguir: ").strip()
            
            if confirm == 'CONFIRMAR':
                deleted_count = 0
                freed_space = 0
                
                for file in files:
                    try:
                        size = file.stat().st_size
                        file.unlink()
                        deleted_count += 1
                        freed_space += size
                    except Exception as e:
                        print(f"❌ Erro ao deletar {file}: {e}")
                
                print(f"✅ {deleted_count} arquivos deletados")
                print(f"💾 Espaço liberado: {self._format_size(freed_space)}")
            else:
                print("❌ Operação cancelada")
                
        except Exception as e:
            self.show_error(f"Erro na deleção: {e}")
    
    def _configure_age_criteria(self):
        """Configurar critérios de idade"""
        print("\n📅 CONFIGURAR CRITÉRIOS DE IDADE")
        print("-" * 40)
        
        try:
            current_days = 30  # Valor padrão
            print(f"Critério atual: arquivos mais antigos que {current_days} dias")
            
            new_days = input("Digite o novo critério em dias (Enter para manter): ").strip()
            if new_days:
                new_days = int(new_days)
                print(f"✅ Novo critério: {new_days} dias")
                # Aqui você salvaria a configuração
            else:
                print("✅ Critério mantido")
                
        except ValueError:
            print("❌ Valor inválido")
        except Exception as e:
            self.show_error(f"Erro na configuração: {e}")
    
    def _restore_specific_file(self, files: List[Path]):
        """Restaurar arquivo específico"""
        print("\n📂 RESTAURAR ARQUIVO ESPECÍFICO")
        print("-" * 40)
        
        try:
            # Mostrar lista numerada
            print("Arquivos disponíveis:")
            for i, file in enumerate(files[:20], 1):
                print(f"  {i}. {file.name}")
            
            choice = input("\nDigite o número do arquivo: ").strip()
            file_index = int(choice) - 1
            
            if 0 <= file_index < len(files):
                file_to_restore = files[file_index]
                
                # Determinar destino
                dest_dir = input("Diretório de destino (Enter para original): ").strip()
                if not dest_dir:
                    dest_dir = "data"
                
                dest_path = Path(dest_dir) / file_to_restore.name
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(str(file_to_restore), str(dest_path))
                print(f"✅ Arquivo restaurado em: {dest_path}")
            else:
                print("❌ Número inválido")
                
        except (ValueError, IndexError):
            print("❌ Seleção inválida")
        except Exception as e:
            self.show_error(f"Erro na restauração: {e}")
    
    def _restore_by_type(self, files: List[Path]):
        """Restaurar por tipo"""
        print("🏷️ Restaurar por tipo - Funcionalidade em desenvolvimento")
    
    def _restore_by_date(self, files: List[Path]):
        """Restaurar por data"""
        print("📅 Restaurar por data - Funcionalidade em desenvolvimento")
    
    def _restore_all(self, files: List[Path]):
        """Restaurar todos os arquivos"""
        print("🔄 Restaurar tudo - Funcionalidade em desenvolvimento")
    
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