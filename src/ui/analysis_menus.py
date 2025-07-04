#!/usr/bin/env python3
"""
Menus de Análise - Categorização e Monitoramento de Preços
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.utils.product_categorizer import ProductCategorizer
from src.utils.price_monitor import PriceMonitor
from .base_menu import BaseMenu


class AnalysisMenus(BaseMenu):
    """Menus para análise de dados"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path,
                 product_categorizer: ProductCategorizer, price_monitor: PriceMonitor):
        super().__init__("Análise", session_stats, data_dir)
        self.product_categorizer = product_categorizer
        self.price_monitor = price_monitor
    
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
    
    # ================== MONITORAMENTO DE PREÇOS ==================
    
    def menu_price_monitor(self):
        """Menu de monitoramento de preços"""
        options = [
            "1. 📥 Importar produtos de CSV",
            "2. 📈 Ver histórico de preços",
            "3. 📊 Ver mudanças de preços",
            "4. 🚨 Ver alertas de preços",
            "5. 💎 Encontrar melhores ofertas",
            "6. 📋 Gerar relatório de preços",
            "7. 📊 Estatísticas de produto",
            "8. ⚙️  Configurar alertas"
        ]
        
        self.show_menu("💰 MONITORAMENTO DE PREÇOS", options)
        choice = self.get_user_choice(8)
        
        if choice == "1":
            self._import_products_for_monitoring()
        elif choice == "2":
            self._view_price_history()
        elif choice == "3":
            self._view_price_changes()
        elif choice == "4":
            self._view_price_alerts()
        elif choice == "5":
            self._find_best_deals()
        elif choice == "6":
            self._generate_price_report()
        elif choice == "7":
            self._view_product_price_stats()
        elif choice == "8":
            self._configure_price_alerts()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _import_products_for_monitoring(self):
        """Importa produtos para monitoramento de preços"""
        print("\n📥 Importação de produtos para monitoramento")
        file_path = input("Caminho do arquivo CSV: ").strip()
        
        try:
            csv_path = self.find_file(file_path, ["products"])
            if not csv_path:
                self.show_error("Arquivo não encontrado!")
                return
            
            print(f"\n🔄 Importando produtos de {csv_path.name}...")
            result = self.price_monitor.import_products_from_csv(csv_path)
            
            self.session_stats['prices_monitored'] += result['imported_count']
            
            self.show_success(f"{result['imported_count']} produtos importados!")
            if result['errors']:
                self.show_warning(f"{len(result['errors'])} erros encontrados")
            
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _view_price_history(self):
        """Visualiza histórico de preços"""
        print("\n📈 Histórico de preços")
        product_id = input("ID do produto: ").strip()
        days = input("Dias de histórico [30]: ").strip()
        days = int(days) if days.isdigit() else 30
        
        history = self.price_monitor.get_price_history(product_id, days=days)
        
        if history:
            print(f"\n📊 Histórico de {len(history)} entradas:")
            for entry in history[-15:]:  # Últimas 15
                timestamp = datetime.fromisoformat(entry['timestamp'])
                promo = " 🏷️" if entry['promotion'] else ""
                print(f"  {timestamp.strftime('%d/%m %H:%M')} - R$ {entry['price']:6.2f}{promo}")
        else:
            self.show_error("Nenhum histórico encontrado")
        
        self.pause()
    
    def _view_price_changes(self):
        """Visualiza mudanças de preços"""
        print("\n📊 Mudanças de preços")
        days = input("Dias para análise [7]: ").strip()
        days = int(days) if days.isdigit() else 7
        
        changes = self.price_monitor.get_price_changes(days=days)
        
        print(f"\n📈 {len(changes)} mudanças nos últimos {days} dias:")
        for change in changes[:20]:
            direction = "↑" if change['change_percentage'] > 0 else "↓"
            timestamp = datetime.fromisoformat(change['timestamp'])
            print(f"  {timestamp.strftime('%d/%m')} {change['product_name'][:25]:<25} {direction} {change['change_percentage']:+6.1f}%")
        
        self.pause()
    
    def _view_price_alerts(self):
        """Visualiza alertas de preços"""
        print("\n🚨 Alertas de preços")
        alerts = self.price_monitor.get_price_alerts()
        
        print(f"\n⚠️ {len(alerts)} alertas não reconhecidos:")
        for alert in alerts[:15]:
            timestamp = datetime.fromisoformat(alert['timestamp'])
            print(f"  {alert['id']:3d}. [{timestamp.strftime('%d/%m')}] {alert['message']}")
        
        if alerts:
            try:
                alert_id = input("\nID do alerta para reconhecer (Enter para pular): ").strip()
                if alert_id.isdigit():
                    if self.price_monitor.acknowledge_alert(int(alert_id)):
                        self.show_success("Alerta reconhecido!")
                    else:
                        self.show_error("Erro ao reconhecer alerta")
            except:
                pass
        
        self.pause()
    
    def _find_best_deals(self):
        """Encontra melhores ofertas"""
        print("\n💎 Melhores ofertas atuais")
        
        deals = self.price_monitor.find_best_deals(max_results=15)
        
        print(f"\n💰 {len(deals)} ofertas encontradas:")
        for i, deal in enumerate(deals, 1):
            print(f"{i:2d}. {deal['product_name'][:35]:<35} R$ {deal['current_price']:6.2f} "
                 f"({deal['discount_percentage']:4.1f}% off)")
        
        self.pause()
    
    def _generate_price_report(self):
        """Gera relatório de preços"""
        print("\n📋 Geração de relatório de preços")
        days = input("Dias para análise [30]: ").strip()
        days = int(days) if days.isdigit() else 30
        
        try:
            report_path = self.price_monitor.generate_price_report(days=days)
            self.show_success(f"Relatório gerado: {report_path.name}")
        except Exception as e:
            self.show_error(str(e))
        
        self.pause()
    
    def _view_product_price_stats(self):
        """Visualiza estatísticas de preço de produto"""
        print("\n📊 Estatísticas de produto")
        product_id = input("ID do produto: ").strip()
        
        stats = self.price_monitor.get_price_statistics(product_id)
        
        if stats:
            print(f"\n📈 Estatísticas para '{stats.product_name}':")
            print(f"  Preço atual: R$ {stats.current_price:.2f}")
            print(f"  Mínimo: R$ {stats.min_price:.2f}")
            print(f"  Máximo: R$ {stats.max_price:.2f}")
            print(f"  Média: R$ {stats.avg_price:.2f}")
            print(f"  Mediana: R$ {stats.median_price:.2f}")
            print(f"  Tendência: {stats.trend}")
            print(f"  Volatilidade: {stats.price_volatility:.2f}")
            print(f"  Total de mudanças: {stats.total_changes}")
        else:
            self.show_error("Produto não encontrado")
        
        self.pause()
    
    def _configure_price_alerts(self):
        """Configura alertas de preços"""
        print("\n⚙️  Configuração de alertas")
        print("Funcionalidade em desenvolvimento...")
        self.pause()