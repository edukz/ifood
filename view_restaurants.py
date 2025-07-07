#!/usr/bin/env python3
"""
Script para visualizar restaurantes no banco de dados
"""

import sys
from tabulate import tabulate
from datetime import datetime
import pandas as pd

# Adicionar o diretório raiz ao path
sys.path.append('.')

from src.database.database_adapter import get_database_manager
from src.utils.logger import setup_logger

logger = setup_logger("ViewRestaurants")

def view_restaurants(city=None, category=None, limit=50, search=None, export_csv=False):
    """Visualiza restaurantes no banco com várias opções de filtro"""
    
    db = get_database_manager()
    
    try:
        with db.db_v2.get_cursor() as (cursor, _):
            # Query base
            query = """
                SELECT 
                    r.id,
                    r.name,
                    r.city,
                    c.name as category,
                    r.rating,
                    r.delivery_time,
                    r.delivery_fee,
                    r.distance,
                    r.last_scraped,
                    r.created_at
                FROM restaurants r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.is_active = TRUE
            """
            
            params = []
            conditions = []
            
            # Aplicar filtros
            if city:
                conditions.append("r.city = %s")
                params.append(city)
                
            if category:
                conditions.append("c.name = %s")
                params.append(category)
                
            if search:
                conditions.append("r.name LIKE %s")
                params.append(f"%{search}%")
            
            # Adicionar condições à query
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # Ordenar e limitar
            query += " ORDER BY r.rating DESC, r.name"
            if limit:
                query += f" LIMIT {limit}"
            
            # Executar query
            cursor.execute(query, params)
            restaurants = cursor.fetchall()
            
            if not restaurants:
                print("\n❌ Nenhum restaurante encontrado com os filtros especificados.")
                return
            
            # Preparar dados para exibição
            table_data = []
            for rest in restaurants:
                table_data.append([
                    rest['id'],
                    rest['name'][:40] + '...' if len(rest['name']) > 40 else rest['name'],
                    rest['city'],
                    rest['category'] or 'N/A',
                    f"{rest['rating']:.1f}" if rest['rating'] else 'N/A',
                    rest['delivery_time'] or 'N/A',
                    rest['delivery_fee'] or 'N/A',
                    rest['distance'] or 'N/A',
                    rest['last_scraped'].strftime('%d/%m %H:%M') if rest['last_scraped'] else 'N/A'
                ])
            
            # Exibir tabela
            headers = ['ID', 'Nome', 'Cidade', 'Categoria', 'Nota', 'Tempo', 'Taxa', 'Dist.', 'Última Coleta']
            
            print(f"\n📊 RESTAURANTES NO BANCO DE DADOS")
            print(f"{'='*100}")
            
            # Mostrar filtros aplicados
            filters = []
            if city:
                filters.append(f"Cidade: {city}")
            if category:
                filters.append(f"Categoria: {category}")
            if search:
                filters.append(f"Busca: '{search}'")
            
            if filters:
                print(f"🔍 Filtros: {' | '.join(filters)}")
                print(f"{'='*100}")
            
            print(f"\n🏪 Total encontrado: {len(restaurants)} restaurantes\n")
            
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
            # Exportar para CSV se solicitado
            if export_csv:
                df = pd.DataFrame(restaurants)
                filename = f"restaurantes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"\n✅ Dados exportados para: {filename}")
            
            # Estatísticas resumidas
            print(f"\n📈 ESTATÍSTICAS:")
            print(f"{'='*50}")
            
            # Estatísticas por categoria
            cursor.execute("""
                SELECT 
                    c.name as category,
                    COUNT(r.id) as total,
                    AVG(r.rating) as avg_rating
                FROM restaurants r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.is_active = TRUE
                GROUP BY c.name
                ORDER BY total DESC
            """)
            
            cat_stats = cursor.fetchall()
            
            print("\n📊 Por Categoria:")
            for stat in cat_stats[:10]:  # Top 10 categorias
                avg_rating = f"{stat['avg_rating']:.1f}" if stat['avg_rating'] else "N/A"
                print(f"  • {stat['category']}: {stat['total']} restaurantes (média: {avg_rating}⭐)")
            
            # Estatísticas por cidade
            cursor.execute("""
                SELECT 
                    city,
                    COUNT(*) as total
                FROM restaurants
                WHERE is_active = TRUE
                GROUP BY city
                ORDER BY total DESC
            """)
            
            city_stats = cursor.fetchall()
            
            print("\n🏙️ Por Cidade:")
            for stat in city_stats:
                print(f"  • {stat['city']}: {stat['total']} restaurantes")
            
            # Top restaurantes por nota
            print("\n🌟 Top 10 Restaurantes (por nota):")
            for i, rest in enumerate(restaurants[:10], 1):
                rating = f"{rest['rating']:.1f}" if rest['rating'] else "N/A"
                print(f"  {i}. {rest['name']} ({rating}⭐) - {rest['category']}")
                
    except Exception as e:
        logger.error(f"Erro ao consultar restaurantes: {e}")
        print(f"\n❌ Erro: {e}")
    finally:
        db.close()


def main():
    """Função principal com interface de linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualizar restaurantes no banco de dados')
    parser.add_argument('-c', '--city', help='Filtrar por cidade')
    parser.add_argument('-t', '--category', help='Filtrar por categoria')
    parser.add_argument('-s', '--search', help='Buscar por nome')
    parser.add_argument('-l', '--limit', type=int, default=50, help='Limite de resultados (padrão: 50)')
    parser.add_argument('-e', '--export', action='store_true', help='Exportar para CSV')
    parser.add_argument('--all', action='store_true', help='Mostrar todos (sem limite)')
    
    args = parser.parse_args()
    
    # Se --all, remover limite
    limit = None if args.all else args.limit
    
    view_restaurants(
        city=args.city,
        category=args.category,
        search=args.search,
        limit=limit,
        export_csv=args.export
    )


if __name__ == "__main__":
    main()