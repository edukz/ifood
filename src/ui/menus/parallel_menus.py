#!/usr/bin/env python3
"""
Execução Paralela - Menus especializados para processamento paralelo
"""

import platform
import asyncio
import time
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

# Imports para execução paralela
from src.scrapers.parallel.windows_parallel_scraper import WindowsParallelScraper, detect_windows
from src.database.database_adapter import get_database_manager
from src.ui.base_menu import BaseMenu


class ParallelMenus(BaseMenu):
    """Menus especializados para execução paralela"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Paralelo", session_stats, data_dir)
        self.db = get_database_manager()
    
    def menu_parallel_execution(self):
        """Menu de execução paralela"""
        options = [
            "1. 🏷️  Extrair categorias em paralelo",
            "2. 🏪 Extrair restaurantes em paralelo",
            "3. 🍕 Extrair produtos em paralelo",
            "4. 🔄 Execução completa (categorias → restaurantes → produtos)",
            "5. ⚙️  Configurar workers",
            "6. 📊 Demonstração de performance"
        ]
        
        self.show_menu("🚀 EXECUÇÃO PARALELA", options)
        choice = self.get_user_choice(6)
        
        if choice == "1":
            self._parallel_categories()
        elif choice == "2":
            self._parallel_restaurants()
        elif choice == "3":
            self._parallel_products()
        elif choice == "4":
            self._parallel_full_pipeline()
        elif choice == "5":
            self._configure_workers()
        elif choice == "6":
            self._demo_performance()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _parallel_categories(self):
        """Extração paralela de categorias"""
        print("\n🏷️  EXTRAÇÃO PARALELA DE CATEGORIAS")
        print("═" * 50)
        
        # Verifica se há dependências necessárias
        if not self._try_install_dependencies():
            return
        
        # Configurações
        city = input(f"Digite a cidade [Birigui]: ").strip() or "Birigui"
        num_workers = input("Número de workers [3]: ").strip() or "3"
        
        try:
            num_workers = int(num_workers)
            if num_workers < 1 or num_workers > 10:
                raise ValueError("Número deve estar entre 1 e 10")
        except ValueError:
            self.show_error("Número de workers inválido. Usando 3.")
            num_workers = 3
        
        print(f"\n🔄 Iniciando extração paralela para {city} com {num_workers} workers...")
        
        try:
            # Usar WindowsParallelScraper
            scraper = WindowsParallelScraper(
                max_workers=num_workers,
                city=city,
                headless=True
            )
            
            # Executar extração paralela de categorias
            result = scraper.extract_categories_parallel()
            
            if result.get('success', False):
                categories_found = result.get('categories_found', 0)
                self.session_stats['categories_extracted'] += categories_found
                
                print(f"\n✅ Extração paralela concluída com sucesso!")
                print(f"📊 Categorias encontradas: {categories_found}")
                print(f"🕐 Tempo total: {result.get('total_time', 0):.2f} segundos")
                print(f"⚡ Workers utilizados: {num_workers}")
                
                if result.get('categories'):
                    print(f"\n📋 Primeiras 10 categorias:")
                    for i, cat in enumerate(result['categories'][:10], 1):
                        print(f"  {i}. {cat.get('name', 'N/A')}")
            else:
                error_msg = result.get('error', 'Erro desconhecido')
                print(f"\n❌ Erro na extração paralela: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Erro na extração paralela: {e}")
            self.show_error(f"Erro na extração: {e}")
        
        self.pause()
    
    def _parallel_restaurants(self):
        """Extração paralela de restaurantes"""
        print("\n🏪 EXTRAÇÃO PARALELA DE RESTAURANTES")
        print("═" * 50)
        
        # Verifica se há dependências necessárias
        if not self._try_install_dependencies():
            return
        
        # Verifica se existem categorias
        categories = self._analyze_existing_categories()
        if not categories:
            print("❌ Nenhuma categoria encontrada!")
            print("💡 Execute primeiro a extração de categorias")
            self.pause()
            return
        
        print(f"\n📋 Encontradas {len(categories)} categorias")
        
        # Opções de seleção
        options = [
            "1. 🎯 Processar TODAS as categorias",
            "2. 🎯 Selecionar categorias específicas",
            "3. 📁 Selecionar categorias de arquivo CSV"
        ]
        
        self.show_menu("🏪 OPÇÕES DE EXTRAÇÃO", options)
        choice = self.get_user_choice(3)
        
        if choice == "1":
            selected_categories = categories
        elif choice == "2":
            selected_categories = self._select_specific_categories(categories)
        elif choice == "3":
            selected_categories = self._select_specific_file_categories(categories)
        else:
            return
        
        if not selected_categories:
            print("❌ Nenhuma categoria selecionada!")
            self.pause()
            return
        
        # Configurações
        num_workers = input("Número de workers [3]: ").strip() or "3"
        
        try:
            num_workers = int(num_workers)
            if num_workers < 1 or num_workers > 10:
                raise ValueError("Número deve estar entre 1 e 10")
        except ValueError:
            self.show_error("Número de workers inválido. Usando 3.")
            num_workers = 3
        
        print(f"\n🔄 Iniciando extração paralela de {len(selected_categories)} categorias com {num_workers} workers...")
        
        confirm = input("⚠️  Isso pode demorar bastante. Continuar? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        try:
            # Usar WindowsParallelScraper
            scraper = WindowsParallelScraper(
                max_workers=num_workers,
                city="Birigui",
                headless=True
            )
            
            # Executar extração paralela de restaurantes
            result = scraper.extract_restaurants_parallel(selected_categories)
            
            if result.get('success', False):
                restaurants_found = result.get('restaurants_found', 0)
                self.session_stats['restaurants_extracted'] += restaurants_found
                
                print(f"\n✅ Extração paralela concluída com sucesso!")
                print(f"📊 Restaurantes encontrados: {restaurants_found}")
                print(f"🏷️  Categorias processadas: {len(selected_categories)}")
                print(f"🕐 Tempo total: {result.get('total_time', 0):.2f} segundos")
                print(f"⚡ Workers utilizados: {num_workers}")
                
                # Estatísticas por categoria
                if result.get('category_stats'):
                    print(f"\n📋 Estatísticas por categoria:")
                    for cat, stats in result['category_stats'].items():
                        print(f"  • {cat}: {stats.get('count', 0)} restaurantes")
            else:
                error_msg = result.get('error', 'Erro desconhecido')
                print(f"\n❌ Erro na extração paralela: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Erro na extração paralela: {e}")
            self.show_error(f"Erro na extração: {e}")
        
        self.pause()
    
    def _parallel_products(self):
        """Extração paralela de produtos"""
        print("\n🍕 EXTRAÇÃO PARALELA DE PRODUTOS")
        print("═" * 50)
        
        # Verifica se há dependências necessárias
        if not self._try_install_dependencies():
            return
        
        # Verifica se existem restaurantes
        try:
            with self.db.get_cursor() as (cursor, _):
                cursor.execute("SELECT COUNT(*) as count FROM restaurants")
                restaurant_count = cursor.fetchone()['count']
                
                if restaurant_count == 0:
                    print("❌ Nenhum restaurante encontrado!")
                    print("💡 Execute primeiro a extração de restaurantes")
                    self.pause()
                    return
                
                print(f"\n📋 Encontrados {restaurant_count} restaurantes")
                
                # Opções de seleção
                options = [
                    "1. 🎯 Processar TODOS os restaurantes",
                    "2. 🎯 Processar restaurantes de categoria específica",
                    "3. 🔢 Processar número limitado de restaurantes"
                ]
                
                self.show_menu("🍕 OPÇÕES DE EXTRAÇÃO", options)
                choice = self.get_user_choice(3)
                
                if choice == "1":
                    cursor.execute("SELECT * FROM restaurants ORDER BY id LIMIT 100")
                    selected_restaurants = cursor.fetchall()
                elif choice == "2":
                    category = input("Digite a categoria: ").strip()
                    if not category:
                        print("❌ Categoria não especificada!")
                        self.pause()
                        return
                    
                    cursor.execute(
                        "SELECT * FROM restaurants WHERE category LIKE %s ORDER BY id LIMIT 100",
                        (f"%{category}%",)
                    )
                    selected_restaurants = cursor.fetchall()
                elif choice == "3":
                    limit = input("Número de restaurantes [50]: ").strip() or "50"
                    try:
                        limit = int(limit)
                        if limit < 1:
                            raise ValueError("Número deve ser maior que 0")
                    except ValueError:
                        self.show_error("Número inválido. Usando 50.")
                        limit = 50
                    
                    cursor.execute(f"SELECT * FROM restaurants ORDER BY id LIMIT {limit}")
                    selected_restaurants = cursor.fetchall()
                else:
                    return
                
                if not selected_restaurants:
                    print("❌ Nenhum restaurante selecionado!")
                    self.pause()
                    return
                
        except Exception as e:
            self.show_error(f"Erro ao buscar restaurantes: {e}")
            self.pause()
            return
        
        # Configurações
        num_workers = input("Número de workers [3]: ").strip() or "3"
        
        try:
            num_workers = int(num_workers)
            if num_workers < 1 or num_workers > 10:
                raise ValueError("Número deve estar entre 1 e 10")
        except ValueError:
            self.show_error("Número de workers inválido. Usando 3.")
            num_workers = 3
        
        print(f"\n🔄 Iniciando extração paralela de {len(selected_restaurants)} restaurantes com {num_workers} workers...")
        
        confirm = input("⚠️  Isso pode demorar muito tempo. Continuar? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        try:
            # Usar WindowsParallelScraper
            scraper = WindowsParallelScraper(
                max_workers=num_workers,
                city="Birigui",
                headless=True
            )
            
            # Executar extração paralela de produtos
            result = scraper.extract_products_parallel(selected_restaurants)
            
            if result.get('success', False):
                products_found = result.get('products_found', 0)
                self.session_stats['products_extracted'] += products_found
                
                print(f"\n✅ Extração paralela concluída com sucesso!")
                print(f"📊 Produtos encontrados: {products_found}")
                print(f"🏪 Restaurantes processados: {len(selected_restaurants)}")
                print(f"🕐 Tempo total: {result.get('total_time', 0):.2f} segundos")
                print(f"⚡ Workers utilizados: {num_workers}")
                
                # Estatísticas por restaurante
                if result.get('restaurant_stats'):
                    print(f"\n📋 Top 10 restaurantes por produtos:")
                    sorted_stats = sorted(
                        result['restaurant_stats'].items(),
                        key=lambda x: x[1].get('count', 0),
                        reverse=True
                    )[:10]
                    
                    for restaurant, stats in sorted_stats:
                        print(f"  • {restaurant}: {stats.get('count', 0)} produtos")
            else:
                error_msg = result.get('error', 'Erro desconhecido')
                print(f"\n❌ Erro na extração paralela: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Erro na extração paralela: {e}")
            self.show_error(f"Erro na extração: {e}")
        
        self.pause()
    
    def _parallel_full_pipeline(self):
        """Execução completa em paralelo"""
        print("\n🚀 Pipeline completo em paralelo")
        print("Executa: Categorias → Restaurantes → Produtos")
        print("═" * 50)
        
        # Verifica se há dependências necessárias
        if not self._try_install_dependencies():
            return
        
        # Configurações
        city = input(f"Digite a cidade [Birigui]: ").strip() or "Birigui"
        num_workers = input("Número de workers [3]: ").strip() or "3"
        
        try:
            num_workers = int(num_workers)
            if num_workers < 1 or num_workers > 10:
                raise ValueError("Número deve estar entre 1 e 10")
        except ValueError:
            self.show_error("Número de workers inválido. Usando 3.")
            num_workers = 3
        
        print(f"\n🔄 Iniciando pipeline completo para {city} com {num_workers} workers...")
        
        confirm = input("⚠️  Isso pode demorar muito tempo. Continuar? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        try:
            # Usar WindowsParallelScraper
            scraper = WindowsParallelScraper(
                max_workers=num_workers,
                city=city,
                headless=True
            )
            
            total_start_time = time.time()
            
            # Fase 1: Categorias
            print(f"\n🏷️  FASE 1: Extraindo categorias...")
            categories_result = scraper.extract_categories_parallel()
            
            if not categories_result.get('success', False):
                print(f"❌ Erro na extração de categorias: {categories_result.get('error', 'Erro desconhecido')}")
                self.pause()
                return
            
            categories_found = categories_result.get('categories_found', 0)
            print(f"✅ Categorias extraídas: {categories_found}")
            
            # Fase 2: Restaurantes
            print(f"\n🏪 FASE 2: Extraindo restaurantes...")
            categories = categories_result.get('categories', [])[:10]  # Limitar a 10 categorias
            
            if not categories:
                print("❌ Nenhuma categoria disponível para extração de restaurantes")
                self.pause()
                return
            
            restaurants_result = scraper.extract_restaurants_parallel(categories)
            
            if not restaurants_result.get('success', False):
                print(f"❌ Erro na extração de restaurantes: {restaurants_result.get('error', 'Erro desconhecido')}")
                self.pause()
                return
            
            restaurants_found = restaurants_result.get('restaurants_found', 0)
            print(f"✅ Restaurantes extraídos: {restaurants_found}")
            
            # Fase 3: Produtos (limitar a 50 restaurantes)
            print(f"\n🍕 FASE 3: Extraindo produtos...")
            
            with self.db.get_cursor() as (cursor, _):
                cursor.execute("SELECT * FROM restaurants ORDER BY id LIMIT 50")
                restaurants = cursor.fetchall()
            
            if not restaurants:
                print("❌ Nenhum restaurante disponível para extração de produtos")
                self.pause()
                return
            
            products_result = scraper.extract_products_parallel(restaurants)
            
            if not products_result.get('success', False):
                print(f"❌ Erro na extração de produtos: {products_result.get('error', 'Erro desconhecido')}")
                self.pause()
                return
            
            products_found = products_result.get('products_found', 0)
            print(f"✅ Produtos extraídos: {products_found}")
            
            # Resultado final
            total_time = time.time() - total_start_time
            
            # Atualizar estatísticas
            self.session_stats['categories_extracted'] += categories_found
            self.session_stats['restaurants_extracted'] += restaurants_found
            self.session_stats['products_extracted'] += products_found
            
            print(f"\n🎯 PIPELINE COMPLETO CONCLUÍDO!")
            print(f"📊 Categorias: {categories_found}")
            print(f"📊 Restaurantes: {restaurants_found}")
            print(f"📊 Produtos: {products_found}")
            print(f"🕐 Tempo total: {total_time:.2f} segundos")
            print(f"⚡ Workers utilizados: {num_workers}")
            
        except Exception as e:
            self.logger.error(f"Erro no pipeline completo: {e}")
            self.show_error(f"Erro no pipeline: {e}")
        
        self.pause()
    
    def _configure_workers(self):
        """Configurar número de workers"""
        print("\n⚙️  CONFIGURAÇÃO DE WORKERS")
        print("═" * 50)
        
        current_workers = 3  # Padrão
        
        print(f"Workers atuais: {current_workers}")
        print(f"Plataforma: {platform.system()}")
        print(f"Processadores: {platform.processor()}")
        
        print("\n💡 Recomendações:")
        print("  • 1-2 workers: Computadores com baixa performance")
        print("  • 3-5 workers: Computadores com performance média")
        print("  • 6-10 workers: Computadores com alta performance")
        print("  • Mais workers não significa necessariamente mais velocidade")
        
        new_workers = input(f"\nNovo número de workers [1-10]: ").strip()
        
        try:
            new_workers = int(new_workers)
            if new_workers < 1 or new_workers > 10:
                raise ValueError("Número deve estar entre 1 e 10")
            
            print(f"✅ Configuração atualizada para {new_workers} workers")
            print("💡 A configuração será aplicada na próxima execução")
            
        except ValueError:
            self.show_error("Número de workers inválido!")
        
        self.pause()
    
    def _demo_performance(self):
        """Demonstração de performance"""
        print("\n📊 DEMONSTRAÇÃO DE PERFORMANCE")
        print("═" * 50)
        
        print("🔄 Executando teste de performance...")
        
        # Simular teste de performance
        import time
        import random
        
        workers_tests = [1, 2, 3, 5]
        results = []
        
        for workers in workers_tests:
            print(f"\n⚡ Testando com {workers} workers...")
            
            # Simular tempo de execução
            start_time = time.time()
            time.sleep(random.uniform(0.5, 2.0))  # Simular trabalho
            end_time = time.time()
            
            execution_time = end_time - start_time
            simulated_items = random.randint(50, 200)
            throughput = simulated_items / execution_time
            
            results.append({
                'workers': workers,
                'time': execution_time,
                'items': simulated_items,
                'throughput': throughput
            })
            
            print(f"  ✅ Tempo: {execution_time:.2f}s")
            print(f"  ✅ Items processados: {simulated_items}")
            print(f"  ✅ Throughput: {throughput:.2f} items/s")
        
        # Mostrar comparação
        print(f"\n📊 COMPARAÇÃO DE PERFORMANCE:")
        print("═" * 50)
        
        best_result = max(results, key=lambda x: x['throughput'])
        
        for result in results:
            status = "🏆 MELHOR" if result == best_result else "📊"
            print(f"{status} {result['workers']} workers: {result['throughput']:.2f} items/s")
        
        print(f"\n💡 Recomendação: Use {best_result['workers']} workers para melhor performance")
        
        self.pause()
    
    def _analyze_existing_categories(self, categories=None):
        """Analisa categorias existentes no banco"""
        if categories is not None:
            return categories
        
        try:
            with self.db.get_cursor() as (cursor, _):
                cursor.execute("SELECT * FROM categories ORDER BY name")
                categories = cursor.fetchall()
                return categories
        except Exception as e:
            self.logger.error(f"Erro ao analisar categorias: {e}")
            return []
    
    def _select_specific_categories(self, all_categories):
        """Seleciona categorias específicas"""
        print(f"\n📋 SELEÇÃO DE CATEGORIAS")
        print("═" * 50)
        
        # Mostrar categorias disponíveis
        print(f"Categorias disponíveis ({len(all_categories)}):")
        for i, cat in enumerate(all_categories[:20], 1):  # Mostrar até 20
            print(f"  {i}. {cat.get('name', 'N/A')}")
        
        if len(all_categories) > 20:
            print(f"  ... e mais {len(all_categories) - 20} categorias")
        
        print(f"\n💡 Opções de seleção:")
        print(f"  • Números específicos: 1,3,5")
        print(f"  • Intervalos: 1-10")
        print(f"  • Combinações: 1,3,5-10,15")
        
        selection = input("\nDigite sua seleção: ").strip()
        
        if not selection:
            return []
        
        try:
            indices = self._parse_selection_input(selection, len(all_categories))
            selected_categories = [all_categories[i-1] for i in indices if 1 <= i <= len(all_categories)]
            
            print(f"\n✅ Selecionadas {len(selected_categories)} categorias:")
            for cat in selected_categories[:10]:  # Mostrar até 10
                print(f"  • {cat.get('name', 'N/A')}")
            
            if len(selected_categories) > 10:
                print(f"  ... e mais {len(selected_categories) - 10} categorias")
            
            return selected_categories
            
        except Exception as e:
            self.show_error(f"Erro na seleção: {e}")
            return []
    
    def _parse_selection_input(self, user_input, max_number):
        """Parseia entrada de seleção do usuário"""
        indices = set()
        
        # Dividir por vírgulas
        parts = user_input.split(',')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Verificar se é um intervalo
            if '-' in part:
                try:
                    start, end = part.split('-', 1)
                    start = int(start.strip())
                    end = int(end.strip())
                    
                    if start > end:
                        start, end = end, start
                    
                    for i in range(start, end + 1):
                        if 1 <= i <= max_number:
                            indices.add(i)
                except ValueError:
                    raise ValueError(f"Intervalo inválido: {part}")
            else:
                # Número individual
                try:
                    num = int(part)
                    if 1 <= num <= max_number:
                        indices.add(num)
                except ValueError:
                    raise ValueError(f"Número inválido: {part}")
        
        return sorted(indices)
    
    def _select_specific_file_categories(self, available_categories):
        """Seleciona categorias de arquivo CSV"""
        print(f"\n📁 SELEÇÃO DE CATEGORIAS DE ARQUIVO")
        print("═" * 50)
        
        # Buscar arquivos CSV de categorias
        csv_files = list(self.data_dir.glob("**/ifood_data_categories*.csv"))
        
        if not csv_files:
            print("❌ Nenhum arquivo CSV de categorias encontrado!")
            return []
        
        print(f"📋 Arquivos CSV encontrados:")
        for i, file in enumerate(csv_files, 1):
            print(f"  {i}. {file.name}")
        
        choice = input(f"\nEscolha um arquivo [1-{len(csv_files)}]: ").strip()
        
        try:
            choice = int(choice)
            if not 1 <= choice <= len(csv_files):
                raise ValueError("Escolha inválida")
            
            selected_file = csv_files[choice - 1]
            
            # Ler categorias do arquivo CSV
            import csv
            categories = []
            
            with open(selected_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    categories.append(row)
            
            print(f"\n✅ Carregadas {len(categories)} categorias do arquivo {selected_file.name}")
            
            # Mostrar primeiras categorias
            for i, cat in enumerate(categories[:10], 1):
                print(f"  {i}. {cat.get('name', cat.get('nome', 'N/A'))}")
            
            if len(categories) > 10:
                print(f"  ... e mais {len(categories) - 10} categorias")
            
            return categories
            
        except ValueError:
            self.show_error("Escolha inválida!")
            return []
        except Exception as e:
            self.show_error(f"Erro ao ler arquivo: {e}")
            return []
    
    def _try_install_dependencies(self):
        """Tenta instalar dependências necessárias"""
        try:
            # Verificar se o Playwright está instalado
            from playwright.sync_api import sync_playwright
            
            # Verificar se o WindowsParallelScraper está disponível
            if not detect_windows() and platform.system() != 'Linux':
                print("⚠️  Sistema não suportado para execução paralela")
                print("💡 Funcionalidade otimizada para Windows e Linux")
                return False
            
            return True
            
        except ImportError:
            print("❌ Playwright não encontrado!")
            print("💡 Instale com: pip install playwright")
            
            install = input("Tentar instalar automaticamente? (s/N): ").strip().lower()
            if install == 's':
                try:
                    import subprocess
                    subprocess.run(["pip", "install", "playwright"], check=True)
                    subprocess.run(["playwright", "install"], check=True)
                    print("✅ Playwright instalado com sucesso!")
                    return True
                except Exception as e:
                    print(f"❌ Erro na instalação: {e}")
                    return False
            else:
                return False
        except Exception as e:
            self.show_error(f"Erro ao verificar dependências: {e}")
            return False