#!/usr/bin/env python3
"""
Windows Database Manager - Operações de banco de dados para scraping paralelo
"""

import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.database.database_adapter import get_database_manager
from src.config.database import execute_query
from src.utils.logger import setup_logger


class WindowsDatabaseManager:
    """Gerenciador de operações de banco de dados para Windows"""
    
    def __init__(self):
        self.logger = setup_logger("WindowsDatabaseManager")
        self.db = get_database_manager()
    
    def _load_existing_restaurants_mysql(self) -> List[Dict[str, Any]]:
        """Carrega restaurantes existentes do MySQL"""
        try:
            query = """
                SELECT id, name, category, rating, delivery_fee, delivery_time, 
                       address, tags, is_open, image_url, created_at 
                FROM restaurants 
                WHERE is_active = TRUE
            """
            
            result = execute_query(query, fetch_all=True)
            
            if result:
                self.logger.info(f"Carregados {len(result)} restaurantes existentes do MySQL")
                return result
            else:
                self.logger.warning("Nenhum restaurante encontrado no MySQL")
                return []
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar restaurantes do MySQL: {e}")
            return []
    
    def _load_existing_products_mysql(self) -> List[Dict[str, Any]]:
        """Carrega produtos existentes do MySQL"""
        try:
            query = """
                SELECT p.id, p.name, p.description, p.price, p.original_price, 
                       p.category, p.restaurant_id, p.image_url, p.is_available, 
                       p.created_at, r.name as restaurant_name
                FROM products p
                JOIN restaurants r ON p.restaurant_id = r.id
                WHERE p.is_active = TRUE AND r.is_active = TRUE
            """
            
            result = execute_query(query, fetch_all=True)
            
            if result:
                self.logger.info(f"Carregados {len(result)} produtos existentes do MySQL")
                return result
            else:
                self.logger.warning("Nenhum produto encontrado no MySQL")
                return []
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar produtos do MySQL: {e}")
            return []
    
    def _save_restaurants_to_mysql(self, restaurants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Salva restaurantes no MySQL e retorna estatísticas"""
        if not restaurants:
            return {'inserted': 0, 'updated': 0, 'errors': 0}
        
        inserted = 0
        updated = 0
        errors = 0
        
        try:
            for restaurant in restaurants:
                try:
                    # Verificar se restaurante já existe
                    check_query = """
                        SELECT id FROM restaurants 
                        WHERE name = %s AND category = %s AND is_active = TRUE
                    """
                    
                    existing = execute_query(
                        check_query, 
                        params=(restaurant['name'], restaurant['category']),
                        fetch_one=True
                    )
                    
                    if existing:
                        # Atualizar restaurante existente
                        update_query = """
                            UPDATE restaurants 
                            SET rating = %s, delivery_fee = %s, delivery_time = %s, 
                                address = %s, tags = %s, is_open = %s, image_url = %s,
                                updated_at = NOW()
                            WHERE id = %s
                        """
                        
                        execute_query(
                            update_query,
                            params=(
                                restaurant['rating'],
                                restaurant['delivery_fee'],
                                restaurant['delivery_time'],
                                restaurant['address'],
                                ','.join(restaurant['tags']) if restaurant['tags'] else '',
                                restaurant['is_open'],
                                restaurant['image_url'],
                                existing['id']
                            )
                        )
                        
                        updated += 1
                        
                    else:
                        # Inserir novo restaurante
                        insert_query = """
                            INSERT INTO restaurants 
                            (name, category, rating, delivery_fee, delivery_time, 
                             address, tags, is_open, image_url, is_active, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())
                        """
                        
                        execute_query(
                            insert_query,
                            params=(
                                restaurant['name'],
                                restaurant['category'],
                                restaurant['rating'],
                                restaurant['delivery_fee'],
                                restaurant['delivery_time'],
                                restaurant['address'],
                                ','.join(restaurant['tags']) if restaurant['tags'] else '',
                                restaurant['is_open'],
                                restaurant['image_url']
                            )
                        )
                        
                        inserted += 1
                        
                except Exception as e:
                    self.logger.error(f"Erro ao salvar restaurante {restaurant.get('name', 'N/A')}: {e}")
                    errors += 1
            
            self.logger.info(f"Restaurantes salvos: {inserted} inseridos, {updated} atualizados, {errors} erros")
            
        except Exception as e:
            self.logger.error(f"Erro geral ao salvar restaurantes: {e}")
            errors += len(restaurants)
        
        return {
            'inserted': inserted,
            'updated': updated,
            'errors': errors,
            'total_processed': len(restaurants)
        }
    
    def _format_products_for_database(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formata produtos para inserção no banco de dados"""
        formatted_products = []
        
        for product in products:
            try:
                # Verificar se o produto tem os campos necessários
                if not all(key in product for key in ['name', 'restaurant_id', 'category']):
                    self.logger.warning(f"Produto inválido ignorado: {product}")
                    continue
                
                formatted_product = {
                    'name': str(product['name']).strip(),
                    'description': str(product.get('description', '')).strip(),
                    'price': float(product.get('price', 0.0)),
                    'original_price': float(product.get('original_price', product.get('price', 0.0))),
                    'category': str(product['category']).strip(),
                    'restaurant_id': int(product['restaurant_id']),
                    'image_url': str(product.get('image_url', '')).strip(),
                    'is_available': bool(product.get('is_available', True)),
                    'nutritional_info': str(product.get('nutritional_info', '')).strip(),
                    'allergens': str(product.get('allergens', '')).strip(),
                    'tags': ','.join(product.get('tags', [])) if product.get('tags') else '',
                    'preparation_time': str(product.get('preparation_time', '')).strip(),
                    'portion_size': str(product.get('portion_size', '')).strip()
                }
                
                # Validar preços
                if formatted_product['price'] < 0:
                    formatted_product['price'] = 0.0
                
                if formatted_product['original_price'] < formatted_product['price']:
                    formatted_product['original_price'] = formatted_product['price']
                
                formatted_products.append(formatted_product)
                
            except Exception as e:
                self.logger.error(f"Erro ao formatar produto: {e}")
                continue
        
        return formatted_products
    
    def save_results(self, restaurants: List[Dict[str, Any]], products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Salva resultados completos no banco de dados"""
        results = {
            'restaurants': {'inserted': 0, 'updated': 0, 'errors': 0},
            'products': {'inserted': 0, 'updated': 0, 'errors': 0},
            'total_time': 0,
            'success': False
        }
        
        start_time = datetime.now()
        
        try:
            # Salvar restaurantes primeiro
            if restaurants:
                self.logger.info(f"Salvando {len(restaurants)} restaurantes...")
                results['restaurants'] = self._save_restaurants_to_mysql(restaurants)
            
            # Salvar produtos
            if products:
                self.logger.info(f"Salvando {len(products)} produtos...")
                results['products'] = self._save_products_to_mysql(products)
            
            # Calcular tempo total
            end_time = datetime.now()
            results['total_time'] = (end_time - start_time).total_seconds()
            
            # Determinar sucesso
            total_errors = results['restaurants']['errors'] + results['products']['errors']
            total_processed = len(restaurants) + len(products)
            
            results['success'] = total_errors == 0 or (total_errors / total_processed) < 0.1  # Menos de 10% de erros
            
            self.logger.info(f"Salvamento concluído em {results['total_time']:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados: {e}")
            results['success'] = False
        
        return results
    
    def _save_products_to_mysql(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Salva produtos no MySQL"""
        if not products:
            return {'inserted': 0, 'updated': 0, 'errors': 0}
        
        # Formatar produtos
        formatted_products = self._format_products_for_database(products)
        
        inserted = 0
        updated = 0
        errors = 0
        
        try:
            for product in formatted_products:
                try:
                    # Verificar se produto já existe
                    check_query = """
                        SELECT id FROM products 
                        WHERE name = %s AND restaurant_id = %s AND is_active = TRUE
                    """
                    
                    existing = execute_query(
                        check_query,
                        params=(product['name'], product['restaurant_id']),
                        fetch_one=True
                    )
                    
                    if existing:
                        # Atualizar produto existente
                        update_query = """
                            UPDATE products 
                            SET description = %s, price = %s, original_price = %s, 
                                category = %s, image_url = %s, is_available = %s,
                                nutritional_info = %s, allergens = %s, tags = %s,
                                preparation_time = %s, portion_size = %s, updated_at = NOW()
                            WHERE id = %s
                        """
                        
                        execute_query(
                            update_query,
                            params=(
                                product['description'],
                                product['price'],
                                product['original_price'],
                                product['category'],
                                product['image_url'],
                                product['is_available'],
                                product['nutritional_info'],
                                product['allergens'],
                                product['tags'],
                                product['preparation_time'],
                                product['portion_size'],
                                existing['id']
                            )
                        )
                        
                        updated += 1
                        
                    else:
                        # Inserir novo produto
                        insert_query = """
                            INSERT INTO products 
                            (name, description, price, original_price, category, restaurant_id,
                             image_url, is_available, nutritional_info, allergens, tags,
                             preparation_time, portion_size, is_active, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())
                        """
                        
                        execute_query(
                            insert_query,
                            params=(
                                product['name'],
                                product['description'],
                                product['price'],
                                product['original_price'],
                                product['category'],
                                product['restaurant_id'],
                                product['image_url'],
                                product['is_available'],
                                product['nutritional_info'],
                                product['allergens'],
                                product['tags'],
                                product['preparation_time'],
                                product['portion_size']
                            )
                        )
                        
                        inserted += 1
                        
                except Exception as e:
                    self.logger.error(f"Erro ao salvar produto {product.get('name', 'N/A')}: {e}")
                    errors += 1
            
            self.logger.info(f"Produtos salvos: {inserted} inseridos, {updated} atualizados, {errors} erros")
            
        except Exception as e:
            self.logger.error(f"Erro geral ao salvar produtos: {e}")
            errors += len(formatted_products)
        
        return {
            'inserted': inserted,
            'updated': updated,
            'errors': errors,
            'total_processed': len(formatted_products)
        }
    
    def get_restaurant_id_by_name(self, restaurant_name: str, category: str) -> Optional[int]:
        """Obtém ID do restaurante pelo nome e categoria"""
        try:
            query = """
                SELECT id FROM restaurants 
                WHERE name = %s AND category = %s AND is_active = TRUE
                LIMIT 1
            """
            
            result = execute_query(
                query,
                params=(restaurant_name, category),
                fetch_one=True
            )
            
            return result['id'] if result else None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter ID do restaurante {restaurant_name}: {e}")
            return None
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """Remove dados antigos do banco (opcional)"""
        try:
            # Marcar restaurantes antigos como inativos
            restaurant_query = """
                UPDATE restaurants 
                SET is_active = FALSE 
                WHERE updated_at < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            restaurant_result = execute_query(restaurant_query, params=(days_old,))
            
            # Marcar produtos de restaurantes inativos como inativos
            product_query = """
                UPDATE products p
                JOIN restaurants r ON p.restaurant_id = r.id
                SET p.is_active = FALSE
                WHERE r.is_active = FALSE
            """
            
            product_result = execute_query(product_query)
            
            self.logger.info(f"Limpeza concluída: dados mais antigos que {days_old} dias marcados como inativos")
            
            return {
                'restaurants_deactivated': restaurant_result if restaurant_result else 0,
                'products_deactivated': product_result if product_result else 0
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de dados antigos: {e}")
            return {'restaurants_deactivated': 0, 'products_deactivated': 0}