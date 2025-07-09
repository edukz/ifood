#!/usr/bin/env python3
"""
Custom Report - Custom filtered reports and queries
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from .reports_base import ReportsBase


class CustomReport(ReportsBase):
    """Custom filtered reports and dynamic queries"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Relatório Personalizado", session_stats, data_dir)
    
    def generate_custom_report(self):
        """Generate custom filtered report"""
        self.print_section_header("📋 RELATÓRIO PERSONALIZADO")
        
        # Get filter parameters
        filters = self._get_filter_parameters()
        
        if not filters:
            print("❌ Nenhum filtro especificado")
            return
        
        # Build and execute query
        results = self._execute_custom_query(filters)
        
        if results:
            # Display results
            self._display_custom_results(results, filters)
            
            # Show statistics
            self._show_result_statistics(results, filters)
            
            # Offer export option
            self._offer_export_option(results, filters)
        else:
            print("❌ Nenhum resultado encontrado com os filtros especificados")
    
    def _get_filter_parameters(self) -> Dict[str, Any]:
        """Get filter parameters from user input"""
        print("Filtros disponíveis (deixe em branco para ignorar):")
        
        filters = {}
        
        # Basic filters
        filters['city'] = input("🌍 Cidade: ").strip()
        filters['category'] = input("🏷️ Categoria: ").strip()
        filters['min_rating'] = input("⭐ Avaliação mínima (0-5): ").strip()
        filters['max_price'] = input("💰 Preço máximo: ").strip()
        filters['delivery_time'] = input("🕐 Tempo máximo de entrega (ex: 30): ").strip()
        
        # Advanced filters
        print("\nFiltros avançados (opcional):")
        filters['restaurant_name'] = input("🏪 Nome do restaurante: ").strip()
        filters['has_products'] = input("Apenas restaurantes com produtos? (s/n): ").strip().lower()
        filters['min_products'] = input("Número mínimo de produtos: ").strip()
        
        # Clean empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        return filters
    
    def _execute_custom_query(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute custom query based on filters"""
        try:
            # Base query with joins
            base_query = """
                SELECT 
                    r.id,
                    r.name,
                    r.category,
                    r.rating,
                    r.delivery_time,
                    r.delivery_fee,
                    r.city,
                    r.address,
                    COUNT(p.id) as product_count,
                    AVG(p.price) as avg_product_price
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
            """
            
            # Build WHERE conditions
            where_conditions = []
            params = []
            
            # City filter
            if 'city' in filters:
                where_conditions.append("r.city LIKE %s")
                params.append(f"%{filters['city']}%")
            
            # Category filter
            if 'category' in filters:
                where_conditions.append("r.category LIKE %s")
                params.append(f"%{filters['category']}%")
            
            # Rating filter
            if 'min_rating' in filters:
                try:
                    min_rating = float(filters['min_rating'])
                    where_conditions.append("r.rating >= %s")
                    params.append(min_rating)
                except ValueError:
                    pass
            
            # Restaurant name filter
            if 'restaurant_name' in filters:
                where_conditions.append("r.name LIKE %s")
                params.append(f"%{filters['restaurant_name']}%")
            
            # Delivery time filter
            if 'delivery_time' in filters:
                try:
                    max_time = int(filters['delivery_time'])
                    # This is a simplified approach - in reality, you'd need to parse the delivery_time field properly
                    where_conditions.append("r.delivery_time LIKE %s")
                    params.append(f"%{max_time}%")
                except ValueError:
                    pass
            
            # Add WHERE clause if conditions exist
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Group by restaurant
            base_query += """
                GROUP BY r.id, r.name, r.category, r.rating, r.delivery_time, 
                         r.delivery_fee, r.city, r.address
            """
            
            # Having clause for product-related filters
            having_conditions = []
            
            if filters.get('has_products') == 's':
                having_conditions.append("COUNT(p.id) > 0")
            
            if 'min_products' in filters:
                try:
                    min_products = int(filters['min_products'])
                    having_conditions.append(f"COUNT(p.id) >= {min_products}")
                except ValueError:
                    pass
            
            if having_conditions:
                base_query += " HAVING " + " AND ".join(having_conditions)
            
            # Order and limit
            base_query += " ORDER BY r.rating DESC, r.name ASC LIMIT 50"
            
            # Execute query
            results = self.safe_execute_query(base_query, tuple(params))
            
            # Apply price filter if needed (post-processing)
            if 'max_price' in filters and results:
                try:
                    max_price = float(filters['max_price'])
                    filtered_results = []
                    
                    for restaurant in results:
                        # Check if restaurant has products within price range
                        product_count = self.safe_execute_query("""
                            SELECT COUNT(*) as count
                            FROM products p
                            WHERE p.restaurant_id = %s AND p.price <= %s AND p.price > 0
                        """, (restaurant['id'], max_price), fetch_one=True)
                        
                        if product_count and product_count['count'] > 0:
                            restaurant['affordable_products'] = product_count['count']
                            filtered_results.append(restaurant)
                    
                    results = filtered_results
                except ValueError:
                    pass
            
            return results or []
            
        except Exception as e:
            self.show_error(f"Erro ao executar consulta personalizada: {e}")
            return []
    
    def _display_custom_results(self, results: List[Dict[str, Any]], filters: Dict[str, Any]):
        """Display custom query results"""
        print(f"\n📊 RESULTADO DO RELATÓRIO PERSONALIZADO ({len(results)} registros):")
        
        if not results:
            return
        
        # Prepare table data
        table_data = []
        for rest in results:
            row = [
                rest['name'][:25],
                rest['category'][:20] if rest['category'] else 'N/A',
                rest['rating'] or 'N/A',
                rest['delivery_time'][:15] if rest['delivery_time'] else 'N/A',
                rest['delivery_fee'][:10] if rest['delivery_fee'] else 'N/A',
                rest['city'][:15] if rest['city'] else 'N/A',
                rest['product_count']
            ]
            
            # Add average price if available
            if rest['avg_product_price']:
                row.append(self.format_currency(rest['avg_product_price']))
            else:
                row.append('N/A')
            
            # Add affordable products count if price filter was used
            if 'affordable_products' in rest:
                row.append(rest['affordable_products'])
            
            table_data.append(row)
        
        # Prepare headers
        headers = ['Nome', 'Categoria', 'Nota', 'Tempo', 'Taxa', 'Cidade', 'Produtos', 'Preço Médio']
        
        if any('affordable_products' in rest for rest in results):
            headers.append('Produtos Acessíveis')
        
        self.format_table(table_data, headers)
    
    def _show_result_statistics(self, results: List[Dict[str, Any]], filters: Dict[str, Any]):
        """Show statistics for the filtered results"""
        if not results:
            return
        
        print(f"\n📈 ESTATÍSTICAS DO RESULTADO:")
        
        # Basic statistics
        total_restaurants = len(results)
        print(f"  Restaurantes encontrados: {total_restaurants}")
        
        # Rating statistics
        ratings = [r['rating'] for r in results if r['rating'] is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"  Avaliação média: {avg_rating:.2f}")
            print(f"  Melhor avaliação: {max(ratings):.2f}")
            print(f"  Pior avaliação: {min(ratings):.2f}")
        
        # Product statistics
        total_products = sum(r['product_count'] for r in results)
        print(f"  Total de produtos: {total_products:,}")
        
        if total_products > 0:
            avg_products_per_restaurant = total_products / total_restaurants
            print(f"  Produtos por restaurante: {avg_products_per_restaurant:.1f}")
        
        # Price statistics
        prices = [r['avg_product_price'] for r in results if r['avg_product_price'] is not None]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"  Preço médio geral: {self.format_currency(avg_price)}")
        
        # City distribution
        cities = {}
        for r in results:
            city = r['city'] or 'N/A'
            cities[city] = cities.get(city, 0) + 1
        
        if len(cities) > 1:
            print(f"\n🌍 Distribuição por cidade:")
            for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_restaurants) * 100
                print(f"    {city}: {count} ({percentage:.1f}%)")
        
        # Category distribution
        categories = {}
        for r in results:
            category = r['category'] or 'N/A'
            categories[category] = categories.get(category, 0) + 1
        
        if len(categories) > 1:
            print(f"\n🏷️ Distribuição por categoria:")
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
            for category, count in top_categories:
                percentage = (count / total_restaurants) * 100
                print(f"    {category[:20]}: {count} ({percentage:.1f}%)")
    
    def _offer_export_option(self, results: List[Dict[str, Any]], filters: Dict[str, Any]):
        """Offer export option for the results"""
        print(f"\n📁 EXPORTAR RESULTADOS")
        export_choice = input("Deseja exportar os resultados? (s/n): ").strip().lower()
        
        if export_choice == 's':
            format_choice = input("Formato (csv/json) [csv]: ").strip().lower() or 'csv'
            
            try:
                # Create export data
                export_data = []
                for rest in results:
                    item = dict(rest)
                    # Remove non-serializable or internal fields
                    if 'affordable_products' in item:
                        del item['affordable_products']
                    export_data.append(item)
                
                # Add filter information
                filter_info = {
                    'filters_applied': filters,
                    'total_results': len(results),
                    'generated_at': self.get_base_statistics()['timestamp']
                }
                
                if format_choice == 'json':
                    full_export = {
                        'metadata': filter_info,
                        'results': export_data
                    }
                    filepath = self.export_to_json(full_export, 'relatorio_personalizado')
                else:
                    # For CSV, add filter info as comment in filename
                    filter_summary = "_".join([f"{k}_{v}" for k, v in filters.items() if len(str(v)) < 10])[:50]
                    filename = f'relatorio_personalizado_{filter_summary}'
                    
                    fieldnames = ['id', 'name', 'category', 'rating', 'delivery_time', 
                                'delivery_fee', 'city', 'address', 'product_count', 'avg_product_price']
                    filepath = self.export_to_csv(export_data, filename, fieldnames)
                
                print(f"✅ Resultados exportados para: {filepath}")
                
            except Exception as e:
                self.show_error(f"Erro ao exportar: {e}")
    
    def generate_predefined_custom_reports(self):
        """Generate predefined custom reports"""
        self.print_section_header("📋 RELATÓRIOS PERSONALIZADOS PREDEFINIDOS")
        
        predefined_options = [
            "1. 🏆 Melhores restaurantes por cidade",
            "2. 💰 Restaurantes com produtos baratos (≤ R$ 15)",
            "3. ⚡ Entrega rápida (≤ 30 min) bem avaliados",
            "4. 🍕 Restaurantes de pizza bem avaliados",
            "5. 🎯 Análise comparativa de categorias",
            "6. 📊 Restaurantes com mais produtos",
            "7. ⭐ Sem avaliação vs bem avaliados"
        ]
        
        for option in predefined_options:
            print(f"  {option}")
        
        choice = input("\nEscolha um relatório predefinido (1-7): ").strip()
        
        if choice == "1":
            self._best_restaurants_by_city()
        elif choice == "2":
            self._cheap_food_restaurants()
        elif choice == "3":
            self._fast_delivery_high_rated()
        elif choice == "4":
            self._pizza_restaurants_analysis()
        elif choice == "5":
            self._category_comparison()
        elif choice == "6":
            self._most_products_restaurants()
        elif choice == "7":
            self._rating_comparison()
        else:
            print("❌ Opção inválida")
    
    def _best_restaurants_by_city(self):
        """Best restaurants by city report"""
        self.print_subsection_header("🏆 MELHORES RESTAURANTES POR CIDADE")
        
        try:
            query = """
                SELECT 
                    r.city,
                    r.name,
                    r.category,
                    r.rating,
                    r.delivery_time,
                    COUNT(p.id) as product_count
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
                WHERE r.rating >= 4.0 AND r.city IS NOT NULL
                GROUP BY r.id, r.city, r.name, r.category, r.rating, r.delivery_time
                ORDER BY r.city, r.rating DESC, r.name
            """
            
            results = self.safe_execute_query(query)
            
            if results:
                # Group by city
                cities = {}
                for rest in results:
                    city = rest['city']
                    if city not in cities:
                        cities[city] = []
                    cities[city].append(rest)
                
                for city, restaurants in cities.items():
                    print(f"\n🌍 {city.upper()} - Top {min(5, len(restaurants))} restaurantes:")
                    
                    table_data = []
                    for i, rest in enumerate(restaurants[:5], 1):
                        table_data.append([
                            i,
                            rest['name'][:30],
                            rest['category'][:20] if rest['category'] else 'N/A',
                            rest['rating'],
                            rest['delivery_time'][:15] if rest['delivery_time'] else 'N/A',
                            rest['product_count']
                        ])
                    
                    headers = ['Pos', 'Nome', 'Categoria', 'Nota', 'Tempo', 'Produtos']
                    self.format_table(table_data, headers)
            
        except Exception as e:
            self.show_error(f"Erro no relatório por cidade: {e}")
    
    def _cheap_food_restaurants(self):
        """Restaurants with cheap food options"""
        self.print_subsection_header("💰 RESTAURANTES COM PRODUTOS BARATOS (≤ R$ 15)")
        
        try:
            query = """
                SELECT 
                    r.name,
                    r.category,
                    r.rating,
                    r.city,
                    COUNT(p.id) as cheap_products,
                    MIN(p.price) as min_price,
                    AVG(p.price) as avg_cheap_price
                FROM restaurants r
                JOIN products p ON p.restaurant_id = r.id
                WHERE p.price > 0 AND p.price <= 15
                GROUP BY r.id, r.name, r.category, r.rating, r.city
                HAVING COUNT(p.id) >= 3
                ORDER BY cheap_products DESC, r.rating DESC
                LIMIT 20
            """
            
            results = self.safe_execute_query(query)
            
            if results:
                table_data = []
                for rest in results:
                    table_data.append([
                        rest['name'][:25],
                        rest['category'][:20] if rest['category'] else 'N/A',
                        rest['rating'] or 'N/A',
                        rest['city'][:15] if rest['city'] else 'N/A',
                        rest['cheap_products'],
                        self.format_currency(rest['min_price']),
                        self.format_currency(rest['avg_cheap_price'])
                    ])
                
                headers = ['Restaurante', 'Categoria', 'Nota', 'Cidade', 'Produtos ≤R$15', 'Menor Preço', 'Preço Médio']
                self.format_table(table_data, headers)
            
        except Exception as e:
            self.show_error(f"Erro no relatório de comida barata: {e}")
    
    def _fast_delivery_high_rated(self):
        """Fast delivery and high rated restaurants"""
        self.print_subsection_header("⚡ ENTREGA RÁPIDA (≤ 30 MIN) BEM AVALIADOS")
        
        try:
            query = """
                SELECT 
                    r.name,
                    r.category,
                    r.rating,
                    r.delivery_time,
                    r.delivery_fee,
                    r.city,
                    COUNT(p.id) as product_count
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
                WHERE r.rating >= 4.0 
                  AND (r.delivery_time LIKE '%20%' OR r.delivery_time LIKE '%25%' OR r.delivery_time LIKE '%30%')
                GROUP BY r.id, r.name, r.category, r.rating, r.delivery_time, r.delivery_fee, r.city
                ORDER BY r.rating DESC, r.name
                LIMIT 25
            """
            
            results = self.safe_execute_query(query)
            
            if results:
                table_data = []
                for rest in results:
                    table_data.append([
                        rest['name'][:25],
                        rest['category'][:20] if rest['category'] else 'N/A',
                        rest['rating'],
                        rest['delivery_time'][:10] if rest['delivery_time'] else 'N/A',
                        rest['delivery_fee'][:10] if rest['delivery_fee'] else 'N/A',
                        rest['city'][:15] if rest['city'] else 'N/A',
                        rest['product_count']
                    ])
                
                headers = ['Restaurante', 'Categoria', 'Nota', 'Tempo', 'Taxa', 'Cidade', 'Produtos']
                self.format_table(table_data, headers)
            
        except Exception as e:
            self.show_error(f"Erro no relatório de entrega rápida: {e}")
    
    def _pizza_restaurants_analysis(self):
        """Pizza restaurants analysis"""
        self.print_subsection_header("🍕 ANÁLISE DE RESTAURANTES DE PIZZA")
        
        try:
            query = """
                SELECT 
                    r.name,
                    r.rating,
                    r.delivery_time,
                    r.delivery_fee,
                    r.city,
                    COUNT(p.id) as product_count,
                    AVG(p.price) as avg_price,
                    MIN(p.price) as min_price,
                    MAX(p.price) as max_price
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
                WHERE r.category LIKE '%pizza%' OR r.name LIKE '%pizza%'
                GROUP BY r.id, r.name, r.rating, r.delivery_time, r.delivery_fee, r.city
                ORDER BY r.rating DESC, product_count DESC
            """
            
            results = self.safe_execute_query(query)
            
            if results:
                print(f"Total de pizzarias encontradas: {len(results)}")
                
                # Show top rated
                print(f"\n🏆 Top 10 pizzarias melhor avaliadas:")
                top_rated = [r for r in results if r['rating'] is not None][:10]
                
                table_data = []
                for rest in top_rated:
                    table_data.append([
                        rest['name'][:25],
                        rest['rating'],
                        rest['delivery_time'][:15] if rest['delivery_time'] else 'N/A',
                        rest['city'][:15] if rest['city'] else 'N/A',
                        rest['product_count'],
                        self.format_currency(rest['avg_price']) if rest['avg_price'] else 'N/A'
                    ])
                
                headers = ['Pizzaria', 'Nota', 'Tempo', 'Cidade', 'Produtos', 'Preço Médio']
                self.format_table(table_data, headers)
                
                # Statistics
                ratings = [r['rating'] for r in results if r['rating'] is not None]
                if ratings:
                    print(f"\n📊 Estatísticas das pizzarias:")
                    print(f"  Avaliação média: {sum(ratings) / len(ratings):.2f}")
                    print(f"  Melhor avaliação: {max(ratings):.2f}")
                    print(f"  Pior avaliação: {min(ratings):.2f}")
            
        except Exception as e:
            self.show_error(f"Erro na análise de pizzarias: {e}")
    
    def _category_comparison(self):
        """Category comparison analysis"""
        self.print_subsection_header("🎯 ANÁLISE COMPARATIVA DE CATEGORIAS")
        
        categories = input("Digite as categorias para comparar (separadas por vírgula): ").strip()
        if not categories:
            print("❌ Nenhuma categoria especificada")
            return
        
        category_list = [cat.strip() for cat in categories.split(',')]
        
        try:
            comparison_data = []
            
            for category in category_list:
                stats = self.safe_execute_query("""
                    SELECT 
                        COUNT(DISTINCT r.id) as restaurant_count,
                        AVG(r.rating) as avg_rating,
                        COUNT(p.id) as product_count,
                        AVG(p.price) as avg_price
                    FROM restaurants r
                    LEFT JOIN products p ON p.restaurant_id = r.id
                    WHERE r.category LIKE %s
                """, (f"%{category}%",), fetch_one=True)
                
                if stats:
                    comparison_data.append([
                        category,
                        stats['restaurant_count'],
                        f"{stats['avg_rating']:.2f}" if stats['avg_rating'] else 'N/A',
                        stats['product_count'],
                        self.format_currency(stats['avg_price']) if stats['avg_price'] else 'N/A'
                    ])
            
            if comparison_data:
                headers = ['Categoria', 'Restaurantes', 'Nota Média', 'Produtos', 'Preço Médio']
                self.format_table(comparison_data, headers)
            
        except Exception as e:
            self.show_error(f"Erro na comparação de categorias: {e}")
    
    def _most_products_restaurants(self):
        """Restaurants with most products"""
        self.print_subsection_header("📊 RESTAURANTES COM MAIS PRODUTOS")
        
        try:
            query = """
                SELECT 
                    r.name,
                    r.category,
                    r.rating,
                    r.city,
                    COUNT(p.id) as product_count,
                    AVG(p.price) as avg_price
                FROM restaurants r
                JOIN products p ON p.restaurant_id = r.id
                GROUP BY r.id, r.name, r.category, r.rating, r.city
                ORDER BY product_count DESC
                LIMIT 20
            """
            
            results = self.safe_execute_query(query)
            
            if results:
                table_data = []
                for i, rest in enumerate(results, 1):
                    table_data.append([
                        i,
                        rest['name'][:25],
                        rest['category'][:20] if rest['category'] else 'N/A',
                        rest['rating'] or 'N/A',
                        rest['city'][:15] if rest['city'] else 'N/A',
                        rest['product_count'],
                        self.format_currency(rest['avg_price']) if rest['avg_price'] else 'N/A'
                    ])
                
                headers = ['Pos', 'Restaurante', 'Categoria', 'Nota', 'Cidade', 'Produtos', 'Preço Médio']
                self.format_table(table_data, headers)
            
        except Exception as e:
            self.show_error(f"Erro no relatório de produtos: {e}")
    
    def _rating_comparison(self):
        """Rating comparison analysis"""
        self.print_subsection_header("⭐ COMPARAÇÃO: SEM AVALIAÇÃO VS BEM AVALIADOS")
        
        try:
            # Restaurants without rating
            no_rating = self.safe_execute_query("""
                SELECT COUNT(*) as count, AVG(COUNT(p.id)) as avg_products
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
                WHERE r.rating IS NULL OR r.rating = 0
                GROUP BY r.id
            """, fetch_one=True)
            
            # Well rated restaurants
            well_rated = self.safe_execute_query("""
                SELECT COUNT(*) as count, AVG(COUNT(p.id)) as avg_products
                FROM restaurants r
                LEFT JOIN products p ON p.restaurant_id = r.id
                WHERE r.rating >= 4.0
                GROUP BY r.id
            """, fetch_one=True)
            
            comparison_data = []
            if no_rating:
                comparison_data.append(['Sem avaliação', no_rating['count'], f"{no_rating['avg_products']:.1f}" if no_rating['avg_products'] else '0'])
            
            if well_rated:
                comparison_data.append(['Bem avaliados (≥4.0)', well_rated['count'], f"{well_rated['avg_products']:.1f}" if well_rated['avg_products'] else '0'])
            
            if comparison_data:
                headers = ['Categoria', 'Restaurantes', 'Produtos Médios']
                self.format_table(comparison_data, headers)
            
        except Exception as e:
            self.show_error(f"Erro na comparação de avaliações: {e}")
    
    def get_custom_report_statistics(self) -> Dict[str, Any]:
        """Get custom report statistics"""
        stats = self.get_base_statistics()
        
        # Add custom report capabilities info
        stats['custom_report_capabilities'] = {
            'available_filters': [
                'city', 'category', 'min_rating', 'max_price', 
                'delivery_time', 'restaurant_name', 'has_products', 'min_products'
            ],
            'predefined_reports': [
                'best_by_city', 'cheap_food', 'fast_delivery', 'pizza_analysis',
                'category_comparison', 'most_products', 'rating_comparison'
            ],
            'export_formats': ['csv', 'json']
        }
        
        return stats