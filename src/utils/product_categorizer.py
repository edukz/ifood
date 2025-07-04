#!/usr/bin/env python3
"""
Sistema de Categorização Automática de Produtos
Classifica produtos automaticamente em categorias usando IA e regras
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import csv
from collections import Counter, defaultdict

from src.utils.logger import setup_logger
from src.config.settings import SETTINGS


@dataclass
class ProductCategory:
    """Representa uma categoria de produto"""
    id: str
    name: str
    keywords: List[str]
    patterns: List[str]
    parent_category: Optional[str] = None
    confidence_threshold: float = 0.7


@dataclass
class CategoryResult:
    """Resultado da categorização de um produto"""
    product_id: str
    product_name: str
    original_category: str
    suggested_category: str
    confidence: float
    reasoning: List[str]
    keywords_found: List[str]


class ProductCategorizer:
    """Sistema inteligente de categorização de produtos"""
    
    def __init__(self, config_path: Path = None):
        self.logger = setup_logger("ProductCategorizer")
        self.config_path = config_path or Path("config/categories_config.json")
        self.categories = {}
        self.category_hierarchy = {}
        
        # Estatísticas
        self.stats = {
            'products_analyzed': 0,
            'categories_suggested': 0,
            'high_confidence_matches': 0,
            'low_confidence_matches': 0,
            'no_match_found': 0
        }
        
        self._load_default_categories()
        self._load_config()
    
    def _load_default_categories(self):
        """Carrega categorias padrão baseadas no iFood"""
        default_categories = {
            # Principais
            'bebidas': ProductCategory(
                id='bebidas',
                name='Bebidas',
                keywords=['bebida', 'suco', 'refrigerante', 'água', 'drink', 'cerveja', 'vinho', 'café', 'chá', 'smoothie', 'milk shake', 'vitamina'],
                patterns=[r'\b(coca|pepsi|fanta|guaraná|sprite)\b', r'\b(água|suco|café|chá)\b', r'\bmilk\s*shake\b']
            ),
            
            'pizza': ProductCategory(
                id='pizza',
                name='Pizza',
                keywords=['pizza', 'marguerita', 'calabresa', 'portuguesa', 'quatro queijos', 'pepperoni', 'mussarela'],
                patterns=[r'\bpizza\b', r'\b(marguerita|calabresa|portuguesa)\b']
            ),
            
            'hamburguer': ProductCategory(
                id='hamburguer',
                name='Hambúrguer',
                keywords=['hambúrguer', 'burger', 'sanduíche', 'x-bacon', 'x-tudo', 'big mac', 'whopper'],
                patterns=[r'\bhamb[uú]rguer\b', r'\bburger\b', r'\bx-\w+\b', r'\bsandu[íi]che\b']
            ),
            
            'sushi': ProductCategory(
                id='sushi',
                name='Sushi/Japonês',
                keywords=['sushi', 'sashimi', 'temaki', 'uramaki', 'hossomaki', 'nigiri', 'tempurá', 'yakisoba', 'sake'],
                patterns=[r'\b(sushi|sashimi|temaki|uramaki|hossomaki|nigiri)\b', r'\btempurá\b', r'\byakisoba\b']
            ),
            
            'doces': ProductCategory(
                id='doces',
                name='Doces e Sobremesas',
                keywords=['doce', 'sobremesa', 'bolo', 'torta', 'pudim', 'mousse', 'sorvete', 'açaí', 'chocolate', 'brigadeiro', 'beijinho'],
                patterns=[r'\b(bolo|torta|pudim|mousse|sorvete|açaí)\b', r'\b(brigadeiro|beijinho|chocolate)\b']
            ),
            
            'massas': ProductCategory(
                id='massas',
                name='Massas',
                keywords=['massa', 'macarrão', 'espaguete', 'lasanha', 'nhoque', 'ravioli', 'talharim', 'penne', 'carbonara'],
                patterns=[r'\b(massa|macarrão|espaguete|lasanha|nhoque)\b', r'\b(ravioli|talharim|penne)\b']
            ),
            
            'carnes': ProductCategory(
                id='carnes',
                name='Carnes',
                keywords=['carne', 'bife', 'frango', 'peixe', 'porco', 'costela', 'picanha', 'alcatra', 'filé', 'linguiça'],
                patterns=[r'\b(carne|bife|frango|peixe|porco)\b', r'\b(costela|picanha|alcatra|filé)\b']
            ),
            
            'saladas': ProductCategory(
                id='saladas',
                name='Saladas',
                keywords=['salada', 'verdura', 'legume', 'alface', 'tomate', 'pepino', 'rúcula', 'agrião', 'vegetariano'],
                patterns=[r'\bsalada\b', r'\b(verdura|legume|vegetariano)\b']
            ),
            
            'lanches': ProductCategory(
                id='lanches',
                name='Lanches',
                keywords=['lanche', 'coxinha', 'pastel', 'esfirra', 'empada', 'pão de açúcar', 'hot dog', 'cachorro quente'],
                patterns=[r'\blanche\b', r'\b(coxinha|pastel|esfirra|empada)\b', r'\bhot\s*dog\b']
            ),
            
            'acompanhamentos': ProductCategory(
                id='acompanhamentos',
                name='Acompanhamentos',
                keywords=['acompanhamento', 'batata frita', 'arroz', 'feijão', 'farofa', 'purê', 'polenta', 'mandioca'],
                patterns=[r'\bacompanhamento\b', r'\bbatata\s*frita\b', r'\b(arroz|feijão|farofa|purê)\b']
            )
        }
        
        self.categories = default_categories
    
    def _load_config(self):
        """Carrega configurações personalizadas se existirem"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Atualiza categorias com configurações personalizadas
                for cat_id, cat_data in config.get('categories', {}).items():
                    if cat_id in self.categories:
                        # Atualiza categoria existente
                        category = self.categories[cat_id]
                        category.keywords.extend(cat_data.get('additional_keywords', []))
                        category.patterns.extend(cat_data.get('additional_patterns', []))
                    else:
                        # Cria nova categoria
                        self.categories[cat_id] = ProductCategory(
                            id=cat_id,
                            name=cat_data['name'],
                            keywords=cat_data['keywords'],
                            patterns=cat_data.get('patterns', []),
                            confidence_threshold=cat_data.get('confidence_threshold', 0.7)
                        )
                        
                self.logger.info(f"Configurações carregadas de {self.config_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao carregar config: {e}")
    
    def save_config(self):
        """Salva configurações atuais"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'categories': {},
            'last_updated': datetime.now().isoformat()
        }
        
        for cat_id, category in self.categories.items():
            config['categories'][cat_id] = {
                'name': category.name,
                'keywords': category.keywords,
                'patterns': category.patterns,
                'confidence_threshold': category.confidence_threshold
            }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Configurações salvas em {self.config_path}")
    
    def categorize_product(self, product_name: str, product_description: str = "", 
                          original_category: str = "") -> CategoryResult:
        """Categoriza um produto individual"""
        self.stats['products_analyzed'] += 1
        
        # Limpa e normaliza texto
        text = self._normalize_text(f"{product_name} {product_description}")
        
        # Analisa cada categoria
        category_scores = {}
        found_keywords = {}
        
        for cat_id, category in self.categories.items():
            score, keywords = self._calculate_category_score(text, category)
            if score > 0:
                category_scores[cat_id] = score
                found_keywords[cat_id] = keywords
        
        # Determina melhor categoria
        if not category_scores:
            self.stats['no_match_found'] += 1
            return CategoryResult(
                product_id="",
                product_name=product_name,
                original_category=original_category,
                suggested_category="outros",
                confidence=0.0,
                reasoning=["Nenhuma categoria específica identificada"],
                keywords_found=[]
            )
        
        # Categoria com maior score
        best_category = max(category_scores.items(), key=lambda x: x[1])
        cat_id, confidence = best_category
        
        # Estatísticas
        if confidence >= 0.8:
            self.stats['high_confidence_matches'] += 1
        elif confidence >= 0.5:
            self.stats['low_confidence_matches'] += 1
        else:
            self.stats['no_match_found'] += 1
        
        self.stats['categories_suggested'] += 1
        
        return CategoryResult(
            product_id="",
            product_name=product_name,
            original_category=original_category,
            suggested_category=self.categories[cat_id].name,
            confidence=confidence,
            reasoning=self._generate_reasoning(cat_id, confidence, found_keywords.get(cat_id, [])),
            keywords_found=found_keywords.get(cat_id, [])
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para análise"""
        if not text:
            return ""
        
        # Converte para minúsculo
        text = text.lower()
        
        # Remove acentos
        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i', 'î': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'û': 'u',
            'ç': 'c'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove caracteres especiais mantendo espaços
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_category_score(self, text: str, category: ProductCategory) -> Tuple[float, List[str]]:
        """Calcula score de uma categoria para um texto"""
        score = 0.0
        found_keywords = []
        
        # Verifica palavras-chave
        for keyword in category.keywords:
            normalized_keyword = self._normalize_text(keyword)
            if normalized_keyword in text:
                # Peso baseado no tamanho da palavra-chave
                weight = len(normalized_keyword.split()) * 0.2
                score += weight
                found_keywords.append(keyword)
        
        # Verifica padrões regex
        for pattern in category.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += len(matches) * 0.3
                found_keywords.extend(matches)
        
        # Normaliza score (0-1)
        max_possible_score = len(category.keywords) * 0.2 + len(category.patterns) * 0.3
        if max_possible_score > 0:
            score = min(score / max_possible_score, 1.0)
        
        return score, found_keywords
    
    def _generate_reasoning(self, category_id: str, confidence: float, keywords: List[str]) -> List[str]:
        """Gera explicação da categorização"""
        reasoning = []
        
        category_name = self.categories[category_id].name
        
        if confidence >= 0.8:
            reasoning.append(f"Alta confiança para '{category_name}'")
        elif confidence >= 0.5:
            reasoning.append(f"Confiança moderada para '{category_name}'")
        else:
            reasoning.append(f"Baixa confiança para '{category_name}'")
        
        if keywords:
            reasoning.append(f"Palavras-chave encontradas: {', '.join(keywords[:3])}")
        
        return reasoning
    
    def categorize_csv_file(self, csv_path: Path, output_path: Path = None) -> Dict[str, Any]:
        """Categoriza produtos de um arquivo CSV"""
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
        
        output_path = output_path or csv_path.parent / f"categorized_{csv_path.name}"
        
        results = []
        processed_count = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    product_name = row.get('nome', '')
                    description = row.get('descricao', '')
                    original_category = row.get('categoria_produto', '')
                    
                    if not product_name:
                        continue
                    
                    result = self.categorize_product(product_name, description, original_category)
                    result.product_id = row.get('id', f"product_{processed_count}")
                    
                    # Adiciona resultado ao CSV original
                    row['categoria_sugerida'] = result.suggested_category
                    row['confianca_categorizacao'] = f"{result.confidence:.2f}"
                    row['palavras_chave_encontradas'] = "; ".join(result.keywords_found)
                    row['categoria_original'] = original_category
                    
                    results.append(row)
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        self.logger.info(f"Processados {processed_count} produtos...")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar CSV: {e}")
            raise
        
        # Salva arquivo categorizado
        if results:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        self.logger.info(f"Categorização concluída: {processed_count} produtos processados")
        self.logger.info(f"Arquivo salvo em: {output_path}")
        
        return {
            'input_file': str(csv_path),
            'output_file': str(output_path),
            'products_processed': processed_count,
            'statistics': self.stats.copy()
        }
    
    def analyze_category_distribution(self, csv_path: Path) -> Dict[str, Any]:
        """Analisa distribuição de categorias em um arquivo"""
        original_categories = Counter()
        suggested_categories = Counter()
        confidence_distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                orig_cat = row.get('categoria_original', 'N/A')
                sugg_cat = row.get('categoria_sugerida', 'N/A')
                confidence = float(row.get('confianca_categorizacao', 0))
                
                original_categories[orig_cat] += 1
                suggested_categories[sugg_cat] += 1
                
                if confidence >= 0.8:
                    confidence_distribution['high'] += 1
                elif confidence >= 0.5:
                    confidence_distribution['medium'] += 1
                else:
                    confidence_distribution['low'] += 1
        
        return {
            'original_categories': dict(original_categories.most_common()),
            'suggested_categories': dict(suggested_categories.most_common()),
            'confidence_distribution': confidence_distribution,
            'total_products': sum(original_categories.values())
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do categorizador"""
        return {
            'stats': self.stats.copy(),
            'categories_available': len(self.categories),
            'category_names': [cat.name for cat in self.categories.values()]
        }
    
    def create_category_report(self, csv_path: Path, report_path: Path = None) -> Path:
        """Cria relatório detalhado de categorização"""
        report_path = report_path or csv_path.parent / f"category_report_{csv_path.stem}.txt"
        
        analysis = self.analyze_category_distribution(csv_path)
        stats = self.get_statistics()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RELATÓRIO DE CATEGORIZAÇÃO AUTOMÁTICA\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Arquivo analisado: {csv_path.name}\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de produtos: {analysis['total_products']}\n\n")
            
            f.write("DISTRIBUIÇÃO DE CONFIANÇA:\n")
            f.write("-" * 30 + "\n")
            conf_dist = analysis['confidence_distribution']
            f.write(f"Alta confiança (≥80%): {conf_dist['high']}\n")
            f.write(f"Média confiança (50-79%): {conf_dist['medium']}\n")
            f.write(f"Baixa confiança (<50%): {conf_dist['low']}\n\n")
            
            f.write("TOP 10 CATEGORIAS SUGERIDAS:\n")
            f.write("-" * 30 + "\n")
            for i, (category, count) in enumerate(list(analysis['suggested_categories'].items())[:10], 1):
                percentage = (count / analysis['total_products']) * 100
                f.write(f"{i:2d}. {category:<20} {count:>5} ({percentage:5.1f}%)\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("ESTATÍSTICAS DO SISTEMA:\n")
            f.write("=" * 60 + "\n")
            for key, value in stats['stats'].items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        
        self.logger.info(f"Relatório criado: {report_path}")
        return report_path


def create_categorization_cli():
    """Interface CLI para categorização"""
    categorizer = ProductCategorizer()
    
    print("\n" + "=" * 60)
    print("SISTEMA DE CATEGORIZAÇÃO AUTOMÁTICA")
    print("=" * 60)
    
    while True:
        print("\nOpções:")
        print("1. Categorizar arquivo CSV")
        print("2. Analisar distribuição de categorias")
        print("3. Criar relatório detalhado")
        print("4. Testar categorização de produto")
        print("5. Ver estatísticas")
        print("6. Gerenciar categorias")
        print("0. Sair")
        
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            file_path = input("Caminho do arquivo CSV: ").strip()
            try:
                csv_path = Path(file_path)
                result = categorizer.categorize_csv_file(csv_path)
                print(f"\n✅ Categorização concluída!")
                print(f"Produtos processados: {result['products_processed']}")
                print(f"Arquivo salvo: {result['output_file']}")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        elif choice == "2":
            file_path = input("Caminho do arquivo categorizado: ").strip()
            try:
                analysis = categorizer.analyze_category_distribution(Path(file_path))
                print(f"\n📊 Análise de {analysis['total_products']} produtos:")
                print("\nTop categorias sugeridas:")
                for cat, count in list(analysis['suggested_categories'].items())[:5]:
                    print(f"  {cat}: {count}")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        elif choice == "3":
            file_path = input("Caminho do arquivo categorizado: ").strip()
            try:
                report_path = categorizer.create_category_report(Path(file_path))
                print(f"✅ Relatório criado: {report_path}")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        elif choice == "4":
            product_name = input("Nome do produto: ").strip()
            description = input("Descrição (opcional): ").strip()
            
            result = categorizer.categorize_product(product_name, description)
            print(f"\n🎯 Resultado da categorização:")
            print(f"Produto: {result.product_name}")
            print(f"Categoria sugerida: {result.suggested_category}")
            print(f"Confiança: {result.confidence:.2f}")
            print(f"Palavras-chave: {', '.join(result.keywords_found)}")
        
        elif choice == "5":
            stats = categorizer.get_statistics()
            print(f"\n📈 Estatísticas do sistema:")
            for key, value in stats['stats'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            print(f"  Categorias disponíveis: {stats['categories_available']}")
        
        elif choice == "6":
            print("\n⚙️ Gerenciamento de categorias:")
            print("1. Listar categorias")
            print("2. Adicionar categoria")
            print("3. Salvar configurações")
            
            sub_choice = input("Escolha: ").strip()
            
            if sub_choice == "1":
                print("\n📋 Categorias disponíveis:")
                for i, (cat_id, category) in enumerate(categorizer.categories.items(), 1):
                    print(f"{i:2d}. {category.name} ({len(category.keywords)} palavras-chave)")
            
            elif sub_choice == "2":
                print("\n➕ Nova categoria")
                print("Funcionalidade em desenvolvimento...")
            
            elif sub_choice == "3":
                categorizer.save_config()
                print("✅ Configurações salvas!")
        
        elif choice == "0":
            break
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    create_categorization_cli()