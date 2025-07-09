#!/usr/bin/env python3
"""
File Configuration - Directory management, file formats, and storage settings
"""

import os
import shutil
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from .config_base import ConfigBase


class FileConfig(ConfigBase):
    """File and directory configuration management"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Configuração de Arquivos", session_stats, data_dir)
        self.data_dir = data_dir
    
    def show_file_menu(self):
        """Show file configuration menu"""
        current_config = {
            "Diretório de dados": "DATA_DIR",
            "Formato de arquivo": "FILE_FORMAT",
            "Auto-backup": "AUTO_BACKUP",
            "Auto-limpeza": "AUTO_CLEANUP",
            "Retenção de logs": "LOG_RETENTION_DAYS"
        }
        
        options = [
            "1. 📁 Configurar diretórios",
            "2. 📄 Configurar formatos de arquivo",
            "3. 💾 Configurar auto-backup",
            "4. 🧹 Configurar auto-limpeza",
            "5. 📊 Visualizar uso de armazenamento",
            "6. 🔄 Reorganizar arquivos",
            "7. 📝 Configurar retenção de logs"
        ]
        
        self._show_config_menu("📁 CONFIGURAÇÕES DE ARQUIVOS", options, current_config)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._configure_directories()
        elif choice == "2":
            self._configure_file_formats()
        elif choice == "3":
            self._configure_auto_backup()
        elif choice == "4":
            self._configure_auto_cleanup()
        elif choice == "5":
            self._show_storage_usage()
        elif choice == "6":
            self._reorganize_files()
        elif choice == "7":
            self._configure_log_retention()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _configure_directories(self):
        """Configure directory structure"""
        print("\n📁 CONFIGURAR DIRETÓRIOS")
        print("═" * 30)
        
        # Current directories
        current_data_dir = self._get_setting("DATA_DIR", "data")
        current_backup_dir = self._get_setting("BACKUP_DIR", "backups")
        current_logs_dir = self._get_setting("LOGS_DIR", "logs")
        current_cache_dir = self._get_setting("CACHE_DIR", "cache")
        
        print("📋 Diretórios atuais:")
        print(f"  Dados: {current_data_dir}")
        print(f"  Backups: {current_backup_dir}")
        print(f"  Logs: {current_logs_dir}")
        print(f"  Cache: {current_cache_dir}")
        
        print("\n📝 Opções:")
        print("  1. Alterar diretório de dados")
        print("  2. Alterar diretório de backups")
        print("  3. Alterar diretório de logs")
        print("  4. Alterar diretório de cache")
        print("  5. Criar estrutura de diretórios")
        print("  6. Verificar permissões")
        
        choice = self._validate_numeric_input("📁 Escolha uma opção (1-6): ", 1, 6)
        
        if choice == 1:
            self._change_data_directory()
        elif choice == 2:
            self._change_backup_directory()
        elif choice == 3:
            self._change_logs_directory()
        elif choice == 4:
            self._change_cache_directory()
        elif choice == 5:
            self._create_directory_structure()
        elif choice == 6:
            self._check_directory_permissions()
    
    def _change_data_directory(self):
        """Change data directory"""
        current_dir = self._get_setting("DATA_DIR", "data")
        
        new_dir = input(f"\n📁 Novo diretório de dados (atual: {current_dir}): ").strip()
        if not new_dir:
            return
        
        # Validate directory
        new_path = Path(new_dir)
        
        if new_path.exists() and not new_path.is_dir():
            self.show_error(f"'{new_dir}' existe mas não é um diretório")
            return
        
        if self._confirm_action(f"alterar diretório de dados para '{new_dir}'"):
            try:
                # Create directory if it doesn't exist
                new_path.mkdir(parents=True, exist_ok=True)
                
                # Update setting
                if self._update_settings("DATA_DIR", new_dir):
                    self.show_success(f"Diretório de dados alterado para: {new_dir}")
                    
                    # Offer to move existing data
                    if Path(current_dir).exists() and current_dir != new_dir:
                        move_data = self._validate_boolean_input("📦 Mover dados existentes para o novo diretório? (s/n): ")
                        if move_data:
                            self._move_directory_contents(current_dir, new_dir)
                            
            except Exception as e:
                self.show_error(f"Erro ao criar diretório: {e}")
    
    def _change_backup_directory(self):
        """Change backup directory"""
        current_dir = self._get_setting("BACKUP_DIR", "backups")
        
        new_dir = input(f"\n💾 Novo diretório de backups (atual: {current_dir}): ").strip()
        if not new_dir:
            return
        
        if self._confirm_action(f"alterar diretório de backups para '{new_dir}'"):
            try:
                Path(new_dir).mkdir(parents=True, exist_ok=True)
                
                if self._update_settings("BACKUP_DIR", new_dir):
                    self.show_success(f"Diretório de backups alterado para: {new_dir}")
                    
            except Exception as e:
                self.show_error(f"Erro ao criar diretório: {e}")
    
    def _change_logs_directory(self):
        """Change logs directory"""
        current_dir = self._get_setting("LOGS_DIR", "logs")
        
        new_dir = input(f"\n📝 Novo diretório de logs (atual: {current_dir}): ").strip()
        if not new_dir:
            return
        
        if self._confirm_action(f"alterar diretório de logs para '{new_dir}'"):
            try:
                Path(new_dir).mkdir(parents=True, exist_ok=True)
                
                if self._update_settings("LOGS_DIR", new_dir):
                    self.show_success(f"Diretório de logs alterado para: {new_dir}")
                    
            except Exception as e:
                self.show_error(f"Erro ao criar diretório: {e}")
    
    def _change_cache_directory(self):
        """Change cache directory"""
        current_dir = self._get_setting("CACHE_DIR", "cache")
        
        new_dir = input(f"\n🗄️ Novo diretório de cache (atual: {current_dir}): ").strip()
        if not new_dir:
            return
        
        if self._confirm_action(f"alterar diretório de cache para '{new_dir}'"):
            try:
                Path(new_dir).mkdir(parents=True, exist_ok=True)
                
                if self._update_settings("CACHE_DIR", new_dir):
                    self.show_success(f"Diretório de cache alterado para: {new_dir}")
                    
            except Exception as e:
                self.show_error(f"Erro ao criar diretório: {e}")
    
    def _create_directory_structure(self):
        """Create complete directory structure"""
        print("\n📁 CRIAR ESTRUTURA DE DIRETÓRIOS")
        print("═" * 40)
        
        directories = [
            self._get_setting("DATA_DIR", "data"),
            self._get_setting("BACKUP_DIR", "backups"),
            self._get_setting("LOGS_DIR", "logs"),
            self._get_setting("CACHE_DIR", "cache"),
            f"{self._get_setting('DATA_DIR', 'data')}/restaurants",
            f"{self._get_setting('DATA_DIR', 'data')}/products",
            f"{self._get_setting('DATA_DIR', 'data')}/categories",
            f"{self._get_setting('LOGS_DIR', 'logs')}/scraping",
            f"{self._get_setting('LOGS_DIR', 'logs')}/system",
            f"{self._get_setting('CACHE_DIR', 'cache')}/search_indexes"
        ]
        
        if self._confirm_action("criar estrutura completa de diretórios"):
            created_count = 0
            for directory in directories:
                try:
                    Path(directory).mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ {directory}")
                    created_count += 1
                except Exception as e:
                    print(f"  ❌ {directory}: {e}")
            
            self.show_success(f"Estrutura criada! {created_count}/{len(directories)} diretórios processados.")
    
    def _check_directory_permissions(self):
        """Check directory permissions"""
        print("\n🔒 VERIFICAR PERMISSÕES")
        print("═" * 30)
        
        directories = [
            self._get_setting("DATA_DIR", "data"),
            self._get_setting("BACKUP_DIR", "backups"),
            self._get_setting("LOGS_DIR", "logs"),
            self._get_setting("CACHE_DIR", "cache")
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                print(f"  ❌ {directory}: Não existe")
                continue
            
            # Check permissions
            readable = os.access(dir_path, os.R_OK)
            writable = os.access(dir_path, os.W_OK)
            executable = os.access(dir_path, os.X_OK)
            
            status = "✅" if readable and writable and executable else "❌"
            perms = f"r{'w' if writable else '-'}{'x' if executable else '-'}"
            
            print(f"  {status} {directory}: {perms}")
    
    def _move_directory_contents(self, source_dir: str, target_dir: str):
        """Move contents from source to target directory"""
        try:
            source_path = Path(source_dir)
            target_path = Path(target_dir)
            
            if not source_path.exists():
                self.show_warning(f"Diretório origem '{source_dir}' não existe")
                return
            
            moved_count = 0
            for item in source_path.iterdir():
                try:
                    target_item = target_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, target_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, target_item)
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Erro ao mover {item.name}: {e}")
            
            self.show_success(f"Movidos {moved_count} itens para {target_dir}")
            
        except Exception as e:
            self.show_error(f"Erro ao mover conteúdo: {e}")
    
    def _configure_file_formats(self):
        """Configure file formats"""
        print("\n📄 CONFIGURAR FORMATOS DE ARQUIVO")
        print("═" * 40)
        
        current_format = self._get_setting("FILE_FORMAT", "json")
        current_encoding = self._get_setting("FILE_ENCODING", "utf-8")
        current_compression = self._get_setting("FILE_COMPRESSION", False)
        
        print(f"Formato atual: {current_format}")
        print(f"Encoding atual: {current_encoding}")
        print(f"Compressão atual: {'Ativada' if current_compression else 'Desativada'}")
        
        print("\n📝 Formatos disponíveis:")
        formats = ["json", "csv", "xlsx", "parquet"]
        for i, fmt in enumerate(formats, 1):
            print(f"  {i}. {fmt.upper()}")
        
        choice = self._validate_numeric_input("📄 Escolha um formato (1-4): ", 1, 4)
        if choice is None:
            return
        
        new_format = formats[choice - 1]
        
        # Encoding options
        encodings = ["utf-8", "latin-1", "ascii"]
        print("\n🔤 Encodings disponíveis:")
        for i, enc in enumerate(encodings, 1):
            print(f"  {i}. {enc}")
        
        enc_choice = self._validate_numeric_input("🔤 Escolha um encoding (1-3): ", 1, 3)
        if enc_choice is None:
            return
        
        new_encoding = encodings[enc_choice - 1]
        
        # Compression option
        new_compression = self._validate_boolean_input("📦 Ativar compressão? (s/n): ")
        if new_compression is None:
            return
        
        if self._confirm_action(f"alterar formato para {new_format} com {new_encoding} e compressão {'ativada' if new_compression else 'desativada'}"):
            success = True
            if new_format != current_format:
                success &= self._update_settings("FILE_FORMAT", new_format)
            if new_encoding != current_encoding:
                success &= self._update_settings("FILE_ENCODING", new_encoding)
            if new_compression != current_compression:
                success &= self._update_settings("FILE_COMPRESSION", new_compression)
            
            if success:
                self.show_success("Configurações de formato atualizadas!")
    
    def _configure_auto_backup(self):
        """Configure automatic backup settings"""
        print("\n💾 CONFIGURAR AUTO-BACKUP")
        print("═" * 32)
        
        current_enabled = self._get_setting("AUTO_BACKUP", True)
        current_interval = self._get_setting("BACKUP_INTERVAL_HOURS", 24)
        current_retention = self._get_setting("BACKUP_RETENTION_DAYS", 7)
        
        print(f"Auto-backup atual: {'Ativado' if current_enabled else 'Desativado'}")
        print(f"Intervalo atual: {current_interval}h")
        print(f"Retenção atual: {current_retention} dias")
        
        new_enabled = self._validate_boolean_input("💾 Ativar auto-backup? (s/n): ")
        if new_enabled is None:
            return
        
        if new_enabled:
            new_interval = self._validate_numeric_input("⏰ Intervalo entre backups (1-168h): ", 1, 168)
            if new_interval is None:
                return
            
            new_retention = self._validate_numeric_input("📅 Retenção de backups (1-365 dias): ", 1, 365)
            if new_retention is None:
                return
        else:
            new_interval = current_interval
            new_retention = current_retention
        
        if self._confirm_action("atualizar configurações de auto-backup"):
            success = True
            if new_enabled != current_enabled:
                success &= self._update_settings("AUTO_BACKUP", new_enabled)
            if new_interval != current_interval:
                success &= self._update_settings("BACKUP_INTERVAL_HOURS", new_interval)
            if new_retention != current_retention:
                success &= self._update_settings("BACKUP_RETENTION_DAYS", new_retention)
            
            if success:
                status = "ativado" if new_enabled else "desativado"
                self.show_success(f"Auto-backup {status}!")
    
    def _configure_auto_cleanup(self):
        """Configure automatic cleanup settings"""
        print("\n🧹 CONFIGURAR AUTO-LIMPEZA")
        print("═" * 32)
        
        current_enabled = self._get_setting("AUTO_CLEANUP", True)
        current_temp_retention = self._get_setting("TEMP_RETENTION_HOURS", 24)
        current_log_retention = self._get_setting("LOG_RETENTION_DAYS", 30)
        current_cache_retention = self._get_setting("CACHE_RETENTION_DAYS", 7)
        
        print(f"Auto-limpeza atual: {'Ativada' if current_enabled else 'Desativada'}")
        print(f"Retenção temp atual: {current_temp_retention}h")
        print(f"Retenção logs atual: {current_log_retention} dias")
        print(f"Retenção cache atual: {current_cache_retention} dias")
        
        new_enabled = self._validate_boolean_input("🧹 Ativar auto-limpeza? (s/n): ")
        if new_enabled is None:
            return
        
        if new_enabled:
            new_temp_retention = self._validate_numeric_input("🗂️ Retenção arquivos temporários (1-168h): ", 1, 168)
            if new_temp_retention is None:
                return
            
            new_log_retention = self._validate_numeric_input("📝 Retenção logs (1-365 dias): ", 1, 365)
            if new_log_retention is None:
                return
            
            new_cache_retention = self._validate_numeric_input("🗄️ Retenção cache (1-90 dias): ", 1, 90)
            if new_cache_retention is None:
                return
        else:
            new_temp_retention = current_temp_retention
            new_log_retention = current_log_retention
            new_cache_retention = current_cache_retention
        
        if self._confirm_action("atualizar configurações de auto-limpeza"):
            success = True
            if new_enabled != current_enabled:
                success &= self._update_settings("AUTO_CLEANUP", new_enabled)
            if new_temp_retention != current_temp_retention:
                success &= self._update_settings("TEMP_RETENTION_HOURS", new_temp_retention)
            if new_log_retention != current_log_retention:
                success &= self._update_settings("LOG_RETENTION_DAYS", new_log_retention)
            if new_cache_retention != current_cache_retention:
                success &= self._update_settings("CACHE_RETENTION_DAYS", new_cache_retention)
            
            if success:
                status = "ativada" if new_enabled else "desativada"
                self.show_success(f"Auto-limpeza {status}!")
    
    def _show_storage_usage(self):
        """Show storage usage information"""
        print("\n📊 USO DE ARMAZENAMENTO")
        print("═" * 30)
        
        directories = [
            ("Dados", self._get_setting("DATA_DIR", "data")),
            ("Backups", self._get_setting("BACKUP_DIR", "backups")),
            ("Logs", self._get_setting("LOGS_DIR", "logs")),
            ("Cache", self._get_setting("CACHE_DIR", "cache"))
        ]
        
        total_size = 0
        
        for name, directory in directories:
            size = self._get_directory_size(directory)
            total_size += size
            
            if size > 0:
                size_str = self._format_size(size)
                print(f"  📁 {name}: {size_str}")
            else:
                print(f"  📁 {name}: Vazio ou não existe")
        
        print(f"\n💾 Total: {self._format_size(total_size)}")
        
        # Show disk usage
        try:
            disk_usage = shutil.disk_usage(".")
            free_space = disk_usage.free
            total_space = disk_usage.total
            used_percentage = ((total_space - free_space) / total_space) * 100
            
            print(f"🖥️ Espaço livre no disco: {self._format_size(free_space)}")
            print(f"📊 Uso do disco: {used_percentage:.1f}%")
            
        except Exception as e:
            print(f"❌ Erro ao verificar uso do disco: {e}")
    
    def _get_directory_size(self, directory: str) -> int:
        """Get directory size in bytes"""
        try:
            total_size = 0
            path = Path(directory)
            
            if not path.exists():
                return 0
            
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
            
            return total_size
            
        except Exception as e:
            print(f"❌ Erro ao calcular tamanho de {directory}: {e}")
            return 0
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _reorganize_files(self):
        """Reorganize files in data directory"""
        print("\n🔄 REORGANIZAR ARQUIVOS")
        print("═" * 30)
        
        data_dir = Path(self._get_setting("DATA_DIR", "data"))
        
        if not data_dir.exists():
            self.show_error("Diretório de dados não existe")
            return
        
        print("📝 Opções de reorganização:")
        print("  1. Organizar por data")
        print("  2. Organizar por tipo")
        print("  3. Organizar por tamanho")
        print("  4. Limpeza de arquivos duplicados")
        
        choice = self._validate_numeric_input("🔄 Escolha uma opção (1-4): ", 1, 4)
        
        if choice == 1:
            self._organize_by_date(data_dir)
        elif choice == 2:
            self._organize_by_type(data_dir)
        elif choice == 3:
            self._organize_by_size(data_dir)
        elif choice == 4:
            self._cleanup_duplicates(data_dir)
    
    def _organize_by_date(self, data_dir: Path):
        """Organize files by date"""
        if not self._confirm_action("organizar arquivos por data"):
            return
        
        try:
            moved_count = 0
            for file_path in data_dir.rglob("*"):
                if file_path.is_file():
                    # Get file creation date
                    creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
                    year_month = creation_time.strftime("%Y-%m")
                    
                    # Create date directory
                    date_dir = data_dir / "organized_by_date" / year_month
                    date_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    new_path = date_dir / file_path.name
                    if not new_path.exists():
                        shutil.move(str(file_path), str(new_path))
                        moved_count += 1
            
            self.show_success(f"Organizados {moved_count} arquivos por data!")
            
        except Exception as e:
            self.show_error(f"Erro ao organizar arquivos: {e}")
    
    def _organize_by_type(self, data_dir: Path):
        """Organize files by type"""
        if not self._confirm_action("organizar arquivos por tipo"):
            return
        
        try:
            moved_count = 0
            for file_path in data_dir.rglob("*"):
                if file_path.is_file():
                    # Get file extension
                    extension = file_path.suffix.lower() or "no_extension"
                    
                    # Create type directory
                    type_dir = data_dir / "organized_by_type" / extension
                    type_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    new_path = type_dir / file_path.name
                    if not new_path.exists():
                        shutil.move(str(file_path), str(new_path))
                        moved_count += 1
            
            self.show_success(f"Organizados {moved_count} arquivos por tipo!")
            
        except Exception as e:
            self.show_error(f"Erro ao organizar arquivos: {e}")
    
    def _organize_by_size(self, data_dir: Path):
        """Organize files by size"""
        if not self._confirm_action("organizar arquivos por tamanho"):
            return
        
        try:
            size_categories = {
                "small": (0, 1024 * 1024),  # 0-1MB
                "medium": (1024 * 1024, 10 * 1024 * 1024),  # 1-10MB
                "large": (10 * 1024 * 1024, 100 * 1024 * 1024),  # 10-100MB
                "huge": (100 * 1024 * 1024, float('inf'))  # >100MB
            }
            
            moved_count = 0
            for file_path in data_dir.rglob("*"):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    
                    # Determine size category
                    category = "unknown"
                    for cat_name, (min_size, max_size) in size_categories.items():
                        if min_size <= file_size < max_size:
                            category = cat_name
                            break
                    
                    # Create size directory
                    size_dir = data_dir / "organized_by_size" / category
                    size_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    new_path = size_dir / file_path.name
                    if not new_path.exists():
                        shutil.move(str(file_path), str(new_path))
                        moved_count += 1
            
            self.show_success(f"Organizados {moved_count} arquivos por tamanho!")
            
        except Exception as e:
            self.show_error(f"Erro ao organizar arquivos: {e}")
    
    def _cleanup_duplicates(self, data_dir: Path):
        """Clean up duplicate files"""
        if not self._confirm_action("remover arquivos duplicados"):
            return
        
        try:
            import hashlib
            
            file_hashes = {}
            duplicates = []
            
            # Find duplicates
            for file_path in data_dir.rglob("*"):
                if file_path.is_file():
                    # Calculate file hash
                    hash_obj = hashlib.md5()
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_obj.update(chunk)
                    
                    file_hash = hash_obj.hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append(file_path)
                    else:
                        file_hashes[file_hash] = file_path
            
            # Remove duplicates
            removed_count = 0
            for duplicate in duplicates:
                duplicate.unlink()
                removed_count += 1
            
            self.show_success(f"Removidos {removed_count} arquivos duplicados!")
            
        except Exception as e:
            self.show_error(f"Erro ao remover duplicados: {e}")
    
    def _configure_log_retention(self):
        """Configure log retention settings"""
        print("\n📝 CONFIGURAR RETENÇÃO DE LOGS")
        print("═" * 40)
        
        current_retention = self._get_setting("LOG_RETENTION_DAYS", 30)
        current_max_size = self._get_setting("MAX_LOG_SIZE_MB", 100)
        current_rotation = self._get_setting("LOG_ROTATION", True)
        
        print(f"Retenção atual: {current_retention} dias")
        print(f"Tamanho máximo atual: {current_max_size} MB")
        print(f"Rotação atual: {'Ativada' if current_rotation else 'Desativada'}")
        
        new_retention = self._validate_numeric_input("📅 Nova retenção (1-365 dias): ", 1, 365)
        if new_retention is None:
            return
        
        new_max_size = self._validate_numeric_input("📏 Novo tamanho máximo (1-1000 MB): ", 1, 1000)
        if new_max_size is None:
            return
        
        new_rotation = self._validate_boolean_input("🔄 Ativar rotação de logs? (s/n): ")
        if new_rotation is None:
            return
        
        if self._confirm_action("atualizar configurações de retenção de logs"):
            success = True
            if new_retention != current_retention:
                success &= self._update_settings("LOG_RETENTION_DAYS", new_retention)
            if new_max_size != current_max_size:
                success &= self._update_settings("MAX_LOG_SIZE_MB", new_max_size)
            if new_rotation != current_rotation:
                success &= self._update_settings("LOG_ROTATION", new_rotation)
            
            if success:
                self.show_success("Configurações de retenção de logs atualizadas!")
    
    def get_file_statistics(self) -> Dict[str, Any]:
        """Get file configuration statistics"""
        stats = self.get_base_statistics()
        
        # Directory sizes
        directories = [
            ("data", self._get_setting("DATA_DIR", "data")),
            ("backups", self._get_setting("BACKUP_DIR", "backups")),
            ("logs", self._get_setting("LOGS_DIR", "logs")),
            ("cache", self._get_setting("CACHE_DIR", "cache"))
        ]
        
        for name, directory in directories:
            stats[f"{name}_size_bytes"] = self._get_directory_size(directory)
            stats[f"{name}_exists"] = Path(directory).exists()
        
        # Configuration status
        stats.update({
            'file_format': self._get_setting("FILE_FORMAT", "json"),
            'auto_backup_enabled': self._get_setting("AUTO_BACKUP", True),
            'auto_cleanup_enabled': self._get_setting("AUTO_CLEANUP", True),
            'compression_enabled': self._get_setting("FILE_COMPRESSION", False)
        })
        
        return stats