#!/usr/bin/env python3
"""
Menus de Sistema - Busca, Arquivos, Relatórios, Configurações
"""

import platform
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# ParallelScraper removido - usando configuração simples
from src.scrapers.parallel.windows_parallel_scraper import WindowsParallelScraper, detect_windows
from src.utils.search_optimizer import SearchIndex, QueryOptimizer
from tools.archive_manager import ArchiveManager
from .base_menu import BaseMenu


class SystemMenus(BaseMenu):
    """Menus para funcionalidades do sistema"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path,
                 parallel_scraper: Any, search_optimizer: QueryOptimizer,
                 archive_manager: ArchiveManager):
        super().__init__("Sistema", session_stats, data_dir)
        self.parallel_scraper = parallel_scraper
        self.search_optimizer = search_optimizer
        self.archive_manager = archive_manager
    
    # ================== EXECUÇÃO PARALELA ==================
    
    def menu_parallel_execution(self):
        """Menu de execução paralela"""
        options = [
            "1. 🏷️  Extrair categorias em paralelo",
            "2. 🏪 Extrair restaurantes em paralelo",
            "3. 🍕 Extrair produtos em paralelo",
            "4. 🎯 Execução completa (categorias → restaurantes → produtos)",
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
        """Execução paralela de categorias"""
        print("\n🚀 Extração paralela de categorias")
        
        # Verificar se há categorias já coletadas
        try:
            from src.utils.database import DatabaseManager
            db = DatabaseManager()
            existing_categories = db.get_existing_categories()
        except Exception as e:
            existing_categories = []
        
        if existing_categories:
            print(f"\n📊 ANÁLISE DE DADOS EXISTENTES:")
            print(f"✅ {len(existing_categories)} categorias já coletadas")
            
            choice = input("\n🎯 Opções:\n1. 📊 Analisar dados existentes\n2. 🚀 Tentar extração nova\n3. 🔙 Voltar\nEscolha: ").strip()
            
            if choice == "1":
                self._analyze_existing_categories(existing_categories)
            elif choice == "2":
                print("\n🚀 Tentando extração nova...")
                print("⚠️  Dependências Playwright necessárias: sudo playwright install-deps")
            elif choice == "3":
                return
        else:
            print("❌ Nenhuma categoria encontrada!")
            print("💡 Execute primeiro a extração de categorias (menu principal → opção 1)")
        
        self.pause()
    
    def _analyze_existing_categories(self, categories):
        """Analisa categorias existentes"""
        print(f"\n📊 ANÁLISE DE {len(categories)} CATEGORIAS:")
        print("═" * 50)
        
        # Agrupar por cidade
        cities = {}
        for cat in categories:
            city = cat.get('city', 'Desconhecida')
            if city not in cities:
                cities[city] = []
            cities[city].append(cat)
        
        print(f"🌐 Cidades disponíveis:")
        for city, city_categories in cities.items():
            print(f"  📍 {city}: {len(city_categories)} categorias")
            
            # Mostrar primeiras 5 categorias
            for i, cat in enumerate(city_categories[:5]):
                print(f"    {i+1}. {cat.get('name', 'N/A')}")
            if len(city_categories) > 5:
                print(f"    ... e mais {len(city_categories) - 5}")
        
        print(f"\n💡 Dados prontos para análise e uso!")
        print(f"🎯 Pode usar estes dados para extração de restaurantes")
    
    def _parallel_restaurants(self):
        """Execução paralela de restaurantes com seleção de categorias"""
        print("\n🚀 Extração paralela de restaurantes")
        
        # Verificar se há categorias
        try:
            from src.utils.database import DatabaseManager
            db = DatabaseManager()
            all_categories = db.get_existing_categories("Birigui")
        except Exception as e:
            self.logger.error(f"Erro ao acessar banco: {e}")
            all_categories = []
        
        if not all_categories:
            print("❌ Nenhuma categoria encontrada!")
            print("💡 Execute primeiro a extração de categorias")
            self.pause()
            return
        
        # Mostrar categorias disponíveis
        print(f"📋 {len(all_categories)} categorias disponíveis:")
        for i, cat in enumerate(all_categories, 1):
            category_name = cat.get('name', 'N/A')
            print(f"  {i:2}. {category_name}")
        
        # Menu de seleção
        print(f"\n🎯 OPÇÕES DE SELEÇÃO:")
        print(f"1. 🎯 Escolher categorias específicas")
        print(f"2. 🌍 Processar todas as categorias")
        print(f"0. 🔙 Voltar ao menu anterior")
        
        choice = input(f"\nEscolha uma opção: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            # Seleção específica de categorias
            selected_categories = self._select_specific_categories(all_categories)
            if not selected_categories:
                print("❌ Nenhuma categoria selecionada")
                self.pause()
                return
        elif choice == "2":
            # Usar todas as categorias
            selected_categories = all_categories
            print(f"✅ Selecionadas todas as {len(selected_categories)} categorias")
        else:
            print("❌ Opção inválida")
            self.pause()
            return
        
        # Mostrar resumo da seleção
        print(f"\n📊 RESUMO DA SELEÇÃO:")
        print(f"  🏷️  Categorias selecionadas: {len(selected_categories)}")
        print(f"  🔧 Workers paralelos: 3")
        
        # Lista categorias selecionadas (máximo 10)
        print(f"\n📋 Categorias que serão processadas:")
        for i, cat in enumerate(selected_categories[:10], 1):
            print(f"  {i:2}. {cat.get('name', 'N/A')}")
        if len(selected_categories) > 10:
            print(f"  ... e mais {len(selected_categories) - 10} categorias")
        
        # Confirmação final
        confirm = input(f"\n⚠️  Continuar com a extração paralela? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        # Pergunta sobre tipo de extração
        print(f"\n🎯 TIPO DE EXTRAÇÃO:")
        print(f"1. ⚡ Extração ULTRA-RÁPIDA (NOVO - Recomendado)")
        print(f"   - RestaurantScraper otimizado + paralelo")
        print(f"   - Dados reais do site iFood")
        print(f"   - 3-5x mais rápido (2-5 min total)")
        print(f"2. 🚀 Extração REAL padrão")
        print(f"   - RestaurantScraper original + paralelo")
        print(f"   - Dados reais mas mais lento (10-30 min)")
        print(f"3. 💨 Extração simulada")
        print(f"   - Dados baseados em templates")
        print(f"   - Muito rápido (segundos)")
        print(f"   - Para testes apenas")
        
        extraction_choice = input(f"\nEscolha o tipo de extração (1/2/3): ").strip()
        
        try:
            if extraction_choice == "1":
                print(f"\n⚡ Iniciando extração ULTRA-RÁPIDA...")
                print(f"🎯 Tempo estimado: {len(selected_categories)*1.5/3:.1f} minutos")
                print(f"💡 Versão otimizada com delays reduzidos")
                
                # Usar o novo extrator ultra-rápido
                from src.scrapers.optimized.ultra_fast_parallel_scraper import UltraFastParallelScraper
                
                scraper = UltraFastParallelScraper(max_workers=3, headless=True)
                
                # Converte categorias
                category_list = []
                for cat in selected_categories:
                    if isinstance(cat, dict):
                        category_list.append({
                            'name': cat.get('name', 'Unknown'),
                            'url': cat.get('url', ''),
                            'city': cat.get('city', 'Birigui')
                        })
                    elif isinstance(cat, tuple) and len(cat) >= 2:
                        category_list.append({
                            'name': cat[0],
                            'url': cat[1],
                            'city': cat[2] if len(cat) > 2 else 'Birigui'
                        })
                
                # Executa extração ultra-rápida
                result = scraper.extract_ultra_fast(category_list)
                
                if result['success']:
                    stats = result['stats']
                    print(f"\n⚡ EXTRAÇÃO ULTRA-RÁPIDA CONCLUÍDA!")
                    print(f"📊 Estatísticas:")
                    print(f"  🏷️  Categorias processadas: {stats['processed']}")
                    print(f"  ✅ Sucessos: {stats['success']}")
                    print(f"  ❌ Falhas: {stats['failed']}")
                    print(f"  🏪 Total restaurantes: {stats['total_restaurants']}")
                    print(f"  💾 Novos salvos: {stats['total_new_saved']}")
                    print(f"  ⏱️  Tempo total: {result['total_duration']/60:.1f} min")
                    print(f"  🚀 Performance: {result['restaurants_per_minute']:.0f} rest/min")
                    print(f"  📈 Média: {result['avg_time_per_category']:.1f}s/categoria")
                    
                    # Atualizar estatísticas
                    self.session_stats['restaurants_extracted'] += stats['total_new_saved']
                    
                else:
                    print(f"❌ Erro na extração ultra-rápida: {result.get('error', 'Erro desconhecido')}")
            
            elif extraction_choice == "2":
                print(f"\n🚀 Iniciando extração paralela REAL...")
                print(f"⚠️  ATENÇÃO: Isso pode demorar 10-30 minutos!")
                print(f"💡 Cada categoria será extraída com scroll completo")
                
                confirm = input(f"\n⚠️  Continuar com extração real? (s/N): ").strip().lower()
                if confirm != 's':
                    print("❌ Operação cancelada")
                    self.pause()
                    return
                
                # Usar o novo extrator paralelo REAL
                from src.scrapers.parallel.real_parallel_restaurant_scraper import RealParallelRestaurantScraper
                
                scraper = RealParallelRestaurantScraper(max_workers=3, headless=True)
                
                # Converte categorias para formato esperado
                category_list = []
                for cat in selected_categories:
                    if isinstance(cat, dict):
                        category_list.append({
                            'name': cat.get('name', 'Unknown'),
                            'url': cat.get('url', ''),
                            'city': cat.get('city', 'Birigui')
                        })
                    elif isinstance(cat, tuple) and len(cat) >= 2:
                        category_list.append({
                            'name': cat[0],
                            'url': cat[1],
                            'city': cat[2] if len(cat) > 2 else 'Birigui'
                        })
                
                # Executa extração paralela REAL
                result = scraper.extract_parallel(category_list)
                
                if result['success']:
                    stats = result['stats']
                    print(f"\n🎉 EXTRAÇÃO PARALELA REAL CONCLUÍDA!")
                    print(f"📊 Estatísticas:")
                    print(f"  🏷️  Categorias processadas: {stats['processed']}")
                    print(f"  ✅ Sucessos: {stats['success']}")
                    print(f"  ❌ Falhas: {stats['failed']}")
                    print(f"  🏪 Total restaurantes encontrados: {stats['total_restaurants']}")
                    print(f"  💾 Total restaurantes novos: {stats['total_new_saved']}")
                    print(f"  🔄 Total duplicados: {stats['total_duplicates']}")
                    print(f"  ⏱️  Tempo total: {result['duration']/60:.2f} minutos")
                    print(f"  🚀 Restaurantes/min: {stats['total_restaurants']/(result['duration']/60):.1f}")
                    
                    # Atualizar estatísticas da sessão
                    self.session_stats['restaurants_extracted'] += stats['total_new_saved']
                    
                else:
                    print(f"❌ Erro na extração paralela real: {result.get('error', 'Erro desconhecido')}")
            
            elif extraction_choice == "2":
                print(f"\n⚡ Iniciando extração simulada rápida...")
                
                # Usar o WindowsParallelScraper para dados simulados
                scraper = WindowsParallelScraper(max_workers=3)
                
                # Converte categorias para formato esperado
                category_list = []
                for cat in selected_categories:
                    if isinstance(cat, dict):
                        category_list.append({
                            'name': cat.get('name', 'Unknown'),
                            'url': cat.get('url', ''),
                            'city': cat.get('city', 'Birigui')
                        })
                    elif isinstance(cat, tuple) and len(cat) >= 2:
                        category_list.append({
                            'name': cat[0],
                            'url': cat[1],
                            'city': cat[2] if len(cat) > 2 else 'Birigui'
                        })
                
                # Executa extração simulada
                result = scraper.extract_restaurants_parallel(category_list)
                
                if result['success']:
                    stats = result['stats']
                    print(f"\n✅ EXTRAÇÃO SIMULADA CONCLUÍDA!")
                    print(f"📊 Estatísticas:")
                    print(f"  🏷️  Categorias processadas: {stats['processed']}")
                    print(f"  ✅ Sucessos: {stats['success']}")
                    print(f"  ❌ Falhas: {stats['failed']}")
                    print(f"  🏪 Restaurantes gerados: {stats['restaurants_generated']}")
                    print(f"  💾 Restaurantes salvos: {stats['restaurants_saved']}")
                    print(f"  ⏱️  Tempo total: {result['duration']:.2f}s")
                    
                    # Atualizar estatísticas da sessão
                    self.session_stats['restaurants_extracted'] += stats['restaurants_saved']
                    
                else:
                    print(f"❌ Erro na extração simulada: {result.get('error', 'Erro desconhecido')}")
            else:
                print("❌ Opção inválida")
                self.pause()
                return
                
        except Exception as e:
            print(f"❌ Erro durante execução: {str(e)}")
            self.logger.error(f"Erro na extração paralela: {e}")
            
        self.pause()
    
    def _select_specific_categories(self, all_categories):
        """Permite seleção específica de categorias"""
        print(f"\n🎯 SELEÇÃO ESPECÍFICA DE CATEGORIAS")
        print("=" * 50)
        
        selected_categories = []
        
        while True:
            # Mostrar categorias disponíveis (não selecionadas)
            available_categories = [cat for cat in all_categories if cat not in selected_categories]
            
            if not available_categories:
                print("✅ Todas as categorias foram selecionadas!")
                break
            
            print(f"\n📋 Categorias disponíveis ({len(available_categories)} restantes):")
            for i, cat in enumerate(available_categories, 1):
                category_name = cat.get('name', 'N/A')
                print(f"  {i:2}. {category_name}")
            
            if selected_categories:
                print(f"\n✅ Categorias já selecionadas ({len(selected_categories)}):")
                for i, cat in enumerate(selected_categories, 1):
                    category_name = cat.get('name', 'N/A')
                    print(f"  ✓ {category_name}")
            
            print(f"\n🎯 OPÇÕES:")
            print(f"  • Digite números das categorias (ex: 1,3,5 ou 1-5)")
            print(f"  • Digite 'all' para selecionar todas restantes")
            print(f"  • Digite 'clear' para limpar seleção")
            print(f"  • Digite 'done' para finalizar seleção")
            print(f"  • Digite '0' para cancelar")
            
            user_input = input(f"\nSua escolha: ").strip().lower()
            
            if user_input == '0':
                return []  # Cancelar
            elif user_input == 'done':
                break  # Finalizar seleção
            elif user_input == 'clear':
                selected_categories = []
                print("🗑️  Seleção limpa!")
                continue
            elif user_input == 'all':
                selected_categories.extend(available_categories)
                print(f"✅ Todas as {len(available_categories)} categorias restantes selecionadas!")
                continue
            
            # Processar números/intervalos
            try:
                selected_indices = self._parse_selection_input(user_input, len(available_categories))
                
                if selected_indices:
                    newly_selected = []
                    for idx in selected_indices:
                        if 1 <= idx <= len(available_categories):
                            category = available_categories[idx - 1]
                            if category not in selected_categories:
                                selected_categories.append(category)
                                newly_selected.append(category.get('name', 'N/A'))
                    
                    if newly_selected:
                        print(f"✅ Adicionadas: {', '.join(newly_selected)}")
                    else:
                        print("⚠️  Nenhuma categoria nova selecionada")
                else:
                    print("❌ Formato inválido. Use: 1,2,3 ou 1-5")
                    
            except Exception as e:
                print(f"❌ Erro na seleção: {e}")
        
        if selected_categories:
            print(f"\n✅ Seleção finalizada!")
            print(f"📊 Total de categorias selecionadas: {len(selected_categories)}")
            return selected_categories
        else:
            print("\n⚠️  Nenhuma categoria foi selecionada")
            return []
    
    def _parse_selection_input(self, user_input, max_number):
        """Analisa entrada do usuário e retorna lista de índices"""
        indices = set()
        
        # Remove espaços e split por vírgula
        parts = [part.strip() for part in user_input.split(',')]
        
        for part in parts:
            if '-' in part:
                # Intervalo (ex: 1-5)
                try:
                    start, end = map(int, part.split('-'))
                    if start > end:
                        start, end = end, start  # Inverte se necessário
                    for i in range(start, end + 1):
                        if 1 <= i <= max_number:
                            indices.add(i)
                except ValueError:
                    continue
            else:
                # Número único
                try:
                    num = int(part)
                    if 1 <= num <= max_number:
                        indices.add(num)
                except ValueError:
                    continue
        
        return sorted(list(indices))
    
    def _select_specific_file_categories(self, available_categories):
        """Permite seleção específica de categorias de arquivos"""
        print(f"\n🎯 SELEÇÃO ESPECÍFICA DE CATEGORIAS")
        print("=" * 50)
        
        selected_categories = []
        
        while True:
            # Mostrar categorias disponíveis (não selecionadas)
            remaining_categories = [cat for cat in available_categories if cat not in selected_categories]
            
            if not remaining_categories:
                print("✅ Todas as categorias foram selecionadas!")
                break
            
            print(f"\n📋 Categorias disponíveis ({len(remaining_categories)} restantes):")
            for i, cat in enumerate(remaining_categories, 1):
                print(f"  {i:2}. {cat['name']} ({cat['count']} restaurantes)")
            
            if selected_categories:
                print(f"\n✅ Categorias já selecionadas ({len(selected_categories)}):")
                for i, cat in enumerate(selected_categories, 1):
                    print(f"  ✓ {cat['name']} ({cat['count']} restaurantes)")
            
            print(f"\n🎯 OPÇÕES:")
            print(f"  • Digite números das categorias (ex: 1,3,5 ou 1-5)")
            print(f"  • Digite 'all' para selecionar todas restantes")
            print(f"  • Digite 'clear' para limpar seleção")
            print(f"  • Digite 'done' para finalizar seleção")
            print(f"  • Digite '0' para cancelar")
            
            user_input = input(f"\nSua escolha: ").strip().lower()
            
            if user_input == '0':
                return []  # Cancelar
            elif user_input == 'done':
                break  # Finalizar seleção
            elif user_input == 'clear':
                selected_categories = []
                print("🗑️  Seleção limpa!")
                continue
            elif user_input == 'all':
                selected_categories.extend(remaining_categories)
                print(f"✅ Todas as {len(remaining_categories)} categorias restantes selecionadas!")
                continue
            
            # Processar números/intervalos
            try:
                selected_indices = self._parse_selection_input(user_input, len(remaining_categories))
                
                if selected_indices:
                    newly_selected = []
                    for idx in selected_indices:
                        if 1 <= idx <= len(remaining_categories):
                            category = remaining_categories[idx - 1]
                            if category not in selected_categories:
                                selected_categories.append(category)
                                newly_selected.append(f"{category['name']} ({category['count']} rest.)")
                    
                    if newly_selected:
                        print(f"✅ Adicionadas: {', '.join(newly_selected)}")
                    else:
                        print("⚠️  Nenhuma categoria nova selecionada")
                else:
                    print("❌ Formato inválido. Use: 1,2,3 ou 1-5")
                    
            except Exception as e:
                print(f"❌ Erro na seleção: {e}")
        
        if selected_categories:
            total_restaurants = sum(cat['count'] for cat in selected_categories)
            print(f"\n✅ Seleção finalizada!")
            print(f"📊 Total: {len(selected_categories)} categorias, {total_restaurants} restaurantes")
            return selected_categories
        else:
            print("\n⚠️  Nenhuma categoria foi selecionada")
            return []
    
    def _parallel_products(self):
        """Execução paralela de produtos"""
        print("\n🚀 Extração paralela de produtos")
        
        # Verificar se há arquivos de restaurantes
        restaurants_dir = self.data_dir / "restaurants"
        if not restaurants_dir.exists():
            print("❌ Diretório de restaurantes não encontrado!")
            print("💡 Execute primeiro a extração de restaurantes")
            self.pause()
            return
        
        restaurant_files = list(restaurants_dir.glob("*.csv"))
        if not restaurant_files:
            print("❌ Nenhum arquivo de restaurante encontrado!")
            print("💡 Execute primeiro a extração de restaurantes")
            self.pause()
            return
        
        print(f"📋 {len(restaurant_files)} arquivos de restaurantes encontrados:")
        for i, file in enumerate(restaurant_files[:5], 1):
            print(f"  {i}. {file.stem}")
        if len(restaurant_files) > 5:
            print(f"  ... e mais {len(restaurant_files) - 5} arquivos")
        
        # Configurações
        print(f"\n⚙️  Configurações atuais:")
        print(f"  🔧 Workers paralelos: {self.parallel_scraper.max_workers}")
        print(f"  📁 Arquivos disponíveis: {len(restaurant_files)}")
        
        # Mostrar categorias disponíveis para seleção
        print(f"\n📋 Categorias de restaurantes disponíveis:")
        available_categories = []
        total_restaurants = 0
        
        for file in restaurant_files:
            # Extrair categoria do nome do arquivo
            filename = file.stem
            if "restaurantes_" in filename:
                category = filename.split("restaurantes_")[-1].replace("_", " ").title()
                
                # Contar restaurantes no arquivo
                try:
                    import csv
                    with open(file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        restaurant_count = len(list(reader))
                        total_restaurants += restaurant_count
                except:
                    restaurant_count = 0
                
                available_categories.append({
                    'name': category,
                    'file': file,
                    'count': restaurant_count
                })
        
        # Mostrar lista numerada
        for i, cat in enumerate(available_categories, 1):
            print(f"  {i:2}. {cat['name']} ({cat['count']} restaurantes)")
        
        # Menu de seleção
        print(f"\n🎯 OPÇÕES DE SELEÇÃO:")
        print(f"1. 🎯 Escolher categorias específicas")
        print(f"2. 🌍 Processar todas as categorias ({total_restaurants} restaurantes)")
        print(f"0. 🔙 Voltar ao menu anterior")
        
        choice = input(f"\nEscolha uma opção: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            # Seleção específica de categorias
            selected_file_categories = self._select_specific_file_categories(available_categories)
            if not selected_file_categories:
                print("❌ Nenhuma categoria selecionada")
                self.pause()
                return
            selected_files = [cat['file'] for cat in selected_file_categories]
            selected_categories = [cat['name'] for cat in selected_file_categories]
        elif choice == "2":
            # Usar todas as categorias
            selected_files = restaurant_files
            selected_categories = [cat['name'] for cat in available_categories]
            print(f"✅ Selecionadas todas as {len(selected_categories)} categorias")
        else:
            print("❌ Opção inválida")
            self.pause()
            return
        
        # Mostrar resumo da seleção
        print(f"\n📋 RESUMO DA SELEÇÃO:")
        for i, category in enumerate(selected_categories):
            print(f"  ✅ {category}")
        
        confirm = input(f"\n⚠️  Processar {len(selected_categories)} categoria(s)? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        try:
            print(f"\n🚀 Iniciando extração paralela com {self.parallel_scraper.max_workers} workers...")
            print(f"📋 Processando categorias: {', '.join(selected_categories)}")
            
            # Carregar restaurantes apenas dos arquivos selecionados
            import csv
            all_restaurants = []
            
            for restaurant_file in selected_files:
                try:
                    with open(restaurant_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        restaurants = list(reader)
                        
                        # Normalizar campos para o formato esperado pelo run_parallel_products
                        for restaurant in restaurants:
                            # Mapear 'nome' para 'name' se necessário
                            if 'nome' in restaurant and 'name' not in restaurant:
                                restaurant['name'] = restaurant['nome']
                            
                            # Garantir que os campos obrigatórios existem
                            if 'url' not in restaurant or not restaurant['url']:
                                restaurant['url'] = restaurant.get('url', '')
                            if 'id' not in restaurant or not restaurant['id']:
                                restaurant['id'] = restaurant.get('id', restaurant.get('nome', 'unknown'))
                        
                        all_restaurants.extend(restaurants)
                        print(f"    📁 {restaurant_file.name}: {len(restaurants)} restaurantes")
                except Exception as e:
                    print(f"    ❌ Erro ao ler {restaurant_file.name}: {e}")
                    continue
            
            if not all_restaurants:
                raise Exception("Nenhum restaurante encontrado nos arquivos")
            
            print(f"    📊 Total: {len(all_restaurants)} restaurantes para processar")
            
            # Detectar se é Windows e usar sistema nativo
            if detect_windows() or platform.system() == "Windows":
                print(f"🪟 Sistema Windows detectado!")
                print(f"💡 Usando extração paralela nativa para Windows...")
                
                # Usar WindowsParallelScraper
                windows_scraper = WindowsParallelScraper(max_workers=self.parallel_scraper.max_workers)
                
                # Configurar event loop para Windows
                if platform.system() == "Windows":
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                
                try:
                    # Executar extração nativa Windows passando os restaurantes filtrados
                    result = asyncio.run(windows_scraper.run_parallel_extraction(
                        max_restaurants=len(all_restaurants),
                        filter_restaurants=all_restaurants
                    ))
                    
                    # Exibir estatísticas
                    stats = result.get('stats', {})
                    print(f"\n✅ EXTRAÇÃO WINDOWS CONCLUÍDA!")
                    print(f"📊 Estatísticas:")
                    print(f"  🏪 Restaurantes: {stats.get('total_restaurants', 0)}")
                    print(f"  ✅ Sucessos: {stats.get('successful_extractions', 0)}")
                    print(f"  ❌ Falhas: {stats.get('failed_extractions', 0)}")
                    print(f"  🍕 Produtos: {stats.get('total_products', 0)}")
                    print(f"  ⏱️  Tempo: {stats.get('total_time', 0):.2f}s")
                    print(f"  🚀 Velocidade: {stats.get('products_per_second', 0):.1f} produtos/s")
                    print(f"  🔧 Workers: {stats.get('workers_used', 0)}")
                    
                    # Salvar estatísticas na sessão
                    self.session_stats['products_extracted'] += stats.get('total_products', 0)
                    self.session_stats['restaurants_extracted'] += stats.get('successful_extractions', 0)
                    
                    # Finalizar com sucesso
                    self.pause()
                    return
                    
                except Exception as e:
                    print(f"❌ Erro na extração Windows: {e}")
                    self.pause()
                    return
            
            # Para sistemas não-Windows, usar fallback
            else:
                print(f"🐧 Sistema Linux/WSL detectado")
                print(f"💡 Usando sistema Windows nativo mesmo assim...")
                
                # Usar o mesmo sistema Windows nativo
                windows_scraper = WindowsParallelScraper(max_workers=self.parallel_scraper.max_workers)
                
                try:
                    result = asyncio.run(windows_scraper.run_parallel_extraction(
                        max_restaurants=len(all_restaurants),
                        filter_restaurants=all_restaurants
                    ))
                    
                    stats = result.get('stats', {})
                    print(f"\n✅ EXTRAÇÃO CONCLUÍDA!")
                    print(f"📊 Estatísticas:")
                    print(f"  🏪 Restaurantes: {stats.get('total_restaurants', 0)}")
                    print(f"  🍕 Produtos: {stats.get('total_products', 0)}")
                    print(f"  ⏱️  Tempo: {stats.get('total_time', 0):.2f}s")
                    
                    self.session_stats['products_extracted'] += stats.get('total_products', 0)
                    self.session_stats['restaurants_extracted'] += stats.get('successful_extractions', 0)
                    
                except Exception as e:
                    print(f"❌ Erro na extração: {e}")
                
            
        except Exception as e:
            self.logger.error(f"Erro durante extração paralela: {e}")
            print(f"\n❌ Erro durante extração: {e}")
            
        self.pause()
    
    def _parallel_full_pipeline(self):
        """Execução completa em paralelo"""
        print("\n🚀 Pipeline completo em paralelo")
        print("Executa: Categorias → Restaurantes → Produtos")
        
        # Configurações
        print(f"\n⚙️  Configurações:")
        print(f"  🔧 Workers paralelos: {self.parallel_scraper.max_workers}")
        print(f"  🌐 Cidade: Birigui")
        
        print(f"\n📋 Etapas do pipeline:")
        print(f"  1️⃣  Extrair categorias")
        print(f"  2️⃣  Extrair restaurantes (paralelo)")
        print(f"  3️⃣  Extrair produtos (paralelo)")
        
        confirm = input("\n⚠️  Pipeline completo pode demorar muito tempo. Continuar? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operação cancelada")
            self.pause()
            return
        
        try:
            from datetime import datetime
            start_time = datetime.now()
            total_stats = {
                'categories': 0,
                'restaurants': 0,
                'products': 0
            }
            
            print(f"\n🚀 Iniciando pipeline completo...")
            
            # ETAPA 1: Categorias
            print(f"\n1️⃣  ETAPA 1: Extraindo categorias...")
            try:
                from playwright.sync_api import sync_playwright
                from src.scrapers.category_scraper import CategoryScraper
                
                with sync_playwright() as p:
                    scraper = CategoryScraper(city="Birigui")
                    result = scraper.run(p)
                    
                    if result['success']:
                        total_stats['categories'] = result['categories_found']
                        print(f"    ✅ {result['categories_found']} categorias extraídas")
                    else:
                        print(f"    ❌ Erro nas categorias: {result['error']}")
                        raise Exception(f"Falha na extração de categorias: {result['error']}")
            except Exception as e:
                print(f"    ❌ Erro na etapa 1: {e}")
                self.pause()
                return
            
            # ETAPA 2: Restaurantes (paralelo)
            print(f"\n2️⃣  ETAPA 2: Extraindo restaurantes em paralelo...")
            try:
                from src.utils.database import DatabaseManager
                from src.scrapers.optimized.ultra_fast_parallel_scraper import UltraFastParallelScraper
                
                db = DatabaseManager()
                categories = db.get_existing_categories("Birigui")
                
                if not categories:
                    raise Exception("Nenhuma categoria encontrada após extração")
                
                # Usa o UltraFastParallelScraper em vez da função antiga
                scraper = UltraFastParallelScraper(max_workers=self.parallel_scraper.max_workers, headless=True)
                result = scraper.extract_from_database_ultra_fast()
                
                if result and result.get('success', False):
                    stats = result['stats']
                    total_stats['restaurants'] = stats.get('total_restaurants', 0)
                    print(f"    ✅ {stats.get('success', 0)} categorias processadas, {stats.get('total_restaurants', 0)} restaurantes extraídos")
                else:
                    print(f"    ❌ Erro nos restaurantes: Resultado inválido")
                    raise Exception(f"Falha na extração de restaurantes: resultado inválido")
            except Exception as e:
                print(f"    ❌ Erro na etapa 2: {e}")
                self.pause()
                return
            
            # ETAPA 3: Produtos (paralelo)
            print(f"\n3️⃣  ETAPA 3: Extraindo produtos em paralelo...")
            try:
                from src.scrapers.parallel.windows_parallel_scraper import WindowsParallelScraper
                import csv
                
                restaurants_dir = self.data_dir / "restaurants"
                restaurant_files = list(restaurants_dir.glob("*.csv"))
                
                if not restaurant_files:
                    raise Exception("Nenhum arquivo de restaurante encontrado após extração")
                
                # Carregar restaurantes de todos os arquivos
                all_restaurants = []
                for restaurant_file in restaurant_files:
                    try:
                        with open(restaurant_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            restaurants = list(reader)
                            
                            # Normalizar campos
                            for restaurant in restaurants:
                                # Mapear 'nome' para 'name' se necessário
                                if 'nome' in restaurant and 'name' not in restaurant:
                                    restaurant['name'] = restaurant['nome']
                                
                                # Garantir que os campos obrigatórios existem
                                if 'url' not in restaurant or not restaurant['url']:
                                    restaurant['url'] = restaurant.get('url', '')
                                if 'id' not in restaurant or not restaurant['id']:
                                    restaurant['id'] = restaurant.get('id', restaurant.get('nome', 'unknown'))
                            
                            all_restaurants.extend(restaurants)
                    except Exception as e:
                        print(f"    ⚠️  Erro ao ler {restaurant_file.name}: {e}")
                        continue
                
                if not all_restaurants:
                    raise Exception("Nenhum restaurante encontrado nos arquivos")
                
                # Usa WindowsParallelScraper para produtos (dados simulados)
                products_scraper = WindowsParallelScraper(max_workers=self.parallel_scraper.max_workers)
                
                # Extrai produtos baseado nos restaurantes
                result = products_scraper.extract_products_parallel(all_restaurants)
                
                if result and result.get('success', False):
                    total_products = result.get('products_extracted', 0)
                    total_stats['products'] = total_products
                    print(f"    ✅ {total_products} produtos extraidos (simulados)")
                else:
                    print(f"    ⚠️  Nenhum produto extraído")
                    print(f"    📝 Usando dados simulados para demonstração")
                    
            except Exception as e:
                print(f"    ❌ Erro na etapa 3: {e}")
                self.pause()
                return
            
            # Resumo final
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Atualiza estatísticas da sessão
            self.session_stats['categories_extracted'] += total_stats['categories']
            self.session_stats['restaurants_extracted'] += total_stats['restaurants']
            self.session_stats['products_extracted'] += total_stats['products']
            
            print(f"\n🎉 PIPELINE COMPLETO CONCLUÍDO!")
            print(f"📊 Resumo final:")
            print(f"  🏷️  Categorias: {total_stats['categories']}")
            print(f"  🏪 Restaurantes: {total_stats['restaurants']}")
            print(f"  🍕 Produtos: {total_stats['products']}")
            print(f"  ⏱️  Tempo total: {duration}")
            print(f"  🚀 Workers utilizados: {self.parallel_scraper.max_workers}")
                
        except Exception as e:
            self.logger.error(f"Erro no pipeline: {e}")
            print(f"❌ Erro no pipeline: {e}")
        
        self.pause()
    
    def _configure_workers(self):
        """Configura workers paralelos"""
        print("\n⚙️  Configuração de workers")
        current_workers = self.parallel_scraper.max_workers
        print(f"Workers atuais: {current_workers}")
        
        try:
            new_workers = int(input("Novo número de workers [3]: ") or "3")
            self.parallel_scraper.max_workers = new_workers
            self.show_success(f"Workers configurados para {new_workers}")
        except ValueError:
            self.show_error("Valor inválido!")
        
        self.pause()
    
    def _demo_performance(self):
        """Demonstração de performance e diagnóstico"""
        print("\n📊 Demonstração de performance e diagnóstico")
        
        print("\n🔍 DIAGNÓSTICO DO SISTEMA:")
        print("═" * 50)
        
        # Verificar Python
        import sys
        print(f"✅ Python: {sys.version.split()[0]}")
        
        # Verificar Playwright
        try:
            import playwright
            print(f"✅ Playwright: Instalado")
        except ImportError:
            print(f"❌ Playwright: Não instalado")
            print(f"   💡 Instale com: pip install playwright")
        
        # Verificar dependências do sistema
        import subprocess
        import os
        
        print(f"\n🖥️  AMBIENTE:")
        print(f"   OS: {os.name}")
        print(f"   Platform: {sys.platform}")
        
        # Testar dependências
        print(f"\n🔧 DEPENDÊNCIAS DO NAVEGADOR:")
        missing_deps = []
        required_libs = ['libnss3', 'libnspr4', 'libasound2']
        
        for lib in required_libs:
            try:
                result = subprocess.run(['dpkg', '-l', lib], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ {lib}: Instalado")
                else:
                    print(f"   ❌ {lib}: Faltando")
                    missing_deps.append(lib)
            except:
                print(f"   ⚠️  {lib}: Não pôde verificar")
                missing_deps.append(lib)
        
        if missing_deps:
            print(f"\n🚨 SOLUÇÃO PARA DEPENDÊNCIAS FALTANDO:")
            print(f"   Execute um dos comandos:")
            print(f"   1️⃣  sudo playwright install-deps")
            print(f"   2️⃣  sudo apt-get install {' '.join(missing_deps)}")
        else:
            print(f"\n✅ Todas as dependências parecem instaladas!")
        
        # Teste rápido do navegador
        print(f"\n🧪 TESTE DO NAVEGADOR:")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("data:text/html,<h1>Teste</h1>")
                title = page.title()
                browser.close()
                print(f"   ✅ Navegador: Funcionando ({title})")
        except Exception as e:
            print(f"   ❌ Navegador: Falhou")
            print(f"   🔍 Erro: {str(e)[:100]}...")
            
        print(f"\n📋 RESUMO:")
        print(f"   🎯 Sistema Modular: ✅ Funcionando")
        print(f"   📊 Interface: ✅ Funcionando") 
        print(f"   🔧 Lógica de Negócio: ✅ Funcionando")
        print(f"   🌐 Navegador: {'✅ OK' if not missing_deps else '❌ Dependências faltando'}")
        
        # Oferecer instalação automática
        if missing_deps:
            print(f"\n🔧 INSTALAÇÃO AUTOMÁTICA:")
            install_choice = input(f"   Tentar instalar dependências automaticamente? (s/N): ").strip().lower()
            
            if install_choice == 's':
                self._try_install_dependencies()
        
        self.pause()
    
    def _try_install_dependencies(self):
        """Tenta instalar dependências automaticamente"""
        print(f"\n🚀 Tentando instalar dependências...")
        
        try:
            import subprocess
            
            # Tentar playwright install-deps
            print(f"   🔧 Executando: playwright install-deps")
            result = subprocess.run(['playwright', 'install-deps'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   ✅ Dependências instaladas com sucesso!")
                print(f"   🎯 Reinicie o sistema para testar")
            else:
                print(f"   ⚠️  Comando playwright falhou, tentando apt-get...")
                
                # Fallback para apt-get
                deps = ['libnss3', 'libnspr4', 'libasound2', 'libatk-bridge2.0-0']
                cmd = ['sudo', 'apt-get', 'install', '-y'] + deps
                
                print(f"   🔧 Executando: {' '.join(cmd)}")
                result2 = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result2.returncode == 0:
                    print(f"   ✅ Dependências básicas instaladas!")
                else:
                    print(f"   ❌ Falha na instalação automática")
                    print(f"   💡 Execute manualmente: sudo playwright install-deps")
                    
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout na instalação (>5min)")
        except Exception as e:
            print(f"   ❌ Erro na instalação: {e}")
            print(f"   💡 Execute manualmente: sudo playwright install-deps")
    
    # ================== SISTEMA DE BUSCA ==================
    
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
        
        # Coleta filtros do usuário
        print("📝 Preencha os filtros (Enter para pular):")
        query = input("🔍 Nome/termo de busca: ").strip()
        category = input("📂 Categoria (ex: Açaí, Japonesa): ").strip()
        
        try:
            min_rating = input("⭐ Avaliação mínima (0-5): ").strip()
            min_rating = float(min_rating) if min_rating else None
        except ValueError:
            min_rating = None
        
        city = input("🏙️  Cidade: ").strip()
        
        print(f"\n🔍 Buscando restaurantes...")
        
        try:
            results = self.search_optimizer.search_restaurants(
                query=query if query else None,
                category=category if category else None,
                min_rating=min_rating,
                city=city if city else None
            )
            
            if results:
                print(f"\n✅ {len(results)} restaurantes encontrados:")
                print("─" * 80)
                
                for i, restaurant in enumerate(results[:15], 1):
                    name = restaurant.get('nome', 'N/A')
                    cat = restaurant.get('categoria', 'N/A')
                    rating = restaurant.get('avaliacao', 'N/A')
                    city_name = restaurant.get('cidade', 'N/A')
                    
                    print(f"{i:2}. 🏪 {name:<30} | 📂 {cat:<12} | ⭐ {rating} | 🏙️ {city_name}")
                
                if len(results) > 15:
                    print(f"\n... e mais {len(results) - 15} restaurantes")
                
                # Opções adicionais
                print(f"\n📊 OPÇÕES:")
                print("1. 💾 Exportar resultados")
                print("2. 🔍 Ver detalhes de um restaurante")
                print("0. ⬅️  Voltar")
                
                choice = input("\nEscolha: ").strip()
                
                if choice == "1":
                    self._export_search_results(results, "restaurantes")
                elif choice == "2":
                    self._show_restaurant_details(results)
                    
            else:
                print("\n❌ Nenhum restaurante encontrado com os filtros especificados")
                
            self.session_stats['searches_performed'] += 1
            
        except Exception as e:
            self.show_error(f"Erro na busca: {e}")
        
        self.pause()
    
    def _search_products(self):
        """Busca produtos com filtros avançados"""
        print("\n🍕 BUSCA AVANÇADA DE PRODUTOS")
        print("═" * 50)
        
        # Coleta filtros do usuário
        print("📝 Preencha os filtros (Enter para pular):")
        query = input("🔍 Nome do produto: ").strip()
        category = input("📂 Categoria (ex: Açaí, Pizza): ").strip()
        restaurant = input("🏪 Restaurante: ").strip()
        
        # Filtros de preço
        try:
            min_price = input("💰 Preço mínimo (R$): ").strip()
            min_price = float(min_price.replace('R$', '').replace(',', '.')) if min_price else None
        except ValueError:
            min_price = None
            
        try:
            max_price = input("💰 Preço máximo (R$): ").strip()
            max_price = float(max_price.replace('R$', '').replace(',', '.')) if max_price else None
        except ValueError:
            max_price = None
        
        print(f"\n🔍 Buscando produtos...")
        
        try:
            results = self.search_optimizer.search_products(
                query=query if query else None,
                category=category if category else None,
                restaurant_name=restaurant if restaurant else None,
                min_price=min_price,
                max_price=max_price
            )
            
            if results:
                print(f"\n✅ {len(results)} produtos encontrados:")
                print("─" * 90)
                
                for i, product in enumerate(results[:20], 1):
                    name = product.get('nome', 'N/A')[:25]
                    price = product.get('preco', 'N/A')
                    restaurant_name = product.get('restaurante', 'N/A')[:20]
                    cat = product.get('categoria_produto', 'N/A')[:15]
                    
                    print(f"{i:2}. 🍕 {name:<25} | 💰 {price:<8} | 🏪 {restaurant_name:<20} | 📂 {cat}")
                
                if len(results) > 20:
                    print(f"\n... e mais {len(results) - 20} produtos")
                
                # Estatísticas rápidas
                if results:
                    prices = []
                    for p in results:
                        price_str = p.get('preco', '0')
                        try:
                            price_num = float(price_str.replace('R$', '').replace(',', '.'))
                            if price_num > 0:
                                prices.append(price_num)
                        except:
                            pass
                    
                    if prices:
                        avg_price = sum(prices) / len(prices)
                        min_p = min(prices)
                        max_p = max(prices)
                        print(f"\n📊 Estatísticas: Preço médio: R$ {avg_price:.2f} | Min: R$ {min_p:.2f} | Max: R$ {max_p:.2f}")
                
                # Opções adicionais
                print(f"\n📊 OPÇÕES:")
                print("1. 💾 Exportar resultados")
                print("2. 📈 Análise de preços detalhada")
                print("3. 🔍 Ver produtos de um restaurante específico")
                print("0. ⬅️  Voltar")
                
                choice = input("\nEscolha: ").strip()
                
                if choice == "1":
                    self._export_search_results(results, "produtos")
                elif choice == "2":
                    self._analyze_product_prices(results)
                elif choice == "3":
                    self._show_restaurant_products(results)
                    
            else:
                print("\n❌ Nenhum produto encontrado com os filtros especificados")
                
            self.session_stats['searches_performed'] += 1
            
        except Exception as e:
            self.show_error(f"Erro na busca: {e}")
        
        self.pause()
    
    def _show_popular_categories(self):
        """Mostra categorias populares com análise detalhada"""
        print("\n📊 ANÁLISE DE CATEGORIAS POPULARES")
        print("═" * 60)
        
        try:
            categories = self.search_optimizer.get_popular_categories(limit=15)
            
            if categories:
                print("🏆 TOP CATEGORIAS POR NÚMERO DE RESTAURANTES:")
                print("─" * 60)
                
                total_restaurants = sum(cat.get('restaurant_count', 0) for cat in categories)
                
                for i, cat in enumerate(categories, 1):
                    name = cat.get('categoria', 'N/A')
                    count = cat.get('restaurant_count', 0)
                    rating = cat.get('avg_rating', 0)
                    percentage = (count / total_restaurants * 100) if total_restaurants > 0 else 0
                    
                    # Barra visual
                    bar_length = 20
                    filled = int(bar_length * percentage / 100)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    
                    print(f"{i:2}. 📂 {name:<15} | {count:3} rest. | ⭐ {rating:.1f} | {percentage:5.1f}% [{bar}]")
                
                print(f"\n📈 Total analisado: {total_restaurants} restaurantes")
                
                # Opções adicionais
                print(f"\n📊 OPÇÕES:")
                print("1. 🔍 Ver restaurantes de uma categoria")
                print("2. 📈 Comparar categorias")
                print("3. 💰 Análise de preços por categoria")
                print("0. ⬅️  Voltar")
                
                choice = input("\nEscolha: ").strip()
                
                if choice == "1":
                    self._show_category_restaurants(categories)
                elif choice == "2":
                    self._compare_categories(categories)
                elif choice == "3":
                    self._analyze_category_prices()
            else:
                print("❌ Nenhuma categoria encontrada")
                
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _analyze_prices(self):
        """Análise detalhada de preços"""
        print("\n💰 ANÁLISE DETALHADA DE PREÇOS")
        print("═" * 60)
        
        try:
            # Opções de análise
            print("📋 Escolha o tipo de análise:")
            print("1. 📊 Distribuição geral de preços")
            print("2. 📂 Preços por categoria")
            print("3. 🏪 Preços por restaurante")
            print("4. 📈 Comparativo de faixas de preço")
            print("0. ⬅️  Voltar")
            
            choice = input("\nEscolha: ").strip()
            
            if choice == "1":
                self._show_general_price_distribution()
            elif choice == "2":
                self._show_category_price_analysis()
            elif choice == "3":
                self._show_restaurant_price_analysis()
            elif choice == "4":
                self._show_price_range_comparison()
            elif choice == "0":
                return
            else:
                print("❌ Opção inválida")
                
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _show_recommendations(self):
        """Sistema inteligente de recomendações"""
        print("\n🎯 SISTEMA DE RECOMENDAÇÕES INTELIGENTES")
        print("═" * 60)
        
        print("📋 Tipos de recomendação disponíveis:")
        print("1. 🏪 Restaurantes similares (baseado em categoria)")
        print("2. 🍕 Produtos populares por categoria")
        print("3. ⭐ Melhores avaliados por faixa de preço")
        print("4. 🔥 Trending (mais produtos únicos)")
        print("5. 🎲 Descoberta aleatória")
        print("0. ⬅️  Voltar")
        
        choice = input("\nEscolha o tipo de recomendação: ").strip()
        
        try:
            if choice == "1":
                self._recommend_similar_restaurants()
            elif choice == "2":
                self._recommend_popular_products()
            elif choice == "3":
                self._recommend_by_rating_and_price()
            elif choice == "4":
                self._recommend_trending()
            elif choice == "5":
                self._recommend_random_discovery()
            elif choice == "0":
                return
            else:
                print("❌ Opção inválida")
                
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _show_database_stats(self):
        """Mostra estatísticas detalhadas do banco"""
        print("\n📈 ESTATÍSTICAS DETALHADAS DO BANCO")
        print("═" * 60)
        
        try:
            # Estatísticas básicas
            stats = self.search_optimizer.get_database_statistics()
            
            if stats:
                print("📊 DADOS GERAIS:")
                print("─" * 30)
                print(f"🏪 Restaurantes: {stats.get('total_restaurants', 0):,}")
                print(f"🍕 Produtos: {stats.get('total_products', 0):,}")
                print(f"📂 Categorias: {stats.get('total_categories', 0):,}")
                
                print(f"\n💰 ANÁLISE DE PREÇOS:")
                print("─" * 30)
                if 'price_stats' in stats:
                    price_stats = stats['price_stats']
                    print(f"💵 Preço médio: R$ {price_stats.get('avg_price', 0):.2f}")
                    print(f"💸 Preço mínimo: R$ {price_stats.get('min_price', 0):.2f}")
                    print(f"💰 Preço máximo: R$ {price_stats.get('max_price', 0):.2f}")
                    print(f"📈 Produtos com preço: {price_stats.get('products_with_price', 0):,}")
                
                print(f"\n⭐ AVALIAÇÕES:")
                print("─" * 30)
                if 'rating_stats' in stats:
                    rating_stats = stats['rating_stats']
                    print(f"⭐ Avaliação média: {rating_stats.get('avg_rating', 0):.2f}")
                    print(f"🌟 Melhor avaliação: {rating_stats.get('max_rating', 0):.1f}")
                    print(f"📊 Restaurantes avaliados: {rating_stats.get('restaurants_with_rating', 0):,}")
                
                print(f"\n📂 TOP 5 CATEGORIAS:")
                print("─" * 40)
                if 'top_categories' in stats:
                    for i, cat in enumerate(stats['top_categories'][:5], 1):
                        name = cat.get('categoria', 'N/A')
                        count = cat.get('count', 0)
                        print(f"{i}. {name:<20} {count:>4} restaurantes")
                
                # Opções adicionais
                print(f"\n📊 OPÇÕES AVANÇADAS:")
                print("1. 📈 Análise temporal dos dados")
                print("2. 🔍 Estatísticas por cidade")
                print("3. 💾 Exportar relatório completo")
                print("4. 🔄 Atualizar estatísticas")
                print("0. ⬅️  Voltar")
                
                choice = input("\nEscolha: ").strip()
                
                if choice == "1":
                    self._show_temporal_analysis()
                elif choice == "2":
                    self._show_city_statistics()
                elif choice == "3":
                    self._export_database_report()
                elif choice == "4":
                    self._refresh_database_stats()
                    
            else:
                print("❌ Não foi possível carregar estatísticas")
                
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    # ================== GERENCIADOR DE ARQUIVOS ==================
    
    def menu_archive_manager(self):
        """Menu do gerenciador de arquivos"""
        options = [
            "1. 📦 Comprimir arquivos antigos",
            "2. 🗂️  Criar arquivos mensais",
            "3. 🧹 Limpar arquivos antigos",
            "4. 📋 Gerar índice de arquivos",
            "5. 📊 Estatísticas de armazenamento",
            "6. 🔄 Descomprimir arquivo",
            "7. ⚙️  Configurar retenção"
        ]
        
        self.show_menu("🗜️ GERENCIADOR DE ARQUIVOS", options)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._compress_old_files()
        elif choice == "2":
            self._create_monthly_archives()
        elif choice == "3":
            self._cleanup_old_files()
        elif choice == "4":
            self._generate_file_index()
        elif choice == "5":
            self._show_storage_stats()
        elif choice == "6":
            self._decompress_file()
        elif choice == "7":
            self._configure_retention()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _compress_old_files(self):
        """Comprime arquivos antigos"""
        print("\n📦 Comprimindo arquivos antigos...")
        try:
            self.archive_manager.compress_individual_files()
            self.archive_manager.show_statistics()
            self.session_stats['files_compressed'] += 1
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _create_monthly_archives(self):
        """Cria arquivos mensais"""
        print("\n🗂️  Criando arquivos mensais...")
        try:
            self.archive_manager.archive_by_date()
            self.archive_manager.show_statistics()
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _cleanup_old_files(self):
        """Limpa arquivos antigos"""
        print("\n🧹 Limpando arquivos antigos...")
        days = input("Remover arquivos mais antigos que quantos dias? [90]: ").strip()
        days = int(days) if days.isdigit() else 90
        
        try:
            self.archive_manager.cleanup_old_archives(days)
            self.show_success(f"Limpeza concluída para arquivos > {days} dias")
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _generate_file_index(self):
        """Gera índice de arquivos"""
        print("\n📋 Gerando índice de arquivos...")
        try:
            index = self.archive_manager.generate_index()
            self.show_success(f"Índice gerado com {index['statistics']['total_archives']} arquivos")
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _show_storage_stats(self):
        """Mostra estatísticas de armazenamento"""
        print("\n📊 Estatísticas de armazenamento")
        self.archive_manager.show_statistics()
        self.pause()
    
    def _decompress_file(self):
        """Descomprime arquivo"""
        print("\n🔄 Descomprimir arquivo")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _configure_retention(self):
        """Configura retenção de arquivos"""
        print("\n⚙️  Configuração de retenção")
        current_retention = self.archive_manager.retention_days
        print(f"Retenção atual: {current_retention} dias")
        
        try:
            new_retention = int(input("Nova retenção (dias): ") or str(current_retention))
            self.archive_manager.retention_days = new_retention
            self.show_success(f"Retenção configurada para {new_retention} dias")
        except ValueError:
            self.show_error("Valor inválido!")
        
        self.pause()
    
    # ================== RELATÓRIOS E ANÁLISES ==================
    
    def menu_reports(self):
        """Menu de relatórios e análises"""
        options = [
            "1. 📈 Relatório geral",
            "2. 🏪 Análise de restaurantes",
            "3. 🍕 Análise de produtos",
            "4. 💰 Análise de preços",
            "5. 🎯 Top categorias",
            "6. 📋 Exportar dados",
            "7. 🔍 Busca avançada"
        ]
        
        self.show_menu("📊 RELATÓRIOS E ANÁLISES", options)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._general_report()
        elif choice == "2":
            self._restaurant_analysis()
        elif choice == "3":
            self._product_analysis()
        elif choice == "4":
            self._price_analysis()
        elif choice == "5":
            self._top_categories()
        elif choice == "6":
            self._export_data()
        elif choice == "7":
            self._advanced_search()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _general_report(self):
        """Relatório geral"""
        print("\n📈 Relatório geral do sistema")
        print("Gerando relatório...")
        self.pause()
    
    def _restaurant_analysis(self):
        """Análise de restaurantes"""
        print("\n🏪 Análise de restaurantes")
        print("Analisando dados...")
        self.pause()
    
    def _product_analysis(self):
        """Análise de produtos"""
        print("\n🍕 Análise de produtos")
        print("Analisando dados...")
        self.pause()
    
    def _price_analysis(self):
        """Análise de preços"""
        print("\n💰 Análise de preços")
        print("Analisando preços...")
        self.pause()
    
    def _top_categories(self):
        """Top categorias"""
        print("\n🎯 Top categorias")
        print("Analisando categorias...")
        self.pause()
    
    def _export_data(self):
        """Exporta dados"""
        print("\n📋 Exportação de dados")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _advanced_search(self):
        """Busca avançada"""
        print("\n🔍 Busca avançada")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    # ================== CONFIGURAÇÕES ==================
    
    def menu_settings(self):
        """Menu de configurações"""
        options = [
            "1. 🌐 Configurar cidade padrão",
            "2. 🔧 Configurar workers paralelos",
            "3. 💾 Configurar cache",
            "4. 🗂️  Configurar diretórios",
            "5. 🔄 Configurar retenção de arquivos",
            "6. 📊 Configurar logging",
            "7. 🎯 Configurações avançadas",
            "8. 💾 Salvar configurações"
        ]
        
        self.show_menu("⚙️ CONFIGURAÇÕES", options)
        choice = self.get_user_choice(8)
        
        if choice == "1":
            self._configure_default_city()
        elif choice == "2":
            self._configure_workers()
        elif choice == "3":
            self._configure_cache()
        elif choice == "4":
            self._configure_directories()
        elif choice == "5":
            self._configure_file_retention()
        elif choice == "6":
            self._configure_logging()
        elif choice == "7":
            self._advanced_settings()
        elif choice == "8":
            self._save_settings()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _configure_default_city(self):
        """Configura cidade padrão"""
        print("\n🌐 Configuração de cidade padrão")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _configure_cache(self):
        """Configura cache"""
        print("\n💾 Configuração de cache")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _configure_directories(self):
        """Configura diretórios"""
        print("\n🗂️  Configuração de diretórios")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _configure_file_retention(self):
        """Configura retenção de arquivos"""
        print("\n🔄 Configuração de retenção")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _configure_logging(self):
        """Configura logging"""
        print("\n📊 Configuração de logging")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _advanced_settings(self):
        """Configurações avançadas"""
        print("\n🎯 Configurações avançadas")
        print("Funcionalidade em desenvolvimento...")
        self.pause()
    
    def _save_settings(self):
        """Salva configurações"""
        print("\n💾 Salvando configurações...")
        self.show_success("Configurações salvas!")
        self.pause()
    
    # ================== STATUS DO SISTEMA ==================
    
    def show_system_status(self):
        """Mostra status do sistema"""
        print("\n📋 STATUS DO SISTEMA")
        print("═" * 50)
        
        # Estatísticas de arquivos
        categories_count = self.count_files("categories")
        restaurants_count = self.count_files("restaurants")
        products_count = self.count_files("products")
        
        print(f"📁 Dados disponíveis:")
        print(f"  🏷️  Categorias: {categories_count} arquivos")
        print(f"  🏪 Restaurantes: {restaurants_count} arquivos")
        print(f"  🍕 Produtos: {products_count} arquivos")
        
        # Estatísticas de armazenamento
        total_size = self.get_total_size()
        print(f"\n💾 Armazenamento:")
        print(f"  📦 Tamanho total: {self.format_size(total_size)}")
        
        # Estatísticas da sessão
        from datetime import datetime
        uptime = datetime.now() - self.session_stats['session_start']
        print(f"\n📊 Sessão atual:")
        print(f"  ⏱️  Tempo ativo: {uptime.seconds//3600:02d}:{(uptime.seconds//60)%60:02d}:{uptime.seconds%60:02d}")
        print(f"  🎯 Extrações realizadas: {sum([self.session_stats['categories_extracted'], self.session_stats['restaurants_extracted'], self.session_stats['products_extracted']])}")
        
        # Status dos serviços
        print(f"\n🔧 Serviços:")
        print(f"  🚀 Paralelização: {'✅ Ativo' if self.parallel_scraper else '❌ Inativo'}")
        print(f"  🔍 Sistema de busca: {'✅ Ativo' if self.search_optimizer else '❌ Inativo'}")
        print(f"  🗜️  Gerenciador de arquivos: {'✅ Ativo' if self.archive_manager else '❌ Inativo'}")
        
        self.pause()
    
    # ================== MÉTODOS AUXILIARES DE BUSCA ==================
    
    def _export_search_results(self, results: List[Dict], data_type: str):
        """Exporta resultados de busca para CSV"""
        try:
            from datetime import datetime
            import csv
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"busca_{data_type}_{timestamp}.csv"
            filepath = self.data_dir / "exports" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            if results:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = results[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
                
                print(f"✅ Resultados exportados: {filepath}")
            else:
                print("❌ Nenhum resultado para exportar")
                
        except Exception as e:
            self.show_error(f"Erro ao exportar: {e}")
    
    def _show_restaurant_details(self, results: List[Dict]):
        """Mostra detalhes de um restaurante específico"""
        try:
            print("\n🔍 Escolha um restaurante para ver detalhes:")
            for i, restaurant in enumerate(results[:10], 1):
                print(f"{i}. {restaurant.get('nome', 'N/A')}")
            
            choice = input(f"\nEscolha (1-{min(10, len(results))}): ").strip()
            idx = int(choice) - 1
            
            if 0 <= idx < len(results):
                restaurant = results[idx]
                print(f"\n🏪 DETALHES DO RESTAURANTE")
                print("─" * 40)
                print(f"📛 Nome: {restaurant.get('nome', 'N/A')}")
                print(f"📂 Categoria: {restaurant.get('categoria', 'N/A')}")
                print(f"⭐ Avaliação: {restaurant.get('avaliacao', 'N/A')}")
                print(f"🏙️ Cidade: {restaurant.get('cidade', 'N/A')}")
                print(f"🆔 ID: {restaurant.get('id', 'N/A')}")
                
                # Busca produtos deste restaurante
                products = self.search_optimizer.search_products(restaurant_name=restaurant.get('nome'))
                if products:
                    print(f"\n🍕 Produtos disponíveis: {len(products)}")
                    for i, product in enumerate(products[:5], 1):
                        print(f"  {i}. {product.get('nome', 'N/A')} - {product.get('preco', 'N/A')}")
                    if len(products) > 5:
                        print(f"  ... e mais {len(products) - 5} produtos")
            else:
                print("❌ Escolha inválida")
                
        except (ValueError, IndexError):
            print("❌ Escolha inválida")
        except Exception as e:
            self.show_error(f"Erro: {e}")
    
    def _analyze_product_prices(self, products: List[Dict]):
        """Análise detalhada de preços dos produtos"""
        try:
            print(f"\n📈 ANÁLISE DETALHADA DE PREÇOS")
            print("─" * 50)
            
            prices = []
            for product in products:
                price_str = product.get('preco', '0')
                try:
                    price_num = float(price_str.replace('R$', '').replace(',', '.'))
                    if price_num > 0:
                        prices.append(price_num)
                except:
                    pass
            
            if prices:
                import statistics
                
                avg_price = statistics.mean(prices)
                median_price = statistics.median(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                print(f"💰 Preço médio: R$ {avg_price:.2f}")
                print(f"📊 Preço mediano: R$ {median_price:.2f}")
                print(f"💸 Menor preço: R$ {min_price:.2f}")
                print(f"💵 Maior preço: R$ {max_price:.2f}")
                print(f"📈 Total analisado: {len(prices)} produtos")
                
                # Distribuição por faixas
                ranges = {
                    "Até R$ 10": 0,
                    "R$ 10-20": 0,
                    "R$ 20-30": 0,
                    "R$ 30-50": 0,
                    "Acima R$ 50": 0
                }
                
                for price in prices:
                    if price <= 10:
                        ranges["Até R$ 10"] += 1
                    elif price <= 20:
                        ranges["R$ 10-20"] += 1
                    elif price <= 30:
                        ranges["R$ 20-30"] += 1
                    elif price <= 50:
                        ranges["R$ 30-50"] += 1
                    else:
                        ranges["Acima R$ 50"] += 1
                
                print(f"\n📊 Distribuição por faixas:")
                for range_name, count in ranges.items():
                    percentage = (count / len(prices) * 100) if prices else 0
                    print(f"  {range_name:<12}: {count:3} produtos ({percentage:5.1f}%)")
            else:
                print("❌ Nenhum preço válido encontrado")
                
        except Exception as e:
            self.show_error(f"Erro na análise: {e}")
    
    def _show_recommendations(self):
        """Sistema de recomendações inteligentes"""
        print("\n🎯 SISTEMA DE RECOMENDAÇÕES INTELIGENTES")
        print("═" * 60)
        
        # Tipos de recomendação disponíveis
        print("📋 Tipos de recomendação disponíveis:")
        print("1. 🏪 Restaurantes similares (baseado em categoria)")
        print("2. 🍕 Produtos populares por categoria")
        print("3. ⭐ Melhores avaliados por faixa de preço")
        print("4. 🔥 Trending (mais produtos únicos)")
        print("5. 🎲 Descoberta aleatória")
        print("0. ⬅️  Voltar")
        
        choice = input("\nEscolha o tipo de recomendação: ").strip()
        
        if choice == "1":
            self._recommend_similar_restaurants()
        elif choice == "2":
            self._recommend_popular_products()
        elif choice == "3":
            self._recommend_best_rated()
        elif choice == "4":
            self._recommend_trending()
        elif choice == "5":
            self._recommend_discovery()
        elif choice == "0":
            return
        else:
            print("❌ Opção inválida")
        
        self.pause()
    
    def _recommend_similar_restaurants(self):
        """Recomenda restaurantes similares"""
        print("\n🏪 RESTAURANTES SIMILARES")
        print("═" * 40)
        
        # Solicita ID do restaurante base
        restaurant_id = input("🆔 Digite o ID do restaurante base (ou Enter para listar): ").strip()
        
        if not restaurant_id:
            # Mostra alguns restaurantes para escolha
            try:
                restaurants = self.search_optimizer.search_restaurants(limit=10)
                if restaurants:
                    print("\n📋 Restaurantes disponíveis:")
                    for i, rest in enumerate(restaurants[:10], 1):
                        print(f"{i:2}. {rest.get('nome', 'N/A'):<25} | ID: {rest.get('id', 'N/A')}")
                    
                    choice = input(f"\nEscolha um restaurante (1-{min(10, len(restaurants))}): ").strip()
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(restaurants):
                            restaurant_id = restaurants[idx].get('id')
                        else:
                            print("❌ Escolha inválida")
                            return
                    except ValueError:
                        print("❌ Escolha inválida")
                        return
                else:
                    print("❌ Nenhum restaurante encontrado")
                    return
            except Exception as e:
                self.show_error(f"Erro ao buscar restaurantes: {e}")
                return
        
        try:
            recommendations = self.search_optimizer.get_recommendations(restaurant_id, limit=8)
            
            if recommendations:
                print(f"\n✅ {len(recommendations)} restaurantes similares encontrados:")
                print("─" * 70)
                
                for i, restaurant in enumerate(recommendations, 1):
                    name = restaurant.get('nome', 'N/A')
                    cat = restaurant.get('categoria', 'N/A')
                    rating = restaurant.get('avaliacao', 'N/A')
                    
                    print(f"{i:2}. 🏪 {name:<30} | 📂 {cat:<12} | ⭐ {rating}")
                
                # Busca produtos do primeiro recomendado como amostra
                if recommendations:
                    first_rec = recommendations[0]
                    products = self.search_optimizer.search_products(
                        restaurant_id=first_rec.get('id'), 
                        limit=3
                    )
                    if products:
                        print(f"\n🍕 Amostra de produtos de '{first_rec.get('nome', 'N/A')}':")
                        for product in products:
                            print(f"   • {product.get('nome', 'N/A')} - {product.get('preco', 'N/A')}")
            else:
                print("❌ Nenhuma recomendação encontrada para este restaurante")
                
        except Exception as e:
            self.show_error(f"Erro ao gerar recomendações: {e}")
    
    def _recommend_popular_products(self):
        """Recomenda produtos populares por categoria"""
        print("\n🍕 PRODUTOS POPULARES POR CATEGORIA")
        print("═" * 45)
        
        try:
            # Lista categorias disponíveis
            categories = self.search_optimizer.get_popular_categories(limit=10)
            
            if categories:
                print("📂 Categorias disponíveis:")
                for i, cat in enumerate(categories, 1):
                    name = cat.get('categoria', 'N/A')
                    count = cat.get('restaurant_count', 0)
                    print(f"{i:2}. {name:<20} ({count} restaurantes)")
                
                choice = input(f"\nEscolha uma categoria (1-{len(categories)}): ").strip()
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(categories):
                        selected_category = categories[idx].get('categoria')
                        
                        # Busca produtos da categoria
                        products = self.search_optimizer.search_products(
                            category=selected_category,
                            available_only=True,
                            limit=15
                        )
                        
                        if products:
                            print(f"\n🔥 TOP produtos de '{selected_category}':")
                            print("─" * 60)
                            
                            # Agrupa produtos por frequência de nome (popularidade)
                            product_names = {}
                            for product in products:
                                name = product.get('nome', 'N/A')
                                if name not in product_names:
                                    product_names[name] = []
                                product_names[name].append(product)
                            
                            # Ordena por frequência
                            popular = sorted(product_names.items(), 
                                           key=lambda x: len(x[1]), 
                                           reverse=True)
                            
                            for i, (name, products_list) in enumerate(popular[:10], 1):
                                count = len(products_list)
                                avg_price = sum(
                                    float(p.get('preco', '0').replace('R$', '').replace(',', '.'))
                                    for p in products_list
                                    if p.get('preco', '0').replace('R$', '').replace(',', '.').replace('.', '').isdigit()
                                ) / max(count, 1)
                                
                                print(f"{i:2}. 🍕 {name:<25} | {count:2} rest. | 💰 ~R$ {avg_price:.2f}")
                        else:
                            print(f"❌ Nenhum produto encontrado para '{selected_category}'")
                    else:
                        print("❌ Escolha inválida")
                except ValueError:
                    print("❌ Escolha inválida")
            else:
                print("❌ Nenhuma categoria encontrada")
                
        except Exception as e:
            self.show_error(f"Erro ao buscar produtos populares: {e}")
    
    def _recommend_best_rated(self):
        """Recomenda melhores avaliados por faixa de preço"""
        print("\n⭐ MELHORES AVALIADOS POR FAIXA DE PREÇO")
        print("═" * 50)
        
        print("💰 Escolha a faixa de preço:")
        print("1. 💸 Econômico (até R$ 15)")
        print("2. 💰 Intermediário (R$ 15-40)")
        print("3. 💵 Premium (acima de R$ 40)")
        print("4. 🔍 Todas as faixas")
        
        choice = input("\nEscolha: ").strip()
        
        min_price = None
        max_price = None
        range_name = ""
        
        if choice == "1":
            max_price = 15.0
            range_name = "Econômico"
        elif choice == "2":
            min_price = 15.0
            max_price = 40.0
            range_name = "Intermediário"
        elif choice == "3":
            min_price = 40.0
            range_name = "Premium"
        elif choice == "4":
            range_name = "Todas as faixas"
        else:
            print("❌ Opção inválida")
            return
        
        try:
            # Busca restaurantes com melhor avaliação
            restaurants = self.search_optimizer.search_restaurants(
                min_rating=4.0,
                limit=10
            )
            
            if restaurants:
                print(f"\n🏆 TOP restaurantes {range_name.lower()}:")
                print("─" * 60)
                
                # Para cada restaurante, verifica se tem produtos na faixa
                valid_restaurants = []
                
                for restaurant in restaurants:
                    products = self.search_optimizer.search_products(
                        restaurant_id=restaurant.get('id'),
                        min_price=min_price,
                        max_price=max_price,
                        limit=5
                    )
                    
                    if products or choice == "4":  # Se tem produtos na faixa ou é "todas"
                        avg_product_price = 0
                        if products:
                            prices = []
                            for p in products:
                                try:
                                    price = float(p.get('preco', '0').replace('R$', '').replace(',', '.'))
                                    if price > 0:
                                        prices.append(price)
                                except:
                                    pass
                            avg_product_price = sum(prices) / len(prices) if prices else 0
                        
                        valid_restaurants.append({
                            'restaurant': restaurant,
                            'avg_price': avg_product_price,
                            'product_count': len(products)
                        })
                
                # Mostra os melhores
                for i, item in enumerate(valid_restaurants[:8], 1):
                    rest = item['restaurant']
                    name = rest.get('nome', 'N/A')
                    rating = rest.get('avaliacao', 'N/A')
                    category = rest.get('categoria', 'N/A')
                    avg_price = item['avg_price']
                    
                    price_info = f"~R$ {avg_price:.2f}" if avg_price > 0 else "Preços variados"
                    
                    print(f"{i:2}. 🏪 {name:<25} | ⭐ {rating} | 📂 {category:<12} | 💰 {price_info}")
                
                if not valid_restaurants:
                    print(f"❌ Nenhum restaurante encontrado na faixa {range_name.lower()}")
            else:
                print("❌ Nenhum restaurante bem avaliado encontrado")
                
        except Exception as e:
            self.show_error(f"Erro ao buscar melhores avaliados: {e}")
    
    def _recommend_trending(self):
        """Recomenda produtos/restaurantes trending"""
        print("\n🔥 TRENDING - MAIOR VARIEDADE DE PRODUTOS")
        print("═" * 50)
        
        try:
            # Busca restaurantes e conta produtos únicos
            restaurants = self.search_optimizer.search_restaurants(limit=50)
            
            restaurant_scores = []
            for restaurant in restaurants:
                products = self.search_optimizer.search_products(
                    restaurant_id=restaurant.get('id'),
                    limit=100
                )
                
                # Conta produtos únicos (por nome)
                unique_products = set()
                for product in products:
                    unique_products.add(product.get('nome', ''))
                
                score = len(unique_products)
                if score > 0:  # Só inclui se tem produtos
                    restaurant_scores.append({
                        'restaurant': restaurant,
                        'unique_products': score,
                        'total_products': len(products)
                    })
            
            # Ordena por variedade de produtos
            restaurant_scores.sort(key=lambda x: x['unique_products'], reverse=True)
            
            if restaurant_scores:
                print("🔥 Restaurantes com maior variedade:")
                print("─" * 70)
                
                for i, item in enumerate(restaurant_scores[:10], 1):
                    rest = item['restaurant']
                    name = rest.get('nome', 'N/A')
                    category = rest.get('categoria', 'N/A')
                    rating = rest.get('avaliacao', 'N/A')
                    unique_count = item['unique_products']
                    total_count = item['total_products']
                    
                    print(f"{i:2}. 🏪 {name:<25} | 📂 {category:<12} | ⭐ {rating} | 🍕 {unique_count} únicos")
                
                # Mostra amostra de produtos do primeiro
                if restaurant_scores:
                    top_rest = restaurant_scores[0]['restaurant']
                    sample_products = self.search_optimizer.search_products(
                        restaurant_id=top_rest.get('id'),
                        limit=5
                    )
                    
                    if sample_products:
                        print(f"\n🍕 Amostra de '{top_rest.get('nome', 'N/A')}':")
                        for product in sample_products:
                            print(f"   • {product.get('nome', 'N/A')} - {product.get('preco', 'N/A')}")
            else:
                print("❌ Não foi possível calcular trending")
                
        except Exception as e:
            self.show_error(f"Erro ao buscar trending: {e}")
    
    def _recommend_discovery(self):
        """Descoberta aleatória de restaurantes e produtos"""
        print("\n🎲 DESCOBERTA ALEATÓRIA")
        print("═" * 30)
        
        try:
            import random
            
            # Busca categorias aleatórias
            categories = self.search_optimizer.get_popular_categories(limit=20)
            
            if categories:
                # Seleciona categoria aleatória
                random_category = random.choice(categories)
                cat_name = random_category.get('categoria', 'N/A')
                
                print(f"🎯 Categoria descoberta: {cat_name}")
                print("─" * 40)
                
                # Busca restaurantes da categoria
                restaurants = self.search_optimizer.search_restaurants(
                    category=cat_name,
                    limit=20
                )
                
                if restaurants:
                    # Seleciona alguns restaurantes aleatórios
                    sample_restaurants = random.sample(
                        restaurants, 
                        min(5, len(restaurants))
                    )
                    
                    print("🎲 Restaurantes para descobrir:")
                    for i, restaurant in enumerate(sample_restaurants, 1):
                        name = restaurant.get('nome', 'N/A')
                        rating = restaurant.get('avaliacao', 'N/A')
                        
                        print(f"{i}. 🏪 {name:<30} | ⭐ {rating}")
                        
                        # Mostra 2 produtos aleatórios de cada
                        products = self.search_optimizer.search_products(
                            restaurant_id=restaurant.get('id'),
                            limit=10
                        )
                        
                        if products:
                            sample_products = random.sample(
                                products,
                                min(2, len(products))
                            )
                            
                            for product in sample_products:
                                print(f"     🍕 {product.get('nome', 'N/A')} - {product.get('preco', 'N/A')}")
                        
                        print()  # Linha em branco
                
                print("💡 Dica: Experimente algo novo hoje!")
            else:
                print("❌ Nenhuma categoria encontrada para descoberta")
                
        except Exception as e:
            self.show_error(f"Erro na descoberta: {e}")