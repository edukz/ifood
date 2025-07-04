#!/usr/bin/env python3
"""
Sistema de Monitoramento de Preços (Histórico)
Monitora variações de preços ao longo do tempo
"""

import csv
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

from src.utils.logger import setup_logger
from src.config.settings import SETTINGS


@dataclass
class PriceEntry:
    """Entrada de preço para um produto"""
    product_id: str
    product_name: str
    restaurant_id: str
    restaurant_name: str
    price: float
    original_price: Optional[float]
    currency: str = "BRL"
    timestamp: datetime = field(default_factory=datetime.now)
    promotion: bool = False
    promotion_type: Optional[str] = None


@dataclass
class PriceChange:
    """Representa uma mudança de preço"""
    product_id: str
    product_name: str
    restaurant_name: str
    old_price: float
    new_price: float
    change_amount: float
    change_percentage: float
    change_type: str  # 'increase', 'decrease', 'stable'
    timestamp: datetime
    days_since_last_change: int


@dataclass
class PriceStats:
    """Estatísticas de preço para um produto"""
    product_id: str
    product_name: str
    current_price: float
    min_price: float
    max_price: float
    avg_price: float
    median_price: float
    price_volatility: float  # Desvio padrão
    total_changes: int
    last_updated: datetime
    trend: str  # 'rising', 'falling', 'stable'


class PriceMonitor:
    """Sistema de monitoramento de preços"""
    
    def __init__(self, db_path: Path = None):
        self.logger = setup_logger("PriceMonitor")
        self.db_path = db_path or Path("data/price_history.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurações
        self.config = {
            'min_change_threshold': 0.05,  # 5 centavos
            'min_percentage_threshold': 0.02,  # 2%
            'volatility_threshold': 0.15,  # 15%
            'trend_analysis_days': 30,
            'alert_percentage_threshold': 0.20  # 20% para alertas
        }
        
        self._init_database()
        
    def _init_database(self):
        """Inicializa banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Tabela principal de preços
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    restaurant_id TEXT NOT NULL,
                    restaurant_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    original_price REAL,
                    currency TEXT DEFAULT 'BRL',
                    timestamp DATETIME NOT NULL,
                    promotion BOOLEAN DEFAULT FALSE,
                    promotion_type TEXT,
                    UNIQUE(product_id, restaurant_id, timestamp)
                )
            """)
            
            # Tabela de mudanças de preço
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    restaurant_name TEXT NOT NULL,
                    old_price REAL NOT NULL,
                    new_price REAL NOT NULL,
                    change_amount REAL NOT NULL,
                    change_percentage REAL NOT NULL,
                    change_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    days_since_last_change INTEGER
                )
            """)
            
            # Tabela de alertas de preço
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    restaurant_name TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    price_change_percentage REAL,
                    timestamp DATETIME NOT NULL,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Índices para performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_price_product_restaurant ON price_history (product_id, restaurant_id)",
                "CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_history (timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_changes_product ON price_changes (product_id)",
                "CREATE INDEX IF NOT EXISTS idx_changes_timestamp ON price_changes (timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON price_alerts (timestamp)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            self.logger.info("Banco de dados de preços inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_price_entry(self, entry: PriceEntry) -> bool:
        """Adiciona entrada de preço ao histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verifica se já existe entrada recente para o mesmo produto
            cursor.execute("""
                SELECT price, timestamp FROM price_history 
                WHERE product_id = ? AND restaurant_id = ?
                ORDER BY timestamp DESC LIMIT 1
            """, (entry.product_id, entry.restaurant_id))
            
            last_entry = cursor.fetchone()
            
            # Adiciona nova entrada
            cursor.execute("""
                INSERT OR REPLACE INTO price_history 
                (product_id, product_name, restaurant_id, restaurant_name, 
                 price, original_price, currency, timestamp, promotion, promotion_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.product_id, entry.product_name, entry.restaurant_id, 
                entry.restaurant_name, entry.price, entry.original_price,
                entry.currency, entry.timestamp, entry.promotion, entry.promotion_type
            ))
            
            # Verifica se houve mudança significativa de preço
            if last_entry:
                old_price, last_timestamp = last_entry
                if abs(entry.price - old_price) >= self.config['min_change_threshold']:
                    self._record_price_change(entry, old_price, last_timestamp, cursor)
            
            conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar preço: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _record_price_change(self, entry: PriceEntry, old_price: float, 
                           last_timestamp: str, cursor):
        """Registra mudança de preço"""
        change_amount = entry.price - old_price
        change_percentage = (change_amount / old_price) * 100 if old_price > 0 else 0
        
        # Determina tipo de mudança
        if abs(change_percentage) < self.config['min_percentage_threshold'] * 100:
            change_type = 'stable'
        elif change_amount > 0:
            change_type = 'increase'
        else:
            change_type = 'decrease'
        
        # Calcula dias desde última mudança
        last_dt = datetime.fromisoformat(last_timestamp)
        days_since = (entry.timestamp - last_dt).days
        
        # Registra mudança
        cursor.execute("""
            INSERT INTO price_changes 
            (product_id, product_name, restaurant_name, old_price, new_price,
             change_amount, change_percentage, change_type, timestamp, days_since_last_change)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.product_id, entry.product_name, entry.restaurant_name,
            old_price, entry.price, change_amount, change_percentage,
            change_type, entry.timestamp, days_since
        ))
        
        # Verifica se precisa gerar alerta
        if abs(change_percentage) >= self.config['alert_percentage_threshold'] * 100:
            self._create_price_alert(entry, change_percentage, change_type, cursor)
    
    def _create_price_alert(self, entry: PriceEntry, change_percentage: float, 
                          change_type: str, cursor):
        """Cria alerta de mudança significativa de preço"""
        if change_type == 'increase':
            alert_type = 'price_spike'
            message = f"Aumento significativo de {change_percentage:.1f}% no preço de {entry.product_name}"
        else:
            alert_type = 'price_drop'
            message = f"Queda significativa de {abs(change_percentage):.1f}% no preço de {entry.product_name}"
        
        cursor.execute("""
            INSERT INTO price_alerts 
            (product_id, product_name, restaurant_name, alert_type, message,
             price_change_percentage, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.product_id, entry.product_name, entry.restaurant_name,
            alert_type, message, change_percentage, entry.timestamp
        ))
        
        self.logger.info(f"Alerta criado: {message}")
    
    def import_products_from_csv(self, csv_path: Path) -> Dict[str, Any]:
        """Importa produtos de arquivo CSV para monitoramento"""
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
        
        imported_count = 0
        errors = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Extrai preço numérico
                    price_str = row.get('preco', '').replace('R$', '').replace(' ', '').replace(',', '.')
                    if not price_str or price_str == 'Não informado':
                        continue
                    
                    price = float(price_str)
                    if price <= 0:
                        continue
                    
                    # Extrai preço original se disponível
                    original_price = None
                    original_price_str = row.get('preco_original', '')
                    if original_price_str and original_price_str != 'Não informado':
                        original_price_str = original_price_str.replace('R$', '').replace(' ', '').replace(',', '.')
                        try:
                            original_price = float(original_price_str)
                        except ValueError:
                            pass
                    
                    # Cria entrada de preço
                    entry = PriceEntry(
                        product_id=row.get('id', f"product_{imported_count}"),
                        product_name=row.get('nome', 'Produto sem nome'),
                        restaurant_id=row.get('restaurant_id', 'unknown'),
                        restaurant_name=row.get('restaurant_name', 'Restaurante desconhecido'),
                        price=price,
                        original_price=original_price,
                        promotion=original_price is not None and original_price > price,
                        timestamp=datetime.now()
                    )
                    
                    if self.add_price_entry(entry):
                        imported_count += 1
                    
                    if imported_count % 100 == 0:
                        self.logger.info(f"Importados {imported_count} produtos...")
                        
                except Exception as e:
                    errors.append(f"Linha {imported_count + 1}: {str(e)}")
                    continue
        
        self.logger.info(f"Importação concluída: {imported_count} produtos importados")
        
        return {
            'imported_count': imported_count,
            'errors': errors,
            'source_file': str(csv_path)
        }
    
    def get_price_history(self, product_id: str, restaurant_id: str = None, 
                         days: int = 30) -> List[Dict[str, Any]]:
        """Obtém histórico de preços de um produto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            if restaurant_id:
                cursor.execute("""
                    SELECT * FROM price_history 
                    WHERE product_id = ? AND restaurant_id = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (product_id, restaurant_id, since_date))
            else:
                cursor.execute("""
                    SELECT * FROM price_history 
                    WHERE product_id = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (product_id, since_date))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar histórico: {e}")
            return []
        finally:
            conn.close()
    
    def get_price_statistics(self, product_id: str, restaurant_id: str = None,
                           days: int = 30) -> Optional[PriceStats]:
        """Calcula estatísticas de preço para um produto"""
        history = self.get_price_history(product_id, restaurant_id, days)
        
        if not history:
            return None
        
        prices = [entry['price'] for entry in history]
        
        # Calcula estatísticas básicas
        current_price = prices[-1]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        
        # Calcula volatilidade (desvio padrão)
        volatility = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # Determina tendência
        if len(prices) >= 3:
            recent_prices = prices[-3:]
            if all(recent_prices[i] <= recent_prices[i+1] for i in range(len(recent_prices)-1)):
                trend = 'rising'
            elif all(recent_prices[i] >= recent_prices[i+1] for i in range(len(recent_prices)-1)):
                trend = 'falling'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # Conta mudanças
        changes = self.get_price_changes(product_id, restaurant_id, days)
        
        return PriceStats(
            product_id=product_id,
            product_name=history[0]['product_name'],
            current_price=current_price,
            min_price=min_price,
            max_price=max_price,
            avg_price=avg_price,
            median_price=median_price,
            price_volatility=volatility,
            total_changes=len(changes),
            last_updated=datetime.fromisoformat(history[-1]['timestamp']),
            trend=trend
        )
    
    def get_price_changes(self, product_id: str = None, restaurant_id: str = None,
                         days: int = 30) -> List[Dict[str, Any]]:
        """Obtém mudanças de preço"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            sql = "SELECT * FROM price_changes WHERE timestamp >= ?"
            params = [since_date]
            
            if product_id:
                sql += " AND product_id = ?"
                params.append(product_id)
            
            if restaurant_id:
                sql += " AND restaurant_name LIKE ?"
                params.append(f"%{restaurant_id}%")
            
            sql += " ORDER BY timestamp DESC"
            
            cursor.execute(sql, params)
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar mudanças: {e}")
            return []
        finally:
            conn.close()
    
    def get_price_alerts(self, acknowledged: bool = False, days: int = 7) -> List[Dict[str, Any]]:
        """Obtém alertas de preço"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT * FROM price_alerts 
                WHERE acknowledged = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (acknowledged, since_date))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar alertas: {e}")
            return []
        finally:
            conn.close()
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Marca alerta como reconhecido"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE price_alerts 
                SET acknowledged = TRUE 
                WHERE id = ?
            """, (alert_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao reconhecer alerta: {e}")
            return False
        finally:
            conn.close()
    
    def find_best_deals(self, category: str = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """Encontra melhores ofertas (produtos com preços mais baixos do histórico)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Query complexa para encontrar produtos com preços atuais baixos
            sql = """
                WITH current_prices AS (
                    SELECT 
                        product_id,
                        product_name,
                        restaurant_name,
                        price as current_price,
                        ROW_NUMBER() OVER (PARTITION BY product_id, restaurant_id ORDER BY timestamp DESC) as rn
                    FROM price_history
                ),
                price_stats AS (
                    SELECT 
                        product_id,
                        MIN(price) as min_price,
                        MAX(price) as max_price,
                        AVG(price) as avg_price
                    FROM price_history
                    GROUP BY product_id
                )
                SELECT 
                    cp.product_id,
                    cp.product_name,
                    cp.restaurant_name,
                    cp.current_price,
                    ps.min_price,
                    ps.max_price,
                    ps.avg_price,
                    ((ps.avg_price - cp.current_price) / ps.avg_price * 100) as discount_percentage
                FROM current_prices cp
                JOIN price_stats ps ON cp.product_id = ps.product_id
                WHERE cp.rn = 1 
                  AND cp.current_price <= ps.min_price * 1.1
                  AND ps.max_price > ps.min_price
                ORDER BY discount_percentage DESC
                LIMIT ?
            """
            
            cursor.execute(sql, (max_results,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar ofertas: {e}")
            return []
        finally:
            conn.close()
    
    def generate_price_report(self, output_path: Path = None, days: int = 30) -> Path:
        """Gera relatório de preços"""
        output_path = output_path or Path("reports") / f"price_report_{datetime.now().strftime('%Y%m%d')}.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Coleta dados
        recent_changes = self.get_price_changes(days=days)
        recent_alerts = self.get_price_alerts(days=days)
        best_deals = self.find_best_deals()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("RELATÓRIO DE MONITORAMENTO DE PREÇOS\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Período analisado: Últimos {days} dias\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            # Resumo de mudanças
            f.write("RESUMO DE MUDANÇAS:\n")
            f.write("-" * 30 + "\n")
            increases = [c for c in recent_changes if c['change_type'] == 'increase']
            decreases = [c for c in recent_changes if c['change_type'] == 'decrease']
            f.write(f"Total de mudanças: {len(recent_changes)}\n")
            f.write(f"Aumentos de preço: {len(increases)}\n")
            f.write(f"Reduções de preço: {len(decreases)}\n\n")
            
            # Maiores mudanças
            if recent_changes:
                f.write("MAIORES MUDANÇAS DE PREÇO:\n")
                f.write("-" * 30 + "\n")
                sorted_changes = sorted(recent_changes, key=lambda x: abs(x['change_percentage']), reverse=True)
                for i, change in enumerate(sorted_changes[:10], 1):
                    direction = "↑" if change['change_percentage'] > 0 else "↓"
                    f.write(f"{i:2d}. {change['product_name'][:30]:<30} {direction} {change['change_percentage']:+6.1f}%\n")
                f.write("\n")
            
            # Alertas
            if recent_alerts:
                f.write("ALERTAS RECENTES:\n")
                f.write("-" * 30 + "\n")
                for i, alert in enumerate(recent_alerts[:10], 1):
                    f.write(f"{i:2d}. {alert['message']}\n")
                f.write("\n")
            
            # Melhores ofertas
            if best_deals:
                f.write("MELHORES OFERTAS ATUAIS:\n")
                f.write("-" * 30 + "\n")
                for i, deal in enumerate(best_deals[:10], 1):
                    f.write(f"{i:2d}. {deal['product_name'][:25]:<25} R$ {deal['current_price']:6.2f} "
                           f"({deal['discount_percentage']:4.1f}% abaixo da média)\n")
        
        self.logger.info(f"Relatório gerado: {output_path}")
        return output_path


def create_price_monitor_cli():
    """Interface CLI para monitoramento de preços"""
    monitor = PriceMonitor()
    
    print("\n" + "=" * 60)
    print("SISTEMA DE MONITORAMENTO DE PREÇOS")
    print("=" * 60)
    
    while True:
        print("\nOpções:")
        print("1. Importar produtos de CSV")
        print("2. Ver histórico de preços")
        print("3. Ver mudanças de preços")
        print("4. Ver alertas de preços")
        print("5. Encontrar melhores ofertas")
        print("6. Gerar relatório")
        print("7. Estatísticas de produto")
        print("0. Sair")
        
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            file_path = input("Caminho do arquivo CSV: ").strip()
            try:
                result = monitor.import_products_from_csv(Path(file_path))
                print(f"✅ {result['imported_count']} produtos importados!")
                if result['errors']:
                    print(f"⚠️ {len(result['errors'])} erros encontrados")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        elif choice == "2":
            product_id = input("ID do produto: ").strip()
            days = int(input("Dias de histórico [30]: ") or "30")
            
            history = monitor.get_price_history(product_id, days=days)
            if history:
                print(f"\n📈 Histórico de {len(history)} entradas:")
                for entry in history[-10:]:  # Últimas 10
                    timestamp = datetime.fromisoformat(entry['timestamp'])
                    print(f"  {timestamp.strftime('%d/%m %H:%M')} - R$ {entry['price']:.2f}")
            else:
                print("❌ Nenhum histórico encontrado")
        
        elif choice == "3":
            days = int(input("Dias para análise [7]: ") or "7")
            changes = monitor.get_price_changes(days=days)
            
            print(f"\n📊 {len(changes)} mudanças nos últimos {days} dias:")
            for change in changes[:15]:
                direction = "↑" if change['change_percentage'] > 0 else "↓"
                print(f"  {change['product_name'][:30]:<30} {direction} {change['change_percentage']:+6.1f}%")
        
        elif choice == "4":
            alerts = monitor.get_price_alerts()
            print(f"\n🚨 {len(alerts)} alertas não reconhecidos:")
            for alert in alerts:
                print(f"  {alert['id']:3d}. {alert['message']}")
        
        elif choice == "5":
            deals = monitor.find_best_deals()
            print(f"\n💰 {len(deals)} melhores ofertas:")
            for deal in deals:
                print(f"  {deal['product_name'][:30]:<30} R$ {deal['current_price']:6.2f} "
                     f"({deal['discount_percentage']:4.1f}% off)")
        
        elif choice == "6":
            days = int(input("Dias para relatório [30]: ") or "30")
            report_path = monitor.generate_price_report(days=days)
            print(f"✅ Relatório gerado: {report_path}")
        
        elif choice == "7":
            product_id = input("ID do produto: ").strip()
            stats = monitor.get_price_statistics(product_id)
            
            if stats:
                print(f"\n📊 Estatísticas para {stats.product_name}:")
                print(f"  Preço atual: R$ {stats.current_price:.2f}")
                print(f"  Mínimo: R$ {stats.min_price:.2f}")
                print(f"  Máximo: R$ {stats.max_price:.2f}")
                print(f"  Média: R$ {stats.avg_price:.2f}")
                print(f"  Tendência: {stats.trend}")
                print(f"  Volatilidade: {stats.price_volatility:.2f}")
            else:
                print("❌ Produto não encontrado")
        
        elif choice == "0":
            break
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    create_price_monitor_cli()