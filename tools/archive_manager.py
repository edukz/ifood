#!/usr/bin/env python3
"""
Sistema de compressão e arquivamento automático de dados antigos
Otimiza espaço em disco mantendo histórico completo
"""

import os
import sys
import gzip
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import tarfile
import zipfile

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.config.settings import SETTINGS


class ArchiveManager:
    """Gerenciador de arquivamento e compressão de dados"""
    
    def __init__(self, 
                 data_dir: Path = None,
                 archive_dir: Path = None,
                 retention_days: int = 7):
        """
        Args:
            data_dir: Diretório de dados para arquivar
            archive_dir: Diretório de destino dos arquivos
            retention_days: Dias para manter arquivos não comprimidos
        """
        self.data_dir = data_dir or Path(SETTINGS.output_dir)
        self.archive_dir = archive_dir or Path("archive/compressed_data")
        self.retention_days = retention_days
        self.logger = setup_logger("ArchiveManager")
        
        # Cria diretório de arquivo se não existir
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Estatísticas
        self.stats = {
            'files_compressed': 0,
            'original_size': 0,
            'compressed_size': 0,
            'space_saved': 0,
            'files_archived': 0
        }
    
    def get_old_files(self, directory: Path, days_old: int) -> List[Path]:
        """Retorna arquivos mais antigos que X dias"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        old_files = []
        
        for file_path in directory.glob("**/*.csv"):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    old_files.append(file_path)
        
        return old_files
    
    def compress_file(self, file_path: Path, compression_level: int = 9) -> Optional[Path]:
        """Comprime um arquivo individual usando gzip"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Atualiza estatísticas
            original_size = file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            
            self.stats['files_compressed'] += 1
            self.stats['original_size'] += original_size
            self.stats['compressed_size'] += compressed_size
            
            # Remove arquivo original
            file_path.unlink()
            
            compression_ratio = (1 - compressed_size / original_size) * 100
            self.logger.info(
                f"Comprimido: {file_path.name} "
                f"({self._format_size(original_size)} → {self._format_size(compressed_size)}, "
                f"{compression_ratio:.1f}% redução)"
            )
            
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"Erro ao comprimir {file_path}: {e}")
            return None
    
    def create_archive(self, files: List[Path], archive_name: str, 
                      format: str = "tar.gz") -> Optional[Path]:
        """Cria arquivo compactado com múltiplos arquivos"""
        archive_path = self.archive_dir / f"{archive_name}.{format}"
        
        try:
            if format == "tar.gz":
                with tarfile.open(archive_path, "w:gz") as tar:
                    for file_path in files:
                        # Adiciona mantendo estrutura de diretórios relativa
                        arcname = file_path.relative_to(self.data_dir)
                        tar.add(file_path, arcname=str(arcname))
                        self.stats['files_archived'] += 1
                        
            elif format == "zip":
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in files:
                        arcname = file_path.relative_to(self.data_dir)
                        zipf.write(file_path, arcname=str(arcname))
                        self.stats['files_archived'] += 1
            
            self.logger.info(f"Arquivo criado: {archive_path.name} ({len(files)} arquivos)")
            return archive_path
            
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo: {e}")
            return None
    
    def archive_by_date(self, category: str = "all"):
        """Arquiva dados por data"""
        self.logger.info(f"Iniciando arquivamento por data (categoria: {category})")
        
        # Determina diretórios baseado na categoria
        if category == "all":
            directories = [
                self.data_dir / "categories",
                self.data_dir / "restaurants",
                self.data_dir / "products"
            ]
        else:
            directories = [self.data_dir / category]
        
        for directory in directories:
            if not directory.exists():
                continue
                
            # Agrupa arquivos por mês
            files_by_month = {}
            old_files = self.get_old_files(directory, self.retention_days)
            
            for file_path in old_files:
                # Extrai data do arquivo (assume formato com timestamp)
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                month_key = mtime.strftime("%Y-%m")
                
                if month_key not in files_by_month:
                    files_by_month[month_key] = []
                files_by_month[month_key].append(file_path)
            
            # Cria arquivos por mês
            for month, files in files_by_month.items():
                category_name = directory.name
                archive_name = f"{category_name}_{month}"
                
                archive_path = self.create_archive(files, archive_name)
                
                if archive_path:
                    # Remove arquivos originais após arquivamento bem-sucedido
                    for file_path in files:
                        try:
                            file_path.unlink()
                            self.logger.debug(f"Removido: {file_path}")
                        except Exception as e:
                            self.logger.error(f"Erro ao remover {file_path}: {e}")
    
    def compress_individual_files(self):
        """Comprime arquivos individuais antigos"""
        self.logger.info("Comprimindo arquivos individuais antigos")
        
        for subdir in ["categories", "restaurants", "products"]:
            directory = self.data_dir / subdir
            if not directory.exists():
                continue
            
            old_files = self.get_old_files(directory, self.retention_days)
            
            for file_path in old_files:
                # Pula se já está comprimido
                if file_path.suffix == '.gz':
                    continue
                    
                self.compress_file(file_path)
    
    def decompress_file(self, compressed_path: Path) -> Optional[Path]:
        """Descomprime um arquivo .gz"""
        try:
            output_path = compressed_path.with_suffix('')
            
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            self.logger.info(f"Descomprimido: {compressed_path.name} → {output_path.name}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erro ao descomprimir {compressed_path}: {e}")
            return None
    
    def extract_archive(self, archive_path: Path, extract_to: Path = None) -> bool:
        """Extrai arquivo compactado"""
        extract_to = extract_to or self.data_dir / "extracted"
        extract_to.mkdir(parents=True, exist_ok=True)
        
        try:
            if archive_path.suffix == '.gz' and archive_path.stem.endswith('.tar'):
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(path=extract_to)
                    
            elif archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(path=extract_to)
            
            self.logger.info(f"Extraído: {archive_path.name} → {extract_to}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair {archive_path}: {e}")
            return False
    
    def cleanup_old_archives(self, max_age_days: int = 90):
        """Remove arquivos muito antigos"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        removed_count = 0
        
        for archive_path in self.archive_dir.glob("*"):
            if archive_path.is_file():
                mtime = datetime.fromtimestamp(archive_path.stat().st_mtime)
                if mtime < cutoff_date:
                    try:
                        archive_path.unlink()
                        removed_count += 1
                        self.logger.info(f"Removido arquivo antigo: {archive_path.name}")
                    except Exception as e:
                        self.logger.error(f"Erro ao remover {archive_path}: {e}")
        
        if removed_count > 0:
            self.logger.info(f"Total de arquivos antigos removidos: {removed_count}")
    
    def generate_index(self):
        """Gera índice de arquivos comprimidos"""
        index = {
            'generated_at': datetime.now().isoformat(),
            'archives': [],
            'statistics': {
                'total_archives': 0,
                'total_size': 0,
                'by_category': {}
            }
        }
        
        for archive_path in sorted(self.archive_dir.glob("*")):
            if archive_path.is_file():
                stat = archive_path.stat()
                
                archive_info = {
                    'name': archive_path.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'category': self._extract_category(archive_path.name)
                }
                
                index['archives'].append(archive_info)
                index['statistics']['total_archives'] += 1
                index['statistics']['total_size'] += stat.st_size
                
                # Estatísticas por categoria
                category = archive_info['category']
                if category not in index['statistics']['by_category']:
                    index['statistics']['by_category'][category] = {
                        'count': 0,
                        'size': 0
                    }
                index['statistics']['by_category'][category]['count'] += 1
                index['statistics']['by_category'][category]['size'] += stat.st_size
        
        # Salva índice
        index_path = self.archive_dir / "archive_index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Índice gerado: {index_path}")
        return index
    
    def _extract_category(self, filename: str) -> str:
        """Extrai categoria do nome do arquivo"""
        if "categories" in filename:
            return "categories"
        elif "restaurants" in filename or "restaurantes" in filename:
            return "restaurants"
        elif "products" in filename or "produtos" in filename:
            return "products"
        else:
            return "other"
    
    def _format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def show_statistics(self):
        """Mostra estatísticas do arquivamento"""
        self.stats['space_saved'] = self.stats['original_size'] - self.stats['compressed_size']
        
        print("\n" + "="*60)
        print("ESTATÍSTICAS DE ARQUIVAMENTO:")
        print(f"  Arquivos comprimidos: {self.stats['files_compressed']}")
        print(f"  Arquivos arquivados: {self.stats['files_archived']}")
        print(f"  Tamanho original: {self._format_size(self.stats['original_size'])}")
        print(f"  Tamanho comprimido: {self._format_size(self.stats['compressed_size'])}")
        print(f"  Espaço economizado: {self._format_size(self.stats['space_saved'])}")
        
        if self.stats['original_size'] > 0:
            reduction = (self.stats['space_saved'] / self.stats['original_size']) * 100
            print(f"  Redução total: {reduction:.1f}%")
        
        print("="*60 + "\n")


def interactive_menu():
    """Menu interativo para gerenciamento de arquivos"""
    manager = ArchiveManager()
    
    while True:
        print("\n" + "="*60)
        print("GERENCIADOR DE ARQUIVOS")
        print("="*60)
        print("1. Comprimir arquivos individuais antigos")
        print("2. Criar arquivos por data (mensal)")
        print("3. Limpar arquivos muito antigos (> 90 dias)")
        print("4. Gerar índice de arquivos")
        print("5. Mostrar estatísticas atuais")
        print("6. Descomprimir arquivo específico")
        print("7. Configurar dias de retenção")
        print("0. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            print("\nComprimindo arquivos individuais...")
            manager.compress_individual_files()
            manager.show_statistics()
            
        elif choice == "2":
            print("\nCategorias disponíveis: all, categories, restaurants, products")
            category = input("Categoria (Enter para 'all'): ").strip() or "all"
            manager.archive_by_date(category)
            manager.show_statistics()
            
        elif choice == "3":
            days = input("Remover arquivos mais antigos que (dias) [90]: ").strip()
            days = int(days) if days else 90
            manager.cleanup_old_archives(days)
            
        elif choice == "4":
            index = manager.generate_index()
            print(f"\nÍndice gerado com {index['statistics']['total_archives']} arquivos")
            print(f"Tamanho total: {manager._format_size(index['statistics']['total_size'])}")
            
        elif choice == "5":
            # Analisa situação atual
            total_size = 0
            file_count = 0
            
            for subdir in ["categories", "restaurants", "products"]:
                directory = manager.data_dir / subdir
                if directory.exists():
                    for file_path in directory.glob("**/*.csv"):
                        total_size += file_path.stat().st_size
                        file_count += 1
            
            print(f"\nArquivos CSV não comprimidos: {file_count}")
            print(f"Tamanho total: {manager._format_size(total_size)}")
            
            # Mostra estatísticas de arquivos
            archive_count = len(list(manager.archive_dir.glob("*")))
            print(f"\nArquivos comprimidos: {archive_count}")
            
        elif choice == "6":
            archives = list(manager.archive_dir.glob("*"))
            if not archives:
                print("\nNenhum arquivo encontrado!")
                continue
                
            print("\nArquivos disponíveis:")
            for i, archive in enumerate(archives, 1):
                print(f"{i}. {archive.name}")
            
            try:
                idx = int(input("\nEscolha o arquivo: ")) - 1
                if 0 <= idx < len(archives):
                    if archives[idx].suffix == '.gz':
                        manager.decompress_file(archives[idx])
                    else:
                        manager.extract_archive(archives[idx])
                else:
                    print("Opção inválida!")
            except ValueError:
                print("Entrada inválida!")
                
        elif choice == "7":
            days = input(f"Dias de retenção atual ({manager.retention_days}): ").strip()
            if days.isdigit():
                manager.retention_days = int(days)
                print(f"Retenção atualizada para {manager.retention_days} dias")
                
        elif choice == "0":
            break
        else:
            print("Opção inválida!")
        
        input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciador de arquivamento de dados")
    parser.add_argument("--compress", action="store_true", 
                       help="Comprimir arquivos antigos")
    parser.add_argument("--archive", action="store_true",
                       help="Criar arquivos por data")
    parser.add_argument("--cleanup", type=int, metavar="DAYS",
                       help="Remover arquivos mais antigos que X dias")
    parser.add_argument("--index", action="store_true",
                       help="Gerar índice de arquivos")
    parser.add_argument("--retention", type=int, default=7,
                       help="Dias de retenção (padrão: 7)")
    
    args = parser.parse_args()
    
    if any([args.compress, args.archive, args.cleanup, args.index]):
        # Modo linha de comando
        manager = ArchiveManager(retention_days=args.retention)
        
        if args.compress:
            manager.compress_individual_files()
            
        if args.archive:
            manager.archive_by_date()
            
        if args.cleanup:
            manager.cleanup_old_archives(args.cleanup)
            
        if args.index:
            manager.generate_index()
            
        manager.show_statistics()
    else:
        # Modo interativo
        interactive_menu()