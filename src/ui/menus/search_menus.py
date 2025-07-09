#!/usr/bin/env python3
"""
Sistema de Busca - Menus especializados para busca e indexação
"""

from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

# Imports para funcionalidades de busca
from src.utils.search_optimizer import SearchIndex, QueryOptimizer
from src.config.database import execute_query
from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu

# Optional imports
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    def tabulate(data, headers=None, **kwargs):
        """Fallback function for when tabulate is not available"""
        if not data:
            return "Nenhum dado disponível"
        
        result = []
        if headers:
            result.append("\t".join(str(h) for h in headers))
            result.append("-" * 50)
        
        for row in data:
            if isinstance(row, dict):
                result.append("\t".join(str(row.get(h, '')) for h in (headers or row.keys())))
            else:
                result.append("\t".join(str(cell) for cell in row))
        
        return "\n".join(result)


class SearchMenus(BaseMenu):
    """Menus especializados para sistema de busca"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path, 
                 search_optimizer: QueryOptimizer):
        super().__init__("Busca", session_stats, data_dir)
        self.search_optimizer = search_optimizer
        self.db = get_database_manager()
    
    def menu_search_system(self):
        """Menu do sistema de busca"""
        options = [
            "1. 🔧 Criar/Atualizar índices",
            "2. 🔍 Buscar restaurantes",
            "3. 🍕 Buscar produtos",
            "4. 📊 Categorias populares",
            "5. 💰 Análise de preços",
            "6. 🎯 Recomendações",
            "7. 📈 Estatísticas do banco"
        ]
        
        self.show_menu("🔍 SISTEMA DE BUSCA", options)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._create_search_indexes()
        elif choice == "2":
            self._search_restaurants()
        elif choice == "3":
            self._search_products()
        elif choice == "4":
            self._show_popular_categories()
        elif choice == "5":
            self._analyze_prices()
        elif choice == "6":
            self._show_recommendations()
        elif choice == "7":
            self._show_database_stats()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _create_search_indexes(self):
        """Cria índices de busca"""
        print("\n🔧 Criando índices de busca...")
        
        try:
            index = SearchIndex()
            index.create_database_indexes()
            index.load_data_to_database()
            self.show_success("Índices criados com sucesso!")
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _search_restaurants(self):
        """Busca restaurantes com filtros avançados"""
        print("\n🔍 BUSCA AVANÇADA DE RESTAURANTES")
        print("═" * 50)
        
        # Opções de busca
        search_options = [
            "1. 🏷️  Buscar por categoria",
            "2. 🏪 Buscar por nome",
            "3. ⭐ Buscar por avaliação",
            "4. 🕐 Buscar por tempo de entrega",
            "5. 💰 Buscar por taxa de entrega",
            "6. 🌍 Buscar por localização",
            "7. 🔍 Busca personalizada"
        ]
        
        self.show_menu("🔍 OPÇÕES DE BUSCA", search_options)
        choice = self.get_user_choice(7)
        
        try:
            with self.db.get_cursor() as (cursor, _):
                if choice == "1":
                    self._search_by_category(cursor)
                elif choice == "2":
                    self._search_by_name(cursor)
                elif choice == "3":
                    self._search_by_rating(cursor)
                elif choice == "4":
                    self._search_by_delivery_time(cursor)
                elif choice == "5":
                    self._search_by_delivery_fee(cursor)
                elif choice == "6":
                    self._search_by_location(cursor)
                elif choice == "7":
                    self._custom_search(cursor)
        except Exception as e:
            self.show_error(f"Erro na busca: {e}")
        
        self.pause()
    
    def _search_by_category(self, cursor):
        """Busca restaurantes por categoria"""
        category = input("\nDigite a categoria (ex: 'Pizza', 'Japonesa'): ").strip()
        if not category:
            return
        
        query = """
        SELECT r.id, r.name, c.name as category, r.rating, r.delivery_time, r.delivery_fee, r.distance, r.city
        FROM restaurants r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE c.name LIKE %s
        ORDER BY r.rating DESC, r.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (f"%{category}%",))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} restaurantes da categoria '{category}':")
            self._display_restaurants_results(results)
        else:
            print(f"\n❌ Nenhum restaurante encontrado para a categoria '{category}'")
    
    def _search_by_name(self, cursor):
        """Busca restaurantes por nome"""
        name = input("\nDigite o nome do restaurante: ").strip()
        if not name:
            return
        
        query = """
        SELECT r.id, r.name, c.name as category, r.rating, r.delivery_time, r.delivery_fee, r.distance, r.city
        FROM restaurants r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.name LIKE %s
        ORDER BY r.rating DESC, r.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (f"%{name}%",))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} restaurantes com nome '{name}':")
            self._display_restaurants_results(results)
        else:
            print(f"\n❌ Nenhum restaurante encontrado com nome '{name}'")
    
    def _search_by_rating(self, cursor):
        """Busca restaurantes por avaliação"""
        min_rating = input("\nDigite a avaliação mínima (0-5): ").strip()
        try:
            min_rating = float(min_rating)
            if min_rating < 0 or min_rating > 5:
                raise ValueError("Avaliação deve estar entre 0 e 5")
        except ValueError as e:
            self.show_error(f"Avaliação inválida: {e}")
            return
        
        query = """
        SELECT r.id, r.name, c.name as category, r.rating, r.delivery_time, r.delivery_fee, r.distance, r.city
        FROM restaurants r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.rating >= %s
        ORDER BY r.rating DESC, r.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (min_rating,))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} restaurantes com avaliação >= {min_rating}:")
            self._display_restaurants_results(results)
        else:
            print(f"\n❌ Nenhum restaurante encontrado com avaliação >= {min_rating}")
    
    def _search_by_delivery_time(self, cursor):
        """Busca restaurantes por tempo de entrega"""
        max_time = input("\nDigite o tempo máximo de entrega (em minutos): ").strip()
        try:
            max_time = int(max_time)
        except ValueError:
            self.show_error("Tempo inválido. Digite apenas números.")
            return
        
        query = """
        SELECT r.id, r.name, c.name as category, r.rating, r.delivery_time, r.delivery_fee, r.distance, r.city
        FROM restaurants r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.delivery_time LIKE %s OR r.delivery_time LIKE %s
        ORDER BY r.rating DESC, r.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (f"%{max_time}%", f"%-{max_time}%"))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} restaurantes com tempo <= {max_time} min:")
            self._display_restaurants_results(results)
        else:
            print(f"\n❌ Nenhum restaurante encontrado com tempo <= {max_time} min")
    
    def _search_by_delivery_fee(self, cursor):
        """Busca restaurantes por taxa de entrega"""
        fee_options = [
            "1. 🆓 Entrega grátis",
            "2. 💰 Até R$ 5,00",
            "3. 💰 Até R$ 10,00",
            "4. 💰 Valor personalizado"
        ]
        
        self.show_menu("💰 TAXA DE ENTREGA", fee_options)
        choice = self.get_user_choice(4)
        
        if choice == "1":
            condition = "r.delivery_fee LIKE '%grátis%' OR r.delivery_fee LIKE '%gratuita%'"
            params = ()
        elif choice == "2":
            condition = "r.delivery_fee LIKE '%R$ 5%' OR r.delivery_fee LIKE '%R$ 4%' OR r.delivery_fee LIKE '%R$ 3%' OR r.delivery_fee LIKE '%R$ 2%' OR r.delivery_fee LIKE '%R$ 1%'"
            params = ()
        elif choice == "3":
            condition = "r.delivery_fee LIKE '%R$ 10%' OR r.delivery_fee LIKE '%R$ 9%' OR r.delivery_fee LIKE '%R$ 8%' OR r.delivery_fee LIKE '%R$ 7%' OR r.delivery_fee LIKE '%R$ 6%' OR r.delivery_fee LIKE '%R$ 5%'"
            params = ()
        elif choice == "4":
            max_fee = input("\nDigite o valor máximo (ex: 8.50): ").strip()
            try:
                max_fee = float(max_fee)
                condition = "r.delivery_fee LIKE %s"
                params = (f"%{max_fee}%",)
            except ValueError:
                self.show_error("Valor inválido.")
                return
        else:
            return
        
        query = f"""
        SELECT r.id, r.name, c.name as category, r.rating, r.delivery_time, r.delivery_fee, r.distance, r.city
        FROM restaurants r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE {condition}
        ORDER BY r.rating DESC, r.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} restaurantes:")
            self._display_restaurants_results(results)
        else:
            print("\n❌ Nenhum restaurante encontrado com os critérios especificados")
    
    def _search_by_location(self, cursor):
        """Busca restaurantes por localização"""
        location = input("\nDigite a cidade ou região: ").strip()
        if not location:
            return
        
        query = """
        SELECT r.id, r.name, c.name as category, r.rating, r.delivery_time, r.delivery_fee, r.distance, r.city
        FROM restaurants r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.city LIKE %s OR r.address LIKE %s
        ORDER BY r.rating DESC, r.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (f"%{location}%", f"%{location}%"))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} restaurantes em '{location}':")
            self._display_restaurants_results(results)
        else:
            print(f"\n❌ Nenhum restaurante encontrado em '{location}'")
    
    def _custom_search(self, cursor):
        """Busca personalizada com múltiplos critérios"""
        print("\n🔍 BUSCA PERSONALIZADA")
        print("Deixe em branco para ignorar um critério")
        
        category = input("Categoria: ").strip()
        min_rating = input("Avaliação mínima (0-5): ").strip()
        max_delivery_time = input("Tempo máximo de entrega (min): ").strip()
        city = input("Cidade: ").strip()
        
        # Construir query dinamicamente
        conditions = []
        params = []
        
        if category:
            conditions.append("c.name LIKE %s")
            params.append(f"%{category}%")
        
        if min_rating:
            try:
                min_rating = float(min_rating)
                conditions.append("r.rating >= %s")
                params.append(min_rating)
            except ValueError:
                pass
        
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                conditions.append("r.delivery_time LIKE %s")
                params.append(f"%{max_delivery_time}%")
            except ValueError:
                pass
        
        if city:
            conditions.append("r.city LIKE %s")
            params.append(f"%{city}%")
        
        if not conditions:
            self.show_error("Nenhum critério especificado.")
            return
        
        query = f"""
        SELECT r.id, r.name, c.name as category, r.rating, r.delivery_time, r.delivery_fee, r.distance, r.city
        FROM restaurants r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE {' AND '.join(conditions)}
        ORDER BY r.rating DESC, r.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} restaurantes:")
            self._display_restaurants_results(results)
        else:
            print("\n❌ Nenhum restaurante encontrado com os critérios especificados")
    
    def _display_restaurants_results(self, results):
        """Exibe resultados da busca de restaurantes"""
        if not results:
            return
        
        # Preparar dados para tabela
        table_data = []
        for rest in results:
            table_data.append([
                rest.get('id', 'N/A'),
                rest.get('name', 'N/A')[:30],  # Limitar nome para caber na tela
                rest.get('category', 'N/A'),
                rest.get('rating', 'N/A'),
                rest.get('delivery_time', 'N/A'),
                rest.get('delivery_fee', 'N/A'),
                rest.get('distance', 'N/A'),
                rest.get('city', 'N/A')
            ])
        
        headers = ['ID', 'Nome', 'Categoria', 'Nota', 'Tempo', 'Taxa', 'Dist.', 'Cidade']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def _search_products(self):
        """Busca produtos com filtros avançados"""
        print("\n🍕 BUSCA AVANÇADA DE PRODUTOS")
        print("═" * 50)
        
        # Opções de busca
        search_options = [
            "1. 🏷️  Buscar por categoria",
            "2. 🍕 Buscar por nome",
            "3. 💰 Buscar por faixa de preço",
            "4. 🏪 Buscar por restaurante",
            "5. 🔍 Busca personalizada"
        ]
        
        self.show_menu("🔍 OPÇÕES DE BUSCA", search_options)
        choice = self.get_user_choice(5)
        
        try:
            with self.db.get_cursor() as (cursor, _):
                if choice == "1":
                    self._search_products_by_category(cursor)
                elif choice == "2":
                    self._search_products_by_name(cursor)
                elif choice == "3":
                    self._search_products_by_price(cursor)
                elif choice == "4":
                    self._search_products_by_restaurant(cursor)
                elif choice == "5":
                    self._custom_product_search(cursor)
        except Exception as e:
            self.show_error(f"Erro na busca: {e}")
        
        self.pause()
    
    def _search_products_by_category(self, cursor):
        """Busca produtos por categoria"""
        category = input("\nDigite a categoria (ex: 'Pizza', 'Hambúrguer'): ").strip()
        if not category:
            return
        
        query = """
        SELECT p.id, p.name, p.price, p.category, r.name as restaurant_name
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE p.category LIKE %s
        ORDER BY p.price ASC, p.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (f"%{category}%",))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} produtos da categoria '{category}':")
            self._display_products_results(results)
        else:
            print(f"\n❌ Nenhum produto encontrado para a categoria '{category}'")
    
    def _search_products_by_name(self, cursor):
        """Busca produtos por nome"""
        name = input("\nDigite o nome do produto: ").strip()
        if not name:
            return
        
        query = """
        SELECT p.id, p.name, p.price, p.category, r.name as restaurant_name
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE p.name LIKE %s
        ORDER BY p.price ASC, p.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (f"%{name}%",))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} produtos com nome '{name}':")
            self._display_products_results(results)
        else:
            print(f"\n❌ Nenhum produto encontrado com nome '{name}'")
    
    def _search_products_by_price(self, cursor):
        """Busca produtos por faixa de preço"""
        print("\n💰 BUSCA POR FAIXA DE PREÇO")
        
        min_price = input("Preço mínimo (deixe em branco para não limitar): ").strip()
        max_price = input("Preço máximo (deixe em branco para não limitar): ").strip()
        
        conditions = []
        params = []
        
        if min_price:
            try:
                min_price = float(min_price)
                conditions.append("p.price >= %s")
                params.append(min_price)
            except ValueError:
                self.show_error("Preço mínimo inválido.")
                return
        
        if max_price:
            try:
                max_price = float(max_price)
                conditions.append("p.price <= %s")
                params.append(max_price)
            except ValueError:
                self.show_error("Preço máximo inválido.")
                return
        
        if not conditions:
            self.show_error("Especifique pelo menos um limite de preço.")
            return
        
        query = f"""
        SELECT p.id, p.name, p.price, p.category, r.name as restaurant_name
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE {' AND '.join(conditions)}
        ORDER BY p.price ASC, p.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} produtos na faixa de preço:")
            self._display_products_results(results)
        else:
            print("\n❌ Nenhum produto encontrado na faixa de preço especificada")
    
    def _search_products_by_restaurant(self, cursor):
        """Busca produtos por restaurante"""
        restaurant = input("\nDigite o nome do restaurante: ").strip()
        if not restaurant:
            return
        
        query = """
        SELECT p.id, p.name, p.price, p.category, r.name as restaurant_name
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE r.name LIKE %s
        ORDER BY p.price ASC, p.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, (f"%{restaurant}%",))
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} produtos do restaurante '{restaurant}':")
            self._display_products_results(results)
        else:
            print(f"\n❌ Nenhum produto encontrado do restaurante '{restaurant}'")
    
    def _custom_product_search(self, cursor):
        """Busca personalizada de produtos"""
        print("\n🔍 BUSCA PERSONALIZADA DE PRODUTOS")
        print("Deixe em branco para ignorar um critério")
        
        name = input("Nome do produto: ").strip()
        category = input("Categoria: ").strip()
        restaurant = input("Restaurante: ").strip()
        min_price = input("Preço mínimo: ").strip()
        max_price = input("Preço máximo: ").strip()
        
        # Construir query dinamicamente
        conditions = []
        params = []
        
        if name:
            conditions.append("p.name LIKE %s")
            params.append(f"%{name}%")
        
        if category:
            conditions.append("p.category LIKE %s")
            params.append(f"%{category}%")
        
        if restaurant:
            conditions.append("r.name LIKE %s")
            params.append(f"%{restaurant}%")
        
        if min_price:
            try:
                min_price = float(min_price)
                conditions.append("p.price >= %s")
                params.append(min_price)
            except ValueError:
                pass
        
        if max_price:
            try:
                max_price = float(max_price)
                conditions.append("p.price <= %s")
                params.append(max_price)
            except ValueError:
                pass
        
        if not conditions:
            self.show_error("Nenhum critério especificado.")
            return
        
        query = f"""
        SELECT p.id, p.name, p.price, p.category, r.name as restaurant_name
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE {' AND '.join(conditions)}
        ORDER BY p.price ASC, p.name ASC
        LIMIT 50
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Encontrados {len(results)} produtos:")
            self._display_products_results(results)
        else:
            print("\n❌ Nenhum produto encontrado com os critérios especificados")
    
    def _display_products_results(self, results):
        """Exibe resultados da busca de produtos"""
        if not results:
            return
        
        # Preparar dados para tabela
        table_data = []
        for product in results:
            table_data.append([
                product.get('id', 'N/A'),
                product.get('name', 'N/A')[:30],  # Limitar nome
                f"R$ {product.get('price', 0):.2f}",
                product.get('category', 'N/A'),
                product.get('restaurant_name', 'N/A')[:25]  # Limitar nome do restaurante
            ])
        
        headers = ['ID', 'Nome', 'Preço', 'Categoria', 'Restaurante']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def _show_popular_categories(self):
        """Mostra categorias mais populares"""
        print("\n📊 CATEGORIAS MAIS POPULARES")
        print("═" * 50)
        
        try:
            # Usar o search_optimizer que já tem fallback implementado
            categories = self.search_optimizer.get_popular_categories(limit=15)
            
            if categories:
                print(f"\n📋 Top {len(categories)} categorias por número de restaurantes:")
                
                table_data = []
                for i, cat in enumerate(categories, 1):
                    table_data.append([
                        i,
                        cat.get('categoria', 'N/A'),
                        cat.get('restaurant_count', 0)
                    ])
                
                headers = ['Pos', 'Categoria', 'Restaurantes']
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                print("\n❌ Nenhuma categoria encontrada")
        except Exception as e:
            self.show_error(f"Erro ao buscar categorias: {e}")
        
        self.pause()
    
    def _analyze_prices(self):
        """Análise de preços dos produtos"""
        print("\n💰 ANÁLISE DE PREÇOS")
        print("═" * 50)
        
        try:
            with self.db.get_cursor() as (cursor, _):
                # Análise geral de preços
                query = """
                SELECT 
                    COUNT(*) as total_products,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    STDDEV(price) as std_price
                FROM products
                WHERE price > 0
                """
                
                cursor.execute(query)
                stats = cursor.fetchone()
                
                if stats and stats.get('total_products', 0) > 0:
                    print(f"\n📊 Estatísticas Gerais:")
                    print(f"  Total de produtos: {stats['total_products']}")
                    print(f"  Preço médio: R$ {stats['avg_price']:.2f}")
                    print(f"  Preço mínimo: R$ {stats['min_price']:.2f}")
                    print(f"  Preço máximo: R$ {stats['max_price']:.2f}")
                    print(f"  Desvio padrão: R$ {stats['std_price']:.2f}")
                    
                    # Análise por categoria
                    query = """
                    SELECT 
                        category,
                        COUNT(*) as count,
                        AVG(price) as avg_price,
                        MIN(price) as min_price,
                        MAX(price) as max_price
                    FROM products
                    WHERE price > 0 AND category IS NOT NULL
                    GROUP BY category
                    HAVING COUNT(*) >= 5
                    ORDER BY avg_price DESC
                    LIMIT 10
                    """
                    
                    cursor.execute(query)
                    categories = cursor.fetchall()
                    
                    if categories:
                        print(f"\n📋 Top 10 categorias por preço médio:")
                        
                        table_data = []
                        for cat in categories:
                            table_data.append([
                                cat.get('category', 'N/A'),
                                cat.get('count', 0),
                                f"R$ {cat.get('avg_price', 0):.2f}",
                                f"R$ {cat.get('min_price', 0):.2f}",
                                f"R$ {cat.get('max_price', 0):.2f}"
                            ])
                        
                        headers = ['Categoria', 'Produtos', 'Preço Médio', 'Mín', 'Máx']
                        print(tabulate(table_data, headers=headers, tablefmt='grid'))
                else:
                    print("\n❌ Nenhum produto com preço encontrado")
        except Exception as e:
            self.show_error(f"Erro na análise de preços: {e}")
        
        self.pause()
    
    def _show_recommendations(self):
        """Sistema de recomendações"""
        print("\n🎯 SISTEMA DE RECOMENDAÇÕES")
        print("═" * 50)
        
        options = [
            "1. 🔥 Produtos mais populares",
            "2. ⭐ Produtos melhor avaliados",
            "3. 📈 Produtos em alta",
            "4. 🎲 Descobrir novos produtos"
        ]
        
        self.show_menu("🎯 RECOMENDAÇÕES", options)
        choice = self.get_user_choice(4)
        
        try:
            with self.db.get_cursor() as (cursor, _):
                if choice == "1":
                    self._recommend_popular_products(cursor)
                elif choice == "2":
                    self._recommend_best_rated(cursor)
                elif choice == "3":
                    self._recommend_trending(cursor)
                elif choice == "4":
                    self._recommend_discovery(cursor)
        except Exception as e:
            self.show_error(f"Erro nas recomendações: {e}")
        
        self.pause()
    
    def _recommend_popular_products(self, cursor):
        """Recomenda produtos populares"""
        print("\n🔥 PRODUTOS MAIS POPULARES")
        
        # Simular popularidade baseada em restaurantes com mais produtos
        query = """
        SELECT p.name, p.price, p.category, r.name as restaurant_name, 
               COUNT(*) OVER (PARTITION BY p.restaurant_id) as restaurant_products
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE p.price > 0
        ORDER BY restaurant_products DESC, p.price ASC
        LIMIT 20
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Top 20 produtos populares:")
            self._display_products_results(results)
        else:
            print("\n❌ Nenhum produto popular encontrado")
    
    def _recommend_best_rated(self, cursor):
        """Recomenda produtos de restaurantes melhor avaliados"""
        print("\n⭐ PRODUTOS DE RESTAURANTES MELHOR AVALIADOS")
        
        query = """
        SELECT p.name, p.price, p.category, r.name as restaurant_name, r.rating
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE p.price > 0 AND r.rating >= 4.5
        ORDER BY r.rating DESC, p.price ASC
        LIMIT 20
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Top 20 produtos de restaurantes bem avaliados:")
            self._display_products_results(results)
        else:
            print("\n❌ Nenhum produto de restaurante bem avaliado encontrado")
    
    def _recommend_trending(self, cursor):
        """Recomenda produtos em alta (simulado)"""
        print("\n📈 PRODUTOS EM ALTA")
        
        # Simular tendência baseada em produtos adicionados recentemente
        query = """
        SELECT p.name, p.price, p.category, r.name as restaurant_name
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE p.price > 0
        ORDER BY p.id DESC
        LIMIT 20
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 Top 20 produtos em alta:")
            self._display_products_results(results)
        else:
            print("\n❌ Nenhum produto em alta encontrado")
    
    def _recommend_discovery(self, cursor):
        """Recomenda produtos para descobrir"""
        print("\n🎲 DESCOBRIR NOVOS PRODUTOS")
        
        # Produtos aleatórios para descoberta
        query = """
        SELECT p.name, p.price, p.category, r.name as restaurant_name
        FROM products p
        JOIN restaurants r ON p.restaurant_id = r.id
        WHERE p.price > 0
        ORDER BY RAND()
        LIMIT 20
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"\n📊 20 produtos para descobrir:")
            self._display_products_results(results)
        else:
            print("\n❌ Nenhum produto para descobrir encontrado")
    
    def _show_database_stats(self):
        """Mostra estatísticas gerais do banco de dados"""
        print("\n📈 ESTATÍSTICAS DO BANCO DE DADOS")
        print("═" * 50)
        
        try:
            with self.db.get_cursor() as (cursor, _):
                # Estatísticas gerais
                stats = {}
                
                # Total de restaurantes
                cursor.execute("SELECT COUNT(*) as count FROM restaurants")
                stats['restaurants'] = cursor.fetchone()['count']
                
                # Total de produtos
                cursor.execute("SELECT COUNT(*) as count FROM products")
                stats['products'] = cursor.fetchone()['count']
                
                # Total de categorias
                cursor.execute("SELECT COUNT(DISTINCT c.name) as count FROM restaurants r LEFT JOIN categories c ON r.category_id = c.id WHERE c.name IS NOT NULL")
                stats['categories'] = cursor.fetchone()['count']
                
                # Restaurantes por cidade
                cursor.execute("SELECT COUNT(DISTINCT city) as count FROM restaurants WHERE city IS NOT NULL")
                stats['cities'] = cursor.fetchone()['count']
                
                print(f"\n📊 Estatísticas Gerais:")
                print(f"  🏪 Total de restaurantes: {stats['restaurants']}")
                print(f"  🍕 Total de produtos: {stats['products']}")
                print(f"  🏷️  Total de categorias: {stats['categories']}")
                print(f"  🌍 Total de cidades: {stats['cities']}")
                
                # Top 5 categorias usando search_optimizer
                try:
                    top_categories = self.search_optimizer.get_popular_categories(limit=5)
                    if top_categories:
                        print(f"\n📋 Top 5 categorias:")
                        for i, cat in enumerate(top_categories, 1):
                            print(f"  {i}. {cat.get('categoria', 'N/A')}: {cat.get('restaurant_count', 0)} restaurantes")
                except Exception as e:
                    print(f"\n⚠️  Erro ao obter categorias: {e}")
                
                # Top 5 cidades
                cursor.execute("""
                    SELECT city, COUNT(*) as count
                    FROM restaurants
                    WHERE city IS NOT NULL
                    GROUP BY city
                    ORDER BY count DESC
                    LIMIT 5
                """)
                
                top_cities = cursor.fetchall()
                if top_cities:
                    print(f"\n🌍 Top 5 cidades:")
                    for i, city in enumerate(top_cities, 1):
                        print(f"  {i}. {city['city']}: {city['count']} restaurantes")
        
        except Exception as e:
            self.show_error(f"Erro ao obter estatísticas: {e}")
        
        self.pause()