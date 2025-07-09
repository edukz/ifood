#!/usr/bin/env python3
"""
Sistema de busca de arquivos
"""

import os
import re
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

from tools.archive_manager import ArchiveManager
from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu


class FileSearch(BaseMenu):
    """Sistema de busca e pesquisa de arquivos"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path, 
                 archive_manager: ArchiveManager):
        super().__init__("Busca de Arquivos", session_stats, data_dir)
        self.archive_manager = archive_manager
        self.db = get_database_manager()
    
    def search_files(self):
        """Menu principal de busca de arquivos"""
        print("\n🔍 BUSCA DE ARQUIVOS")
        print("=" * 50)
        
        options = [
            "1. 🔍 Buscar por nome",
            "2. 🏷️ Buscar por extensão",
            "3. 📊 Buscar por tamanho",
            "4. 📅 Buscar por data",
            "5. 📝 Buscar por conteúdo",
            "6. 🔄 Busca avançada"
        ]
        
        self.show_menu("🔍 OPÇÕES DE BUSCA", options)
        choice = self.get_user_choice(6)
        
        if choice == "1":
            self._search_by_name()
        elif choice == "2":
            self._search_by_extension()
        elif choice == "3":
            self._search_by_size()
        elif choice == "4":
            self._search_by_date()
        elif choice == "5":
            self._search_by_content()
        elif choice == "6":
            self._advanced_search()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def search_specific_files(self):
        """Buscar arquivos específicos"""
        print("\n🔍 BUSCAR ARQUIVOS ESPECÍFICOS")
        print("-" * 50)
        
        try:
            # Obter termo de busca
            search_term = input("Digite o termo de busca: ").strip()
            if not search_term:
                print("❌ Termo de busca não pode estar vazio")
                return
            
            # Buscar arquivos
            found_files = []
            search_dirs = ["data", "logs", "cache", "archive"]
            
            for search_dir in search_dirs:
                dir_path = Path(search_dir)
                if dir_path.exists():
                    files = list(dir_path.rglob("*"))
                    files = [f for f in files if f.is_file()]
                    
                    for file in files:
                        if search_term.lower() in file.name.lower():
                            found_files.append(file)
            
            # Exibir resultados
            if found_files:
                print(f"\n📋 Encontrados {len(found_files)} arquivos:")
                for file in found_files[:20]:  # Limitar a 20 resultados
                    stat = file.stat()
                    size = self._format_size(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"  📄 {file} ({size}) - {modified}")
                
                if len(found_files) > 20:
                    print(f"  ... e mais {len(found_files) - 20} arquivos")
            else:
                print(f"❌ Nenhum arquivo encontrado com '{search_term}'")
            
        except Exception as e:
            self.show_error(f"Erro na busca: {e}")
    
    def _search_by_name(self):
        """Buscar por nome"""
        print("\n🔍 BUSCAR POR NOME")
        print("-" * 30)
        
        try:
            pattern = input("Digite o padrão de nome (use * para wildcards): ").strip()
            if not pattern:
                print("❌ Padrão não pode estar vazio")
                return
            
            # Converter wildcards para regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            
            found_files = []
            for path in Path(".").rglob("*"):
                if path.is_file() and re.search(regex_pattern, path.name, re.IGNORECASE):
                    found_files.append(path)
            
            self._display_search_results(found_files, f"nome '{pattern}'")
            
        except Exception as e:
            self.show_error(f"Erro na busca por nome: {e}")
    
    def _search_by_extension(self):
        """Buscar por extensão"""
        print("\n🏷️ BUSCAR POR EXTENSÃO")
        print("-" * 30)
        
        try:
            extension = input("Digite a extensão (ex: .txt, .csv, .json): ").strip()
            if not extension:
                print("❌ Extensão não pode estar vazia")
                return
            
            if not extension.startswith('.'):
                extension = '.' + extension
            
            found_files = list(Path(".").rglob(f"*{extension}"))
            found_files = [f for f in found_files if f.is_file()]
            
            self._display_search_results(found_files, f"extensão '{extension}'")
            
        except Exception as e:
            self.show_error(f"Erro na busca por extensão: {e}")
    
    def _search_by_size(self):
        """Buscar por tamanho"""
        print("\n📊 BUSCAR POR TAMANHO")
        print("-" * 30)
        
        try:
            size_options = [
                "1. Arquivos menores que 1 MB",
                "2. Arquivos entre 1-10 MB",
                "3. Arquivos entre 10-100 MB",
                "4. Arquivos maiores que 100 MB",
                "5. Tamanho personalizado"
            ]
            
            print("Escolha o critério de tamanho:")
            for option in size_options:
                print(f"  {option}")
            
            choice = input("\nEscolha: ").strip()
            
            min_size = 0
            max_size = float('inf')
            
            if choice == "1":
                max_size = 1 * 1024 * 1024  # 1 MB
            elif choice == "2":
                min_size = 1 * 1024 * 1024  # 1 MB
                max_size = 10 * 1024 * 1024  # 10 MB
            elif choice == "3":
                min_size = 10 * 1024 * 1024  # 10 MB
                max_size = 100 * 1024 * 1024  # 100 MB
            elif choice == "4":
                min_size = 100 * 1024 * 1024  # 100 MB
            elif choice == "5":
                min_mb = float(input("Tamanho mínimo (MB): ").strip() or "0")
                max_mb = float(input("Tamanho máximo (MB, Enter para sem limite): ").strip() or "inf")
                min_size = min_mb * 1024 * 1024
                max_size = max_mb * 1024 * 1024 if max_mb != float('inf') else float('inf')
            else:
                print("❌ Opção inválida")
                return
            
            # Buscar arquivos
            found_files = []
            for path in Path(".").rglob("*"):
                if path.is_file():
                    size = path.stat().st_size
                    if min_size <= size <= max_size:
                        found_files.append(path)
            
            self._display_search_results(found_files, f"tamanho entre {self._format_size(min_size)} e {self._format_size(max_size)}")
            
        except Exception as e:
            self.show_error(f"Erro na busca por tamanho: {e}")
    
    def _search_by_date(self):
        """Buscar por data"""
        print("\n📅 BUSCAR POR DATA")
        print("-" * 30)
        
        try:
            date_options = [
                "1. Arquivos modificados hoje",
                "2. Arquivos modificados na última semana",
                "3. Arquivos modificados no último mês",
                "4. Arquivos mais antigos que 1 mês",
                "5. Data personalizada"
            ]
            
            print("Escolha o critério de data:")
            for option in date_options:
                print(f"  {option}")
            
            choice = input("\nEscolha: ").strip()
            
            now = datetime.now()
            
            if choice == "1":
                min_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                max_date = now
            elif choice == "2":
                min_date = now - timedelta(days=7)
                max_date = now
            elif choice == "3":
                min_date = now - timedelta(days=30)
                max_date = now
            elif choice == "4":
                min_date = datetime.min
                max_date = now - timedelta(days=30)
            elif choice == "5":
                date_str = input("Digite a data (YYYY-MM-DD): ").strip()
                try:
                    target_date = datetime.strptime(date_str, "%Y-%m-%d")
                    min_date = target_date
                    max_date = target_date.replace(hour=23, minute=59, second=59)
                except ValueError:
                    print("❌ Formato de data inválido")
                    return
            else:
                print("❌ Opção inválida")
                return
            
            # Buscar arquivos
            found_files = []
            for path in Path(".").rglob("*"):
                if path.is_file():
                    mod_time = datetime.fromtimestamp(path.stat().st_mtime)
                    if min_date <= mod_time <= max_date:
                        found_files.append(path)
            
            self._display_search_results(found_files, f"data entre {min_date.strftime('%Y-%m-%d')} e {max_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            self.show_error(f"Erro na busca por data: {e}")
    
    def _search_by_content(self):
        """Buscar por conteúdo"""
        print("\n📝 BUSCAR POR CONTEÚDO")
        print("-" * 30)
        
        try:
            search_text = input("Digite o texto a buscar: ").strip()
            if not search_text:
                print("❌ Texto de busca não pode estar vazio")
                return
            
            # Extensões de arquivo de texto
            text_extensions = ['.txt', '.csv', '.json', '.xml', '.log', '.py', '.js', '.html', '.css', '.md']
            
            found_files = []
            for path in Path(".").rglob("*"):
                if path.is_file() and path.suffix.lower() in text_extensions:
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if search_text.lower() in content.lower():
                                found_files.append(path)
                    except Exception:
                        # Ignorar arquivos que não podem ser lidos
                        continue
            
            self._display_search_results(found_files, f"conteúdo '{search_text}'")
            
        except Exception as e:
            self.show_error(f"Erro na busca por conteúdo: {e}")
    
    def _advanced_search(self):
        """Busca avançada"""
        print("\n🔄 BUSCA AVANÇADA")
        print("-" * 30)
        
        try:
            # Coletar critérios
            criteria = {}
            
            # Nome
            name_pattern = input("Padrão de nome (Enter para pular): ").strip()
            if name_pattern:
                criteria['name'] = name_pattern.replace("*", ".*").replace("?", ".")
            
            # Extensão
            extension = input("Extensão (Enter para pular): ").strip()
            if extension:
                if not extension.startswith('.'):
                    extension = '.' + extension
                criteria['extension'] = extension
            
            # Tamanho mínimo
            min_size_mb = input("Tamanho mínimo em MB (Enter para pular): ").strip()
            if min_size_mb:
                criteria['min_size'] = float(min_size_mb) * 1024 * 1024
            
            # Tamanho máximo
            max_size_mb = input("Tamanho máximo em MB (Enter para pular): ").strip()
            if max_size_mb:
                criteria['max_size'] = float(max_size_mb) * 1024 * 1024
            
            if not criteria:
                print("❌ Pelo menos um critério deve ser especificado")
                return
            
            # Buscar arquivos
            found_files = []
            for path in Path(".").rglob("*"):
                if not path.is_file():
                    continue
                
                # Verificar nome
                if 'name' in criteria:
                    if not re.search(criteria['name'], path.name, re.IGNORECASE):
                        continue
                
                # Verificar extensão
                if 'extension' in criteria:
                    if path.suffix.lower() != criteria['extension'].lower():
                        continue
                
                # Verificar tamanho
                size = path.stat().st_size
                if 'min_size' in criteria and size < criteria['min_size']:
                    continue
                if 'max_size' in criteria and size > criteria['max_size']:
                    continue
                
                found_files.append(path)
            
            self._display_search_results(found_files, "critérios avançados")
            
        except Exception as e:
            self.show_error(f"Erro na busca avançada: {e}")
    
    def _display_search_results(self, files: List[Path], search_desc: str):
        """Exibir resultados da busca"""
        if files:
            print(f"\n📋 Encontrados {len(files)} arquivos para {search_desc}:")
            
            # Ordenar por data de modificação (mais recente primeiro)
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            for file in files[:20]:  # Limitar a 20 resultados
                stat = file.stat()
                size = self._format_size(stat.st_size)
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                print(f"  📄 {file} ({size}) - {modified}")
            
            if len(files) > 20:
                print(f"  ... e mais {len(files) - 20} arquivos")
            
            # Estatísticas
            total_size = sum(f.stat().st_size for f in files)
            print(f"\n📊 Total: {len(files)} arquivos, {self._format_size(total_size)}")
        else:
            print(f"❌ Nenhum arquivo encontrado para {search_desc}")
    
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