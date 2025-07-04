#!/usr/bin/env python3
"""
Script para atualizar índices de busca após correção de categorias
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.search_optimizer import SearchIndex, QueryOptimizer

def refresh_search_indexes():
    """Atualiza os índices de busca com dados corrigidos"""
    print("🔄 ATUALIZAÇÃO DOS ÍNDICES DE BUSCA")
    print("=" * 50)
    
    try:
        # Cria nova instância do índice
        print("📊 Criando índices de busca...")
        search_index = SearchIndex()
        
        # Recria banco de dados
        print("🗃️  Criando banco de dados...")
        search_index.create_database_indexes()
        
        # Recarrega todos os dados
        print("📥 Carregando dados corrigidos...")
        search_index.load_data_to_database()
        
        # Testa se os índices estão funcionando
        print("🧪 Testando índices...")
        query_optimizer = QueryOptimizer()
        
        # Busca categorias populares para verificar
        categories = query_optimizer.get_popular_categories(limit=10)
        
        print(f"\n✅ Índices atualizados com sucesso!")
        print(f"📊 {len(categories)} categorias encontradas:")
        
        for i, cat in enumerate(categories[:5], 1):
            name = cat.get('categoria', 'N/A')
            count = cat.get('restaurant_count', 0)
            print(f"  {i}. {name:<15} ({count} restaurantes)")
        
        # Verifica se ainda existe categoria "Novidade"
        novidade_found = any(cat.get('categoria', '').lower() == 'novidade' for cat in categories)
        
        if novidade_found:
            print(f"\n⚠️  ATENÇÃO: Ainda existem registros com categoria 'Novidade'")
            print(f"💡 Execute novamente o script de correção de categorias")
        else:
            print(f"\n🎉 Sucesso! Nenhuma categoria 'Novidade' encontrada")
        
        # Estatísticas do banco
        stats = query_optimizer.get_database_statistics()
        if stats:
            print(f"\n📈 ESTATÍSTICAS DO BANCO:")
            print(f"  🏪 Restaurantes: {stats.get('total_restaurants', 0):,}")
            print(f"  🍕 Produtos: {stats.get('total_products', 0):,}")
            print(f"  📂 Categorias: {stats.get('total_categories', 0):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar índices: {e}")
        return False

if __name__ == "__main__":
    success = refresh_search_indexes()
    
    if success:
        print(f"\n✅ Atualização concluída com sucesso!")
        print(f"🔍 O sistema de busca agora reflete as categorias corrigidas")
    else:
        print(f"\n❌ Falha na atualização dos índices")
        sys.exit(1)