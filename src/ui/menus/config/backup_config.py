#!/usr/bin/env python3
"""
Backup Configuration - Backup creation, restoration, and maintenance operations
"""

import json
import shutil
import tarfile
import zipfile
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta

from .config_base import ConfigBase


class BackupConfig(ConfigBase):
    """Backup and maintenance configuration management"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Backup e Manutenção", session_stats, data_dir)
        self.backup_dir = Path(self._get_setting("BACKUP_DIR", "backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def show_backup_menu(self):
        """Show backup configuration menu"""
        current_config = {
            "Auto-backup": "AUTO_BACKUP",
            "Diretório de backup": "BACKUP_DIR",
            "Retenção de backups": "BACKUP_RETENTION_DAYS",
            "Compressão": "BACKUP_COMPRESSION",
            "Backup incremental": "INCREMENTAL_BACKUP"
        }
        
        options = [
            "1. 💾 Criar backup",
            "2. 🔄 Restaurar backup",
            "3. 📋 Listar backups",
            "4. 🗑️ Remover backups antigos",
            "5. ⚙️ Configurar backup automático",
            "6. 🔧 Resetar configurações",
            "7. 🧹 Manutenção do sistema"
        ]
        
        self._show_config_menu("💾 BACKUP E MANUTENÇÃO", options, current_config)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._create_backup()
        elif choice == "2":
            self._restore_backup()
        elif choice == "3":
            self._list_backups()
        elif choice == "4":
            self._remove_old_backups()
        elif choice == "5":
            self._configure_auto_backup()
        elif choice == "6":
            self._reset_config()
        elif choice == "7":
            self._system_maintenance()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _create_backup(self):
        """Create a new backup"""
        print("\n💾 CRIAR BACKUP")
        print("═" * 20)
        
        backup_types = [
            ("Configurações", "config"),
            ("Dados", "data"),
            ("Logs", "logs"),
            ("Cache", "cache"),
            ("Completo", "full")
        ]
        
        print("📋 Tipos de backup disponíveis:")
        for i, (name, _) in enumerate(backup_types, 1):
            print(f"  {i}. {name}")
        
        choice = self._validate_numeric_input("💾 Escolha o tipo de backup (1-5): ", 1, 5)
        if choice is None:
            return
        
        backup_name, backup_type = backup_types[choice - 1]
        
        # Compression option
        use_compression = self._validate_boolean_input("📦 Usar compressão? (s/n): ")
        if use_compression is None:
            return
        
        # Custom name
        custom_name = input(f"\n🏷️ Nome customizado (deixe vazio para usar padrão): ").strip()
        
        if self._confirm_action(f"criar backup do tipo '{backup_name}'"):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if custom_name:
                    backup_filename = f"{custom_name}_{timestamp}"
                else:
                    backup_filename = f"{backup_type}_backup_{timestamp}"
                
                backup_path = self._perform_backup(backup_type, backup_filename, use_compression)
                
                if backup_path:
                    size = self._get_file_size(backup_path)
                    self.show_success(f"✅ Backup criado: {backup_path}")
                    self.show_info(f"📊 Tamanho: {self._format_size(size)}")
                else:
                    self.show_error("Falha ao criar backup")
                    
            except Exception as e:
                self.show_error(f"Erro ao criar backup: {e}")
    
    def _perform_backup(self, backup_type: str, filename: str, use_compression: bool) -> Path:
        """Perform the actual backup operation"""
        try:
            extension = ".tar.gz" if use_compression else ".tar"
            backup_path = self.backup_dir / f"{filename}{extension}"
            
            # Define what to backup based on type
            backup_items = self._get_backup_items(backup_type)
            
            if not backup_items:
                self.show_warning(f"Nenhum item encontrado para backup do tipo '{backup_type}'")
                return None
            
            # Create backup archive
            if use_compression:
                with tarfile.open(backup_path, "w:gz") as tar:
                    for item_path, archive_name in backup_items:
                        if item_path.exists():
                            tar.add(item_path, arcname=archive_name)
                            print(f"  ✅ Adicionado: {archive_name}")
                        else:
                            print(f"  ⚠️ Não encontrado: {item_path}")
            else:
                with tarfile.open(backup_path, "w") as tar:
                    for item_path, archive_name in backup_items:
                        if item_path.exists():
                            tar.add(item_path, arcname=archive_name)
                            print(f"  ✅ Adicionado: {archive_name}")
                        else:
                            print(f"  ⚠️ Não encontrado: {item_path}")
            
            # Create metadata file
            metadata = {
                "backup_type": backup_type,
                "created_at": datetime.now().isoformat(),
                "compression": use_compression,
                "items_count": len(backup_items),
                "size_bytes": backup_path.stat().st_size,
                "version": "1.0"
            }
            
            metadata_path = self.backup_dir / f"{filename}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return backup_path
            
        except Exception as e:
            self.show_error(f"Erro durante backup: {e}")
            return None
    
    def _get_backup_items(self, backup_type: str) -> List[tuple]:
        """Get list of items to backup based on type"""
        items = []
        
        if backup_type in ["config", "full"]:
            items.extend([
                (Path("config/settings.json"), "config/settings.json"),
                (Path(".env"), ".env"),
                (Path("src/config"), "src/config"),
            ])
        
        if backup_type in ["data", "full"]:
            data_dir = Path(self._get_setting("DATA_DIR", "data"))
            if data_dir.exists():
                items.append((data_dir, "data"))
        
        if backup_type in ["logs", "full"]:
            logs_dir = Path(self._get_setting("LOGS_DIR", "logs"))
            if logs_dir.exists():
                items.append((logs_dir, "logs"))
        
        if backup_type in ["cache", "full"]:
            cache_dir = Path(self._get_setting("CACHE_DIR", "cache"))
            if cache_dir.exists():
                items.append((cache_dir, "cache"))
        
        return items
    
    def _restore_backup(self):
        """Restore from backup"""
        print("\n🔄 RESTAURAR BACKUP")
        print("═" * 23)
        
        # List available backups
        backups = self._get_available_backups()
        
        if not backups:
            self.show_warning("Nenhum backup encontrado")
            return
        
        print("📋 Backups disponíveis:")
        for i, backup in enumerate(backups, 1):
            metadata = backup.get("metadata", {})
            created_at = metadata.get("created_at", "Unknown")
            backup_type = metadata.get("backup_type", "Unknown")
            size = self._format_size(metadata.get("size_bytes", 0))
            
            print(f"  {i}. {backup['name']} ({backup_type}) - {created_at} - {size}")
        
        choice = self._validate_numeric_input(f"🔄 Escolha o backup (1-{len(backups)}): ", 1, len(backups))
        if choice is None:
            return
        
        selected_backup = backups[choice - 1]
        
        # Restoration options
        print("\n📝 Opções de restauração:")
        print("  1. Restauração completa (substitui tudo)")
        print("  2. Restauração seletiva (escolher itens)")
        print("  3. Restauração com backup atual")
        
        restore_choice = self._validate_numeric_input("🔄 Escolha o tipo de restauração (1-3): ", 1, 3)
        if restore_choice is None:
            return
        
        backup_current = restore_choice == 3
        selective = restore_choice == 2
        
        if backup_current:
            if not self._confirm_action("criar backup das configurações atuais antes de restaurar"):
                return
            
            # Create backup of current state
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = self._perform_backup("full", f"before_restore_{timestamp}", True)
            if current_backup:
                self.show_info(f"Backup atual criado: {current_backup}")
        
        if self._confirm_action(f"restaurar backup '{selected_backup['name']}'"):
            try:
                self._perform_restore(selected_backup, selective)
                self.show_success("✅ Restauração concluída com sucesso!")
                
            except Exception as e:
                self.show_error(f"Erro durante restauração: {e}")
    
    def _perform_restore(self, backup: Dict[str, Any], selective: bool = False):
        """Perform the actual restore operation"""
        backup_path = backup["path"]
        
        try:
            # Extract backup
            with tarfile.open(backup_path, "r:*") as tar:
                members = tar.getmembers()
                
                if selective:
                    # Show available items for selection
                    print("\n📋 Itens disponíveis no backup:")
                    for i, member in enumerate(members, 1):
                        print(f"  {i}. {member.name}")
                    
                    selection = input("\n📝 Digite os números dos itens separados por vírgula: ").strip()
                    if selection:
                        try:
                            selected_indices = [int(x.strip()) - 1 for x in selection.split(",")]
                            members = [members[i] for i in selected_indices if 0 <= i < len(members)]
                        except ValueError:
                            self.show_error("Seleção inválida, restaurando todos os itens")
                
                # Extract selected members
                for member in members:
                    try:
                        tar.extract(member, ".")
                        print(f"  ✅ Restaurado: {member.name}")
                    except Exception as e:
                        print(f"  ❌ Erro ao restaurar {member.name}: {e}")
                        
        except Exception as e:
            raise Exception(f"Erro ao extrair backup: {e}")
    
    def _list_backups(self):
        """List available backups"""
        print("\n📋 LISTA DE BACKUPS")
        print("═" * 25)
        
        backups = self._get_available_backups()
        
        if not backups:
            self.show_warning("Nenhum backup encontrado")
            return
        
        total_size = 0
        
        for i, backup in enumerate(backups, 1):
            metadata = backup.get("metadata", {})
            created_at = metadata.get("created_at", "Unknown")
            backup_type = metadata.get("backup_type", "Unknown")
            size_bytes = metadata.get("size_bytes", 0)
            size = self._format_size(size_bytes)
            compression = metadata.get("compression", False)
            
            total_size += size_bytes
            
            print(f"\n  {i}. {backup['name']}")
            print(f"     Tipo: {backup_type}")
            print(f"     Criado: {created_at}")
            print(f"     Tamanho: {size}")
            print(f"     Comprimido: {'Sim' if compression else 'Não'}")
        
        print(f"\n📊 Total: {len(backups)} backups - {self._format_size(total_size)}")
    
    def _get_available_backups(self) -> List[Dict[str, Any]]:
        """Get list of available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.tar*"):
            if backup_file.is_file():
                backup_info = {
                    "name": backup_file.stem,
                    "path": backup_file,
                    "created": datetime.fromtimestamp(backup_file.stat().st_ctime),
                    "size": backup_file.stat().st_size
                }
                
                # Try to load metadata
                metadata_file = self.backup_dir / f"{backup_file.stem}_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            backup_info["metadata"] = json.load(f)
                    except:
                        backup_info["metadata"] = {}
                else:
                    backup_info["metadata"] = {}
                
                backups.append(backup_info)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def _remove_old_backups(self):
        """Remove old backups"""
        print("\n🗑️ REMOVER BACKUPS ANTIGOS")
        print("═" * 32)
        
        retention_days = self._get_setting("BACKUP_RETENTION_DAYS", 30)
        
        print(f"Retenção configurada: {retention_days} dias")
        
        # Allow custom retention for this operation
        custom_retention = self._validate_boolean_input("🗓️ Usar retenção personalizada? (s/n): ")
        if custom_retention:
            retention_days = self._validate_numeric_input("📅 Quantos dias manter? (1-365): ", 1, 365)
            if retention_days is None:
                return
        
        backups = self._get_available_backups()
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        old_backups = [b for b in backups if b["created"] < cutoff_date]
        
        if not old_backups:
            self.show_info("Nenhum backup antigo encontrado")
            return
        
        print(f"\n📋 Backups que serão removidos ({len(old_backups)}):")
        total_size = 0
        for backup in old_backups:
            print(f"  - {backup['name']} ({backup['created'].strftime('%Y-%m-%d %H:%M')})")
            total_size += backup["size"]
        
        print(f"\n💾 Espaço que será liberado: {self._format_size(total_size)}")
        
        if self._confirm_action(f"remover {len(old_backups)} backup(s) antigo(s)"):
            try:
                removed_count = 0
                for backup in old_backups:
                    # Remove backup file
                    backup["path"].unlink()
                    removed_count += 1
                    
                    # Remove metadata file if exists
                    metadata_file = self.backup_dir / f"{backup['name']}_metadata.json"
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    print(f"  ✅ Removido: {backup['name']}")
                
                self.show_success(f"Removidos {removed_count} backups antigos!")
                self.show_info(f"Espaço liberado: {self._format_size(total_size)}")
                
            except Exception as e:
                self.show_error(f"Erro ao remover backups: {e}")
    
    def _configure_auto_backup(self):
        """Configure automatic backup settings"""
        print("\n⚙️ CONFIGURAR BACKUP AUTOMÁTICO")
        print("═" * 38)
        
        current_enabled = self._get_setting("AUTO_BACKUP", True)
        current_interval = self._get_setting("AUTO_BACKUP_INTERVAL_HOURS", 24)
        current_retention = self._get_setting("BACKUP_RETENTION_DAYS", 30)
        current_types = self._get_setting("AUTO_BACKUP_TYPES", ["config", "data"])
        current_compression = self._get_setting("BACKUP_COMPRESSION", True)
        
        print(f"Auto-backup atual: {'Ativado' if current_enabled else 'Desativado'}")
        print(f"Intervalo atual: {current_interval}h")
        print(f"Retenção atual: {current_retention} dias")
        print(f"Tipos atual: {', '.join(current_types)}")
        print(f"Compressão atual: {'Ativada' if current_compression else 'Desativada'}")
        
        new_enabled = self._validate_boolean_input("\n⚙️ Ativar backup automático? (s/n): ")
        if new_enabled is None:
            return
        
        if new_enabled:
            new_interval = self._validate_numeric_input("⏰ Intervalo entre backups (1-168h): ", 1, 168)
            if new_interval is None:
                return
            
            new_retention = self._validate_numeric_input("📅 Retenção de backups (1-365 dias): ", 1, 365)
            if new_retention is None:
                return
            
            # Backup types
            available_types = ["config", "data", "logs", "cache"]
            print("\n📋 Tipos de backup disponíveis:")
            for i, backup_type in enumerate(available_types, 1):
                print(f"  {i}. {backup_type}")
            
            types_input = input("📝 Digite os números dos tipos separados por vírgula: ").strip()
            if types_input:
                try:
                    type_indices = [int(x.strip()) - 1 for x in types_input.split(",")]
                    new_types = [available_types[i] for i in type_indices if 0 <= i < len(available_types)]
                except ValueError:
                    self.show_error("Seleção inválida, mantendo tipos atuais")
                    new_types = current_types
            else:
                new_types = current_types
            
            new_compression = self._validate_boolean_input("📦 Usar compressão? (s/n): ")
            if new_compression is None:
                return
        else:
            new_interval = current_interval
            new_retention = current_retention
            new_types = current_types
            new_compression = current_compression
        
        if self._confirm_action("atualizar configurações de backup automático"):
            success = True
            if new_enabled != current_enabled:
                success &= self._update_settings("AUTO_BACKUP", new_enabled)
            if new_interval != current_interval:
                success &= self._update_settings("AUTO_BACKUP_INTERVAL_HOURS", new_interval)
            if new_retention != current_retention:
                success &= self._update_settings("BACKUP_RETENTION_DAYS", new_retention)
            if new_types != current_types:
                success &= self._update_settings("AUTO_BACKUP_TYPES", new_types)
            if new_compression != current_compression:
                success &= self._update_settings("BACKUP_COMPRESSION", new_compression)
            
            if success:
                status = "ativado" if new_enabled else "desativado"
                self.show_success(f"Backup automático {status}!")
    
    def _reset_config(self):
        """Reset configuration to defaults"""
        print("\n🔧 RESETAR CONFIGURAÇÕES")
        print("═" * 30)
        
        reset_options = [
            ("Configurações do sistema", "system"),
            ("Configurações de rede", "network"),
            ("Configurações de arquivos", "files"),
            ("Configurações de scraping", "scraping"),
            ("Todas as configurações", "all")
        ]
        
        print("📋 Opções de reset:")
        for i, (name, _) in enumerate(reset_options, 1):
            print(f"  {i}. {name}")
        
        choice = self._validate_numeric_input("🔧 Escolha o que resetar (1-5): ", 1, 5)
        if choice is None:
            return
        
        reset_name, reset_type = reset_options[choice - 1]
        
        # Create backup before reset
        create_backup = self._validate_boolean_input("💾 Criar backup antes de resetar? (s/n): ")
        if create_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self._perform_backup("config", f"before_reset_{timestamp}", True)
            if backup_path:
                self.show_info(f"Backup criado: {backup_path}")
        
        if self._confirm_action(f"resetar {reset_name.lower()}"):
            try:
                self._perform_reset(reset_type)
                self.show_success(f"✅ {reset_name} resetadas com sucesso!")
                self.show_warning("⚠️ Reinicie o sistema para aplicar as mudanças")
                
            except Exception as e:
                self.show_error(f"Erro ao resetar configurações: {e}")
    
    def _perform_reset(self, reset_type: str):
        """Perform the actual reset operation"""
        if reset_type in ["system", "all"]:
            system_defaults = {
                "LOG_LEVEL": "INFO",
                "CACHE_ENABLED": True,
                "SECURITY_ENABLED": True,
                "MONITORING_ENABLED": False,
                "WEBHOOKS_ENABLED": False,
                "DEVELOPMENT_MODE": False,
                "PLUGINS_ENABLED": True,
                "LANGUAGE": "pt_BR",
                "TIMEZONE": "America/Sao_Paulo"
            }
            
            for key, value in system_defaults.items():
                self._update_settings(key, value)
        
        if reset_type in ["network", "all"]:
            network_defaults = {
                "HTTP_TIMEOUT": 30,
                "USER_AGENT": "iFoodScraper/1.0",
                "MIN_DELAY": 1.0,
                "MAX_DELAY": 3.0,
                "MAX_RETRIES": 3,
                "RETRY_DELAY": 5.0
            }
            
            for key, value in network_defaults.items():
                self._update_settings(key, value)
            
            # Clear proxy settings
            self._update_env_file("HTTP_PROXY", "")
            self._update_env_file("HTTPS_PROXY", "")
        
        if reset_type in ["files", "all"]:
            files_defaults = {
                "DATA_DIR": "data",
                "BACKUP_DIR": "backups",
                "LOGS_DIR": "logs",
                "CACHE_DIR": "cache",
                "FILE_FORMAT": "json",
                "FILE_ENCODING": "utf-8",
                "FILE_COMPRESSION": False,
                "AUTO_BACKUP": True,
                "AUTO_CLEANUP": True
            }
            
            for key, value in files_defaults.items():
                self._update_settings(key, value)
        
        if reset_type in ["scraping", "all"]:
            scraping_defaults = {
                "MAX_WORKERS": 3,
                "HEADLESS_MODE": True,
                "BROWSER_TYPE": "chromium",
                "WINDOW_SIZE": "1920x1080",
                "DEBUG_MODE": False,
                "COLLECT_METRICS": True,
                "PAGE_TIMEOUT": 30000,
                "ELEMENT_TIMEOUT": 10000,
                "SCROLL_DELAY": 1.0
            }
            
            for key, value in scraping_defaults.items():
                self._update_settings(key, value)
        
        if reset_type == "all":
            # Reset database environment variables
            db_defaults = {
                "DB_HOST": "localhost",
                "DB_PORT": "3306",
                "DB_NAME": "ifood_scraper_v3",
                "DB_USER": "root",
                "DB_POOL_SIZE": "5"
            }
            
            for key, value in db_defaults.items():
                self._update_env_file(key, value)
    
    def _system_maintenance(self):
        """System maintenance operations"""
        print("\n🧹 MANUTENÇÃO DO SISTEMA")
        print("═" * 30)
        
        options = [
            "1. 🔍 Verificar integridade do sistema",
            "2. 🛠️ Reparar configurações corrompidas",
            "3. 🗂️ Reorganizar arquivos",
            "4. 📊 Otimizar banco de dados",
            "5. 🧹 Limpeza profunda",
            "6. 📈 Relatório de sistema"
        ]
        
        for option in options:
            print(f"  {option}")
        
        choice = self._validate_numeric_input("\n🧹 Escolha uma opção (1-6): ", 1, 6)
        
        if choice == 1:
            self._system_integrity_check()
        elif choice == 2:
            self._repair_corrupted_configs()
        elif choice == 3:
            self._reorganize_files()
        elif choice == 4:
            self._optimize_database()
        elif choice == 5:
            self._deep_cleanup()
        elif choice == 6:
            self._system_report()
    
    def _system_integrity_check(self):
        """Check system integrity"""
        print("\n🔍 VERIFICAÇÃO DE INTEGRIDADE")
        print("═" * 35)
        
        issues = []
        
        # Check required directories
        required_dirs = [
            self._get_setting("DATA_DIR", "data"),
            self._get_setting("BACKUP_DIR", "backups"),
            self._get_setting("LOGS_DIR", "logs"),
            self._get_setting("CACHE_DIR", "cache")
        ]
        
        print("📁 Verificando diretórios...")
        for directory in required_dirs:
            if not Path(directory).exists():
                issues.append(f"Diretório não encontrado: {directory}")
                print(f"  ❌ {directory}")
            else:
                print(f"  ✅ {directory}")
        
        # Check configuration files
        print("\n📄 Verificando arquivos de configuração...")
        config_files = [
            ("config/settings.json", "Configurações do sistema"),
            (".env", "Variáveis de ambiente")
        ]
        
        for file_path, description in config_files:
            if not Path(file_path).exists():
                issues.append(f"Arquivo não encontrado: {file_path}")
                print(f"  ❌ {description}")
            else:
                print(f"  ✅ {description}")
        
        # Check database connection
        print("\n🗄️ Verificando conexão com banco...")
        try:
            from src.config.database import get_connection
            conn = get_connection()
            if conn:
                conn.close()
                print("  ✅ Conexão com banco de dados")
            else:
                issues.append("Falha na conexão com banco de dados")
                print("  ❌ Conexão com banco de dados")
        except Exception as e:
            issues.append(f"Erro na conexão com banco: {e}")
            print(f"  ❌ Conexão com banco de dados: {e}")
        
        # Summary
        if issues:
            print(f"\n⚠️ Encontrados {len(issues)} problema(s):")
            for issue in issues:
                print(f"  - {issue}")
                
            fix_issues = self._validate_boolean_input("\n🔧 Tentar corrigir automaticamente? (s/n): ")
            if fix_issues:
                self._auto_fix_issues(issues)
        else:
            print("\n✅ Sistema íntegro! Nenhum problema encontrado.")
    
    def _auto_fix_issues(self, issues: List[str]):
        """Automatically fix detected issues"""
        fixed_count = 0
        
        for issue in issues:
            try:
                if "Diretório não encontrado" in issue:
                    # Extract directory name
                    dir_name = issue.split(": ")[1]
                    Path(dir_name).mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ Criado diretório: {dir_name}")
                    fixed_count += 1
                
                elif "Arquivo não encontrado" in issue:
                    if "config/settings.json" in issue:
                        # Create default settings file
                        Path("config").mkdir(parents=True, exist_ok=True)
                        with open("config/settings.json", 'w') as f:
                            json.dump({}, f)
                        print("  ✅ Criado arquivo de configurações")
                        fixed_count += 1
                    
                    elif ".env" in issue:
                        # Create default .env file
                        with open(".env", 'w') as f:
                            f.write("# Arquivo de configuração criado automaticamente\n")
                        print("  ✅ Criado arquivo .env")
                        fixed_count += 1
                        
            except Exception as e:
                print(f"  ❌ Erro ao corrigir {issue}: {e}")
        
        self.show_success(f"Corrigidos {fixed_count}/{len(issues)} problemas")
    
    def _repair_corrupted_configs(self):
        """Repair corrupted configuration files"""
        print("\n🛠️ REPARAR CONFIGURAÇÕES")
        print("═" * 30)
        
        # Check and repair JSON files
        json_files = [
            "config/settings.json",
            "config/database.json"
        ]
        
        repaired_count = 0
        
        for json_file in json_files:
            if Path(json_file).exists():
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                    print(f"  ✅ {json_file} - OK")
                except json.JSONDecodeError:
                    print(f"  🔧 {json_file} - Corrompido, reparando...")
                    
                    # Backup corrupted file
                    backup_path = f"{json_file}.corrupted.bak"
                    shutil.copy2(json_file, backup_path)
                    
                    # Create empty valid JSON
                    with open(json_file, 'w') as f:
                        json.dump({}, f, indent=2)
                    
                    print(f"  ✅ {json_file} - Reparado (backup: {backup_path})")
                    repaired_count += 1
        
        self.show_success(f"Reparados {repaired_count} arquivos de configuração")
    
    def _reorganize_files(self):
        """Reorganize system files"""
        print("\n🗂️ REORGANIZAR ARQUIVOS")
        print("═" * 28)
        
        # Move misplaced files to correct directories
        moved_count = 0
        
        # Check for log files in wrong places
        for log_file in Path(".").glob("*.log"):
            logs_dir = Path(self._get_setting("LOGS_DIR", "logs"))
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = logs_dir / log_file.name
            log_file.rename(target_path)
            print(f"  ✅ Movido: {log_file.name} → {target_path}")
            moved_count += 1
        
        # Check for backup files in wrong places
        for backup_file in Path(".").glob("*.bak"):
            backup_dir = Path(self._get_setting("BACKUP_DIR", "backups"))
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = backup_dir / backup_file.name
            backup_file.rename(target_path)
            print(f"  ✅ Movido: {backup_file.name} → {target_path}")
            moved_count += 1
        
        self.show_success(f"Reorganizados {moved_count} arquivos")
    
    def _optimize_database(self):
        """Optimize database performance"""
        print("\n📊 OTIMIZAR BANCO DE DADOS")
        print("═" * 32)
        
        try:
            from src.config.database import get_connection
            
            conn = get_connection()
            if not conn:
                self.show_error("Não foi possível conectar ao banco")
                return
            
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if not tables:
                self.show_warning("Nenhuma tabela encontrada")
                return
            
            optimized_count = 0
            for (table_name,) in tables:
                try:
                    cursor.execute(f"OPTIMIZE TABLE {table_name}")
                    print(f"  ✅ Otimizada: {table_name}")
                    optimized_count += 1
                except Exception as e:
                    print(f"  ❌ Erro em {table_name}: {e}")
            
            cursor.close()
            conn.close()
            
            self.show_success(f"Otimizadas {optimized_count} tabelas")
            
        except Exception as e:
            self.show_error(f"Erro na otimização: {e}")
    
    def _deep_cleanup(self):
        """Perform deep system cleanup"""
        print("\n🧹 LIMPEZA PROFUNDA")
        print("═" * 24)
        
        if not self._confirm_action("executar limpeza profunda (pode demorar)"):
            return
        
        cleaned_items = 0
        
        # Clean temporary files
        temp_patterns = ["*.tmp", "*.temp", "*~", "*.bak"]
        for pattern in temp_patterns:
            for temp_file in Path(".").rglob(pattern):
                if temp_file.is_file():
                    temp_file.unlink()
                    cleaned_items += 1
        
        # Clean cache
        cache_dir = Path(self._get_setting("CACHE_DIR", "cache"))
        if cache_dir.exists():
            for cache_file in cache_dir.rglob("*"):
                if cache_file.is_file():
                    cache_file.unlink()
                    cleaned_items += 1
        
        # Clean old logs
        logs_dir = Path(self._get_setting("LOGS_DIR", "logs"))
        if logs_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=30)
            for log_file in logs_dir.rglob("*.log*"):
                if log_file.is_file():
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        log_file.unlink()
                        cleaned_items += 1
        
        self.show_success(f"Limpeza concluída! {cleaned_items} itens removidos")
    
    def _system_report(self):
        """Generate system report"""
        print("\n📈 RELATÓRIO DO SISTEMA")
        print("═" * 30)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "configuration": {},
            "storage": {},
            "backups": {}
        }
        
        # System info
        report["system_info"] = {
            "config_file_exists": self.config_file.exists(),
            "env_file_exists": self.env_file.exists(),
            "directories": {
                "data": Path(self._get_setting("DATA_DIR", "data")).exists(),
                "backups": Path(self._get_setting("BACKUP_DIR", "backups")).exists(),
                "logs": Path(self._get_setting("LOGS_DIR", "logs")).exists(),
                "cache": Path(self._get_setting("CACHE_DIR", "cache")).exists()
            }
        }
        
        # Configuration
        report["configuration"] = {
            "auto_backup": self._get_setting("AUTO_BACKUP", True),
            "compression": self._get_setting("BACKUP_COMPRESSION", True),
            "retention_days": self._get_setting("BACKUP_RETENTION_DAYS", 30)
        }
        
        # Storage
        directories = [
            ("data", self._get_setting("DATA_DIR", "data")),
            ("backups", self._get_setting("BACKUP_DIR", "backups")),
            ("logs", self._get_setting("LOGS_DIR", "logs")),
            ("cache", self._get_setting("CACHE_DIR", "cache"))
        ]
        
        for name, directory in directories:
            report["storage"][name] = {
                "exists": Path(directory).exists(),
                "size_bytes": self._get_directory_size(directory)
            }
        
        # Backups
        backups = self._get_available_backups()
        report["backups"] = {
            "total_count": len(backups),
            "total_size_bytes": sum(b["size"] for b in backups),
            "oldest": backups[-1]["created"].isoformat() if backups else None,
            "newest": backups[0]["created"].isoformat() if backups else None
        }
        
        # Save report
        report_file = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Display summary
        print("📊 Resumo do sistema:")
        print(f"  📁 Diretórios: {sum(1 for d in report['system_info']['directories'].values() if d)}/4")
        print(f"  💾 Backups: {report['backups']['total_count']}")
        print(f"  📏 Tamanho total: {self._format_size(sum(s['size_bytes'] for s in report['storage'].values()))}")
        print(f"  📄 Relatório salvo: {report_file}")
    
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
            
        except Exception:
            return 0
    
    def _get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except:
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
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup configuration statistics"""
        stats = self.get_base_statistics()
        
        # Backup information
        backups = self._get_available_backups()
        
        stats.update({
            'auto_backup_enabled': self._get_setting("AUTO_BACKUP", True),
            'backup_compression': self._get_setting("BACKUP_COMPRESSION", True),
            'backup_retention_days': self._get_setting("BACKUP_RETENTION_DAYS", 30),
            'backup_count': len(backups),
            'backup_total_size': sum(b["size"] for b in backups),
            'backup_directory_exists': self.backup_dir.exists(),
            'backup_directory_size': self._get_directory_size(str(self.backup_dir))
        })
        
        return stats