#!/usr/bin/env python3
"""
Script para verificar contagem real de restaurantes no banco
"""

from src.config.database import execute_query

def check_restaurants_count():
    """Verifica contagem atual de restaurantes"""
    
    print("🔍 VERIFICANDO RESTAURANTES NO BANCO...")
    
    # 1. Contagem total
    total = execute_query("SELECT COUNT(*) as total FROM restaurants_unique", fetch_one=True)
    print(f"📊 Total de restaurantes únicos: {total['total']}")
    
    # 2. Restaurantes recentes (últimas 2 horas)
    recent = execute_query("""
        SELECT COUNT(*) as recent 
        FROM restaurants_unique 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 2 HOUR)
    """, fetch_one=True)
    print(f"🆕 Restaurantes recentes (2h): {recent['recent']}")
    
    # 3. Últimos 10 restaurantes adicionados
    print("\n📋 ÚLTIMOS 10 RESTAURANTES:")
    latest = execute_query("""
        SELECT name, created_at, address
        FROM restaurants_unique 
        ORDER BY created_at DESC 
        LIMIT 10
    """, fetch_all=True)
    
    for i, rest in enumerate(latest or [], 1):
        print(f"  {i:2}. {rest['name']} - {rest['created_at'].strftime('%H:%M:%S')}")
    
    # 4. Contagem por categoria
    print("\n🏷️ RESTAURANTES POR CATEGORIA:")
    category_stats = execute_query("""
        SELECT 
            c.name as categoria,
            COUNT(DISTINCT ru.id) as restaurantes
        FROM categories c
        LEFT JOIN restaurant_categories rc ON c.id = rc.category_id
        LEFT JOIN restaurants_unique ru ON rc.restaurant_id = ru.id
        GROUP BY c.name
        ORDER BY restaurantes DESC
        LIMIT 10
    """, fetch_all=True)
    
    for cat in category_stats or []:
        print(f"  • {cat['categoria']}: {cat['restaurantes']} restaurantes")
    
    # 5. Estatísticas de relacionamentos
    relationships = execute_query("SELECT COUNT(*) as total FROM restaurant_categories", fetch_one=True)
    print(f"\n🔗 Total de relacionamentos: {relationships['total']}")
    
    if total['total'] > 0 and relationships['total'] > 0:
        avg_categories = relationships['total'] / total['total']
        print(f"📈 Média de categorias por restaurante: {avg_categories:.1f}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    check_restaurants_count()