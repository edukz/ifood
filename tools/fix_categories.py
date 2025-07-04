#!/usr/bin/env python3
"""
Script para corrigir categorias incorretas nos dados do iFood
Remove tags promocionais como 'Novidade' e as substitui por categorias apropriadas
"""

import csv
import os
from pathlib import Path
import shutil
from datetime import datetime

def fix_incorrect_category(category: str, restaurant_name: str) -> str:
    """Corrige categorias incorretas como 'Novidade' baseado no contexto"""
    # Lista de categorias que são tags promocionais, não tipos de comida
    promotional_tags = ['novidade', 'novo', 'new', 'promoção', 'oferta', 'destaque']
    
    # Se a categoria é uma tag promocional
    if any(tag in category.lower() for tag in promotional_tags):
        # Analisa o nome do restaurante para inferir a categoria correta
        restaurant_lower = restaurant_name.lower()
        
        # Mapeamento inteligente baseado no nome
        if any(keyword in restaurant_lower for keyword in ['açaí', 'acai']):
            return 'Açaí'
        elif any(keyword in restaurant_lower for keyword in ['pizza', 'pizzaria']):
            return 'Pizzas'
        elif any(keyword in restaurant_lower for keyword in ['japonês', 'japonesa', 'sushi', 'japanese']):
            return 'Japonesa'
        elif any(keyword in restaurant_lower for keyword in ['burger', 'hamburg', 'lanch']):
            return 'Lanches'
        elif any(keyword in restaurant_lower for keyword in ['brasileira', 'caseira', 'marmita', 'prato']):
            return 'Brasileira'
        elif any(keyword in restaurant_lower for keyword in ['doce', 'sobremesa', 'sorvete']):
            return 'Doces & Bolos'
        elif any(keyword in restaurant_lower for keyword in ['bebida', 'drink', 'suco']):
            return 'Bebidas'
        elif any(keyword in restaurant_lower for keyword in ['fast', 'express']):
            return 'Fast Food'
        else:
            # Fallback: usa alimentação geral
            return 'Alimentação'
    
    # Se não é tag promocional, retorna a categoria original
    return category

def fix_restaurant_categories():
    """Corrige categorias nos arquivos de restaurantes"""
    base_dir = Path("/mnt/c/Users/edukz/Desktop/ifood")
    restaurants_dir = base_dir / "data" / "restaurants"
    
    if not restaurants_dir.exists():
        print("❌ Diretório de restaurantes não encontrado")
        return
    
    fixed_count = 0
    files_processed = 0
    
    # Processa todos os arquivos CSV de restaurantes
    for csv_file in restaurants_dir.glob("*.csv"):
        print(f"🔍 Processando: {csv_file.name}")
        files_processed += 1
        
        # Cria backup
        backup_file = csv_file.with_suffix('.csv.backup')
        shutil.copy2(csv_file, backup_file)
        
        # Lê o arquivo original
        rows = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = [field for field in reader.fieldnames if field is not None]
            
            for row in reader:
                # Remove campos None
                cleaned_row = {k: v for k, v in row.items() if k is not None}
                
                original_category = cleaned_row.get('categoria', '')
                restaurant_name = cleaned_row.get('nome', '')
                
                # Corrige a categoria se necessário
                new_category = fix_incorrect_category(original_category, restaurant_name)
                
                if new_category != original_category:
                    cleaned_row['categoria'] = new_category
                    fixed_count += 1
                    print(f"  ✅ {restaurant_name}: '{original_category}' → '{new_category}'")
                
                rows.append(cleaned_row)
        
        # Escreve o arquivo corrigido
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"\n📊 RESULTADO:")
    print(f"  📁 Arquivos processados: {files_processed}")
    print(f"  ✅ Categorias corrigidas: {fixed_count}")
    print(f"  📅 Data de correção: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if fixed_count > 0:
        print(f"\n💡 Backups criados com extensão .backup")
        print(f"🔄 Recomendado: Regenerar índices de busca após esta correção")

def remove_incorrect_product_files():
    """Remove arquivos de produtos com categorias incorretas"""
    base_dir = Path("/mnt/c/Users/edukz/Desktop/ifood")
    products_dir = base_dir / "data" / "products"
    
    if not products_dir.exists():
        print("❌ Diretório de produtos não encontrado")
        return
    
    # Lista de padrões de arquivo com categorias incorretas
    incorrect_patterns = ['produtos_novidade_*', 'produtos_novo_*', 'produtos_promoção_*']
    
    removed_count = 0
    for pattern in incorrect_patterns:
        for file_path in products_dir.glob(pattern):
            print(f"🗑️  Removendo arquivo incorreto: {file_path.name}")
            file_path.unlink()
            removed_count += 1
    
    print(f"📊 Arquivos removidos: {removed_count}")

if __name__ == "__main__":
    print("🔧 CORREÇÃO DE CATEGORIAS INCORRETAS")
    print("=" * 50)
    
    # Remove arquivos de produtos incorretos
    print("\n1️⃣ Removendo arquivos de produtos com categorias incorretas...")
    remove_incorrect_product_files()
    
    # Corrige categorias nos restaurantes
    print("\n2️⃣ Corrigindo categorias nos arquivos de restaurantes...")
    fix_restaurant_categories()
    
    print("\n✅ Correção concluída!")
    print("💡 Dica: Execute a extração de produtos novamente para gerar dados corretos")