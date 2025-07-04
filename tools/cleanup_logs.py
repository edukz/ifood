#!/usr/bin/env python3
"""
Ferramenta para limpeza e organização de logs
Remove logs antigos e organiza os logs existentes
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def count_files_in_directory(directory):
    """Conta arquivos em um diretório"""
    if not directory.exists():
        return 0
    return len(list(directory.glob("*")))


def cleanup_archive_logs(archive_dir, keep_days=7):
    """Limpa logs antigos do arquivo"""
    if not archive_dir.exists():
        print(f"❌ Diretório não encontrado: {archive_dir}")
        return
    
    cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
    
    removed_count = 0
    kept_count = 0
    
    for log_file in archive_dir.glob("*.log"):
        try:
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                removed_count += 1
            else:
                kept_count += 1
        except Exception as e:
            print(f"⚠️  Erro ao processar {log_file.name}: {e}")
    
    return removed_count, kept_count


def organize_current_logs(logs_dir):
    """Organiza logs atuais no diretório principal"""
    if not logs_dir.exists():
        print(f"❌ Diretório não encontrado: {logs_dir}")
        return
    
    # Agrupa logs por data
    logs_by_date = {}
    
    for log_file in logs_dir.glob("*.log"):
        try:
            # Extrai data do nome do arquivo ou da modificação
            mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            date_key = mod_time.strftime('%Y%m%d')
            
            if date_key not in logs_by_date:
                logs_by_date[date_key] = []
            
            logs_by_date[date_key].append(log_file)
        except Exception as e:
            print(f"⚠️  Erro ao processar {log_file.name}: {e}")
    
    # Consolida logs do mesmo dia
    consolidated_count = 0
    for date_key, log_files in logs_by_date.items():
        if len(log_files) > 1:
            # Cria arquivo consolidado
            consolidated_file = logs_dir / f"ifood_scraper_{date_key}_consolidated.log"
            
            try:
                with open(consolidated_file, 'w', encoding='utf-8') as outfile:
                    outfile.write(f"=== Logs Consolidados - {date_key} ===\n\n")
                    
                    for log_file in sorted(log_files):
                        outfile.write(f"\n=== {log_file.name} ===\n")
                        with open(log_file, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                        
                        # Remove arquivo original após consolidação
                        log_file.unlink()
                        consolidated_count += 1
                
                print(f"✅ Consolidados {len(log_files)} logs do dia {date_key}")
            except Exception as e:
                print(f"❌ Erro ao consolidar logs do dia {date_key}: {e}")
    
    return consolidated_count


def main():
    """Execução principal da limpeza"""
    print("🧹 iFood Scraper - Limpeza de Logs")
    print("=" * 50)
    
    # Diretórios
    logs_dir = Path("logs")
    archive_dir = Path("archive/old_logs")
    screenshots_dir = Path("archive/screenshots")
    
    # Estatísticas iniciais
    print("\n📊 Estatísticas antes da limpeza:")
    print(f"   Logs atuais: {count_files_in_directory(logs_dir)} arquivos")
    print(f"   Logs arquivados: {count_files_in_directory(archive_dir)} arquivos")
    print(f"   Screenshots: {count_files_in_directory(screenshots_dir)} arquivos")
    
    # Pergunta ao usuário
    print("\n🤔 O que deseja fazer?")
    print("1. Limpar logs antigos (manter últimos 7 dias)")
    print("2. Limpar TODOS os logs arquivados")
    print("3. Consolidar logs do mesmo dia")
    print("4. Limpeza completa (1 + 3)")
    print("0. Cancelar")
    
    choice = input("\nEscolha uma opção (0-4): ").strip()
    
    if choice == "0":
        print("❌ Operação cancelada")
        return
    
    print("\n🔄 Processando...")
    
    if choice in ["1", "4"]:
        # Limpa logs antigos
        removed, kept = cleanup_archive_logs(archive_dir, keep_days=7)
        print(f"✅ Logs arquivados: {removed} removidos, {kept} mantidos")
    
    if choice == "2":
        # Remove TODOS os logs arquivados
        if archive_dir.exists():
            confirm = input("⚠️  Tem certeza? Isso removerá TODOS os logs arquivados (s/N): ")
            if confirm.lower() == 's':
                shutil.rmtree(archive_dir)
                os.makedirs(archive_dir, exist_ok=True)
                print("✅ Todos os logs arquivados foram removidos")
            else:
                print("❌ Operação cancelada")
    
    if choice in ["3", "4"]:
        # Consolida logs do mesmo dia
        consolidated = organize_current_logs(logs_dir)
        print(f"✅ Logs consolidados: {consolidated} arquivos processados")
    
    # Estatísticas finais
    print("\n📊 Estatísticas após a limpeza:")
    print(f"   Logs atuais: {count_files_in_directory(logs_dir)} arquivos")
    print(f"   Logs arquivados: {count_files_in_directory(archive_dir)} arquivos")
    print(f"   Screenshots: {count_files_in_directory(screenshots_dir)} arquivos")
    
    print("\n✨ Limpeza concluída!")
    
    # Sugestão adicional
    if count_files_in_directory(archive_dir) > 100:
        print("\n💡 Dica: Você ainda tem muitos logs arquivados.")
        print("   Use a opção 2 para uma limpeza mais agressiva.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Operação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)