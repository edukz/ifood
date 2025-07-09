#!/usr/bin/env python3
"""
Menus de Análise - Categorização e Monitoramento de Preços
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.utils.product_categorizer import ProductCategorizer
from src.ui.base_menu import BaseMenu


class AnalysisMenus(BaseMenu):
    """Menus para análise de dados"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path,
                 product_categorizer: ProductCategorizer):
        super().__init__("Análise", session_stats, data_dir)
        self.product_categorizer = product_categorizer
    
    # ================== CATEGORIZAÇÃO AUTOMÁTICA ==================
    
    def menu_product_categorizer(self):
        """Menu de categorização automática"""
        options = [
            "1. 📁 Categorizar arquivo CSV",
            "2. 🧪 Testar produto individual",
            "3. 📊 Analisar distribuição de categorias",
            "4. 📋 Criar relatório de categorização",
            "5. ⚙️  Gerenciar categorias",
            "6. 📈 Ver estatísticas"
        ]
        
        self.show_menu("🤖 CATEGORIZAÇÃO AUTOMÁTICA", options)
        choice = self.get_user_choice(6)
        
        if choice == "1":
            self._categorize_csv_file()
        elif choice == "2":
            self._test_product_categorization()
        elif choice == "3":
            self._analyze_category_distribution()
        elif choice == "4":
            self._create_categorization_report()
        elif choice == "5":
            self._manage_categories()
        elif choice == "6":
            self._show_categorization_stats()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _categorize_csv_file(self):
        """Categoriza produtos de arquivo CSV"""
        print("\n📁 Categorização de arquivo CSV")
        file_path = input("Caminho do arquivo CSV: ").strip()
        
        if not file_path:
            self.show_error("Caminho não informado!")
            return
        
        try:
            csv_path = self.find_file(file_path, ["products"])
            if not csv_path:
                self.show_error("Arquivo não encontrado!")
                return
            
            print(f"\n🔄 Categorizando produtos de {csv_path.name}...")
            result = self.product_categorizer.categorize_csv_file(csv_path)
            
            self.session_stats['products_categorized'] += result['products_processed']
            
            self.show_success("Categorização concluída!")
            print(f"Produtos processados: {result['products_processed']}")
            print(f"Arquivo salvo: {Path(result['output_file']).name}")
            
            # Mostra estatísticas
            stats = result['statistics']
            print(f"\n📊 Estatísticas:")
            print(f"  Alta confiança: {stats['high_confidence_matches']}")
            print(f"  Média confiança: {stats['low_confidence_matches']}")
            print(f"  Sem correspondência: {stats['no_match_found']}")
            
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _test_product_categorization(self):
        """Testa categorização de produto individual"""
        print("\n🧪 Teste de categorização individual")
        
        product_name = input("Nome do produto: ").strip()
        if not product_name:
            self.show_error("Nome não informado!")
            return
        
        description = input("Descrição (opcional): ").strip()
        
        result = self.product_categorizer.categorize_product(product_name, description)
        
        print(f"\n🎯 Resultado da categorização:")
        print(f"Produto: {result.product_name}")
        print(f"Categoria sugerida: {result.suggested_category}")
        print(f"Confiança: {result.confidence:.2f} ({result.confidence*100:.0f}%)")
        if result.keywords_found:
            print(f"Palavras-chave: {', '.join(result.keywords_found[:5])}")
        if result.reasoning:
            print(f"Justificativa: {result.reasoning[0]}")
        
        self.pause()
    
    def _analyze_category_distribution(self):
        """Analisa distribuição de categorias"""
        print("\n📊 Análise de distribuição de categorias")
        file_path = input("Arquivo categorizado: ").strip()
        
        try:
            csv_path = self.find_file(file_path, ["products"])
            if not csv_path:
                self.show_error("Arquivo não encontrado!")
                return
            
            analysis = self.product_categorizer.analyze_category_distribution(csv_path)
            
            print(f"\n📈 Análise de {analysis['total_products']} produtos:")
            
            print("\nTop 10 categorias sugeridas:")
            for i, (category, count) in enumerate(list(analysis['suggested_categories'].items())[:10], 1):
                percentage = (count / analysis['total_products']) * 100
                print(f"  {i:2d}. {category:<20} {count:>4} ({percentage:5.1f}%)")
            
            print("\nDistribuição de confiança:")
            conf = analysis['confidence_distribution']
            total = sum(conf.values())
            print(f"  Alta (≥80%): {conf['high']:>4} ({conf['high']/total*100:5.1f}%)")
            print(f"  Média (50-79%): {conf['medium']:>4} ({conf['medium']/total*100:5.1f}%)")
            print(f"  Baixa (<50%): {conf['low']:>4} ({conf['low']/total*100:5.1f}%)")
            
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _create_categorization_report(self):
        """Cria relatório detalhado de categorização"""
        print("\n📋 Criação de relatório")
        file_path = input("Arquivo categorizado: ").strip()
        
        try:
            csv_path = self.find_file(file_path, ["products"])
            if not csv_path:
                self.show_error("Arquivo não encontrado!")
                return
            
            report_path = self.product_categorizer.create_category_report(csv_path)
            self.show_success(f"Relatório criado: {report_path.name}")
            
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _manage_categories(self):
        """Gerencia categorias do sistema"""
        print("\n⚙️  Gerenciamento de categorias")
        print("1. Listar categorias disponíveis")
        print("2. Salvar configurações")
        print("3. Ver detalhes de categoria")
        
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            print(f"\n📋 {len(self.product_categorizer.categories)} categorias disponíveis:")
            for i, (cat_id, category) in enumerate(self.product_categorizer.categories.items(), 1):
                print(f"{i:2d}. {category.name} ({len(category.keywords)} palavras-chave)")
        
        elif choice == "2":
            self.product_categorizer.save_config()
            self.show_success("Configurações salvas!")
        
        elif choice == "3":
            cat_name = input("Nome da categoria: ").strip().lower()
            found = None
            for cat_id, category in self.product_categorizer.categories.items():
                if cat_id == cat_name or category.name.lower() == cat_name:
                    found = category
                    break
            
            if found:
                print(f"\n📋 Detalhes de '{found.name}':")
                print(f"ID: {cat_id}")
                print(f"Palavras-chave: {', '.join(found.keywords[:10])}")
                if len(found.keywords) > 10:
                    print(f"... e mais {len(found.keywords) - 10} palavras")
            else:
                self.show_error("Categoria não encontrada!")
        
        self.pause()
    
    def _show_categorization_stats(self):
        """Mostra estatísticas do categorizador"""
        stats = self.product_categorizer.get_statistics()
        
        print("\n📈 Estatísticas do categorizador:")
        for key, value in stats['stats'].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nCategorias disponíveis: {stats['categories_available']}")
        print("Nomes das categorias:")
        for name in stats['category_names']:
            print(f"  • {name}")
        
        self.pause()
    
    # ================== MONITORAMENTO DE PREÇOS [REMOVIDO] ==================
    
    def menu_price_monitor(self):
        """Menu de monitoramento de preços [REMOVIDO]"""
        self.show_error("Funcionalidade de monitoramento de preços foi removida do sistema")
        self.pause()