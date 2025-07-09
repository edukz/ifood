#!/usr/bin/env python3
"""
Configuration Base - Base class for all configuration modules
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from src.config.settings import SETTINGS
from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu


class ConfigBase(BaseMenu):
    """Base class for configuration modules with common functionality"""
    
    def __init__(self, title: str, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__(title, session_stats, data_dir)
        self.db = get_database_manager()
        self.config_file = Path("config/settings.json")
        self.env_file = Path(".env")
    
    def _update_settings(self, key: str, value: Any) -> bool:
        """
        Update a setting in the settings file
        
        Args:
            key: Setting key to update
            value: New value for the setting
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Load current settings
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Update the setting
            settings[key] = value
            
            # Save settings
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            self.show_success(f"Configuração '{key}' atualizada com sucesso!")
            return True
            
        except Exception as e:
            self.show_error(f"Erro ao atualizar configuração: {e}")
            return False
    
    def _update_env_file(self, key: str, value: str) -> bool:
        """
        Update an environment variable in the .env file
        
        Args:
            key: Environment variable key
            value: New value for the variable
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Read current .env file
            env_content = {}
            if self.env_file.exists():
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            k, v = line.split('=', 1)
                            env_content[k] = v
            
            # Update the variable
            env_content[key] = value
            
            # Write back to .env file
            with open(self.env_file, 'w', encoding='utf-8') as f:
                for k, v in env_content.items():
                    f.write(f"{k}={v}\n")
            
            self.show_success(f"Variável de ambiente '{key}' atualizada!")
            return True
            
        except Exception as e:
            self.show_error(f"Erro ao atualizar arquivo .env: {e}")
            return False
    
    def _get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value from SETTINGS or config file
        
        Args:
            key: Setting key to retrieve
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        try:
            # Try to get from SETTINGS first
            if hasattr(SETTINGS, key):
                return getattr(SETTINGS, key)
            
            # Try to get from config file
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if key in settings:
                        return settings[key]
            
            return default
            
        except Exception as e:
            self.show_error(f"Erro ao obter configuração '{key}': {e}")
            return default
    
    def _get_env_var(self, key: str, default: str = "") -> str:
        """
        Get an environment variable value
        
        Args:
            key: Environment variable key
            default: Default value if key not found
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
    
    def _validate_numeric_input(self, prompt: str, min_val: int = None, max_val: int = None) -> Optional[int]:
        """
        Validate numeric input with optional range checking
        
        Args:
            prompt: Input prompt message
            min_val: Minimum allowed value (optional)
            max_val: Maximum allowed value (optional)
            
        Returns:
            Validated integer value or None if invalid
        """
        try:
            value = int(input(prompt))
            
            if min_val is not None and value < min_val:
                self.show_error(f"Valor deve ser maior ou igual a {min_val}")
                return None
            
            if max_val is not None and value > max_val:
                self.show_error(f"Valor deve ser menor ou igual a {max_val}")
                return None
            
            return value
            
        except ValueError:
            self.show_error("Por favor, insira um número válido")
            return None
    
    def _validate_boolean_input(self, prompt: str) -> Optional[bool]:
        """
        Validate boolean input (s/n, y/n, sim/não)
        
        Args:
            prompt: Input prompt message
            
        Returns:
            Boolean value or None if invalid
        """
        response = input(prompt).strip().lower()
        
        if response in ['s', 'sim', 'y', 'yes', '1', 'true']:
            return True
        elif response in ['n', 'não', 'nao', 'no', '0', 'false']:
            return False
        else:
            self.show_error("Por favor, responda com 's' para sim ou 'n' para não")
            return None
    
    def _create_backup(self, backup_type: str = "config") -> bool:
        """
        Create a backup of current configuration
        
        Args:
            backup_type: Type of backup (config, database, etc.)
            
        Returns:
            True if backup created successfully, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(f"backups/{backup_type}")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_data = {
                'timestamp': timestamp,
                'type': backup_type,
                'settings': {},
                'env_vars': {}
            }
            
            # Backup settings file
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    backup_data['settings'] = json.load(f)
            
            # Backup environment variables
            if self.env_file.exists():
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            k, v = line.split('=', 1)
                            backup_data['env_vars'][k] = v
            
            # Save backup
            backup_file = backup_dir / f"{backup_type}_backup_{timestamp}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.show_success(f"Backup criado: {backup_file}")
            return True
            
        except Exception as e:
            self.show_error(f"Erro ao criar backup: {e}")
            return False
    
    def _show_current_config(self, config_keys: Dict[str, str]):
        """
        Display current configuration values
        
        Args:
            config_keys: Dictionary of {display_name: config_key}
        """
        print("\n📋 Configurações atuais:")
        for display_name, config_key in config_keys.items():
            if config_key.startswith("DB_"):
                value = self._get_env_var(config_key, "não definido")
            else:
                value = self._get_setting(config_key, "não definido")
            
            print(f"  {display_name}: {value}")
    
    def _confirm_action(self, action: str) -> bool:
        """
        Ask for confirmation before performing an action
        
        Args:
            action: Description of the action
            
        Returns:
            True if user confirmed, False otherwise
        """
        confirm = self._validate_boolean_input(f"\n❓ Confirmar {action}? (s/n): ")
        return confirm is True
    
    def _show_config_menu(self, title: str, options: list, current_values: Dict[str, Any] = None):
        """
        Show a configuration menu with current values
        
        Args:
            title: Menu title
            options: List of menu options
            current_values: Dictionary of current configuration values
        """
        print(f"\n{title}")
        print("═" * len(title))
        
        if current_values:
            self._show_current_config(current_values)
        
        print("\n📝 Opções disponíveis:")
        for option in options:
            print(f"  {option}")
        print("  0. ← Voltar")
    
    def get_base_statistics(self) -> Dict[str, Any]:
        """Get base configuration statistics"""
        return {
            'config_file_exists': self.config_file.exists(),
            'env_file_exists': self.env_file.exists(),
            'config_file_size': self.config_file.stat().st_size if self.config_file.exists() else 0,
            'env_file_size': self.env_file.stat().st_size if self.env_file.exists() else 0,
            'backup_dir_exists': Path("backups").exists()
        }