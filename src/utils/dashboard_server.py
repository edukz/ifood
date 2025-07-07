"""
Servidor Web Simples para Dashboard de Performance
Exibe métricas em tempo real do sistema de scraping
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

from src.utils.performance_monitor import performance_monitor
from src.database.database_adapter import get_database_manager
from src.utils.logger import setup_logger

logger = setup_logger("DashboardServer")


class DashboardHandler(BaseHTTPRequestHandler):
    """Handler para requisições do dashboard"""
    
    def do_GET(self):
        """Processa requisições GET"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self._serve_dashboard()
        elif path == '/api/metrics':
            self._serve_metrics()
        elif path == '/api/stats':
            self._serve_stats()
        elif path == '/api/alerts':
            self._serve_alerts()
        elif path == '/health':
            self._serve_health()
        else:
            self._serve_404()
    
    def _serve_dashboard(self):
        """Serve página principal do dashboard"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>iFood Scraper - Performance Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric-unit { font-size: 14px; color: #666; }
        .status-good { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-error { color: #dc3545; }
        .refresh-info { text-align: center; color: #666; margin-top: 20px; }
        .alert-box { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .operations-table { width: 100%; border-collapse: collapse; }
        .operations-table th, .operations-table td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        .operations-table th { background-color: #f8f9fa; }
    </style>
    <script>
        function refreshDashboard() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => updateMetrics(data))
                .catch(error => console.error('Error:', error));
            
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => updateStats(data))
                .catch(error => console.error('Error:', error));
                
            fetch('/api/alerts')
                .then(response => response.json())
                .then(data => updateAlerts(data))
                .catch(error => console.error('Error:', error));
        }
        
        function updateMetrics(data) {
            // Atualiza métricas do sistema
            updateMetric('cpu-usage', data.system_metrics?.cpu_usage?.latest || 0, '%');
            updateMetric('memory-usage', data.system_metrics?.memory_usage?.latest || 0, '%');
            updateMetric('mysql-connections', data.system_metrics?.mysql_connections?.latest || 0, 'conn');
            updateMetric('operations-total', data.operation_stats ? Object.keys(data.operation_stats).length : 0, 'ops');
        }
        
        function updateStats(data) {
            // Atualiza estatísticas detalhadas
            const operations = data.operation_stats || {};
            let tableHtml = '<tr><th>Operação</th><th>Total</th><th>Taxa Sucesso</th><th>Tempo Médio</th><th>Ops/s</th></tr>';
            
            Object.entries(operations).forEach(([op, stats]) => {
                tableHtml += `<tr>
                    <td>${op}</td>
                    <td>${stats.total_operations || 0}</td>
                    <td class="${stats.success_rate > 95 ? 'status-good' : stats.success_rate > 80 ? 'status-warning' : 'status-error'}">${(stats.success_rate || 0).toFixed(1)}%</td>
                    <td>${(stats.avg_duration || 0).toFixed(3)}s</td>
                    <td>${(stats.operations_per_second || 0).toFixed(2)}</td>
                </tr>`;
            });
            
            document.getElementById('operations-table').innerHTML = tableHtml;
        }
        
        function updateAlerts(data) {
            const alertsContainer = document.getElementById('alerts-container');
            if (data.active_alerts && data.active_alerts.length > 0) {
                alertsContainer.style.display = 'block';
                alertsContainer.innerHTML = '<h3>⚠️ Alertas Ativos</h3>' +
                    data.active_alerts.map(alert => `<div>• ${alert.alert} (${alert.duration_seconds}s)</div>`).join('');
            } else {
                alertsContainer.style.display = 'none';
            }
        }
        
        function updateMetric(id, value, unit) {
            const valueElement = document.getElementById(id + '-value');
            const unitElement = document.getElementById(id + '-unit');
            if (valueElement) valueElement.textContent = typeof value === 'number' ? value.toFixed(1) : value;
            if (unitElement) unitElement.textContent = unit;
        }
        
        // Atualiza a cada 5 segundos
        setInterval(refreshDashboard, 5000);
        
        // Primeira carga
        document.addEventListener('DOMContentLoaded', refreshDashboard);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 iFood Scraper Dashboard</h1>
            <p>Monitoramento de Performance em Tempo Real</p>
        </div>
        
        <div id="alerts-container" class="alert-box" style="display: none;"></div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">CPU Usage</div>
                <div class="metric-value" id="cpu-usage-value">--</div>
                <div class="metric-unit" id="cpu-usage-unit">%</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Memory Usage</div>
                <div class="metric-value" id="memory-usage-value">--</div>
                <div class="metric-unit" id="memory-usage-unit">%</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">MySQL Connections</div>
                <div class="metric-value" id="mysql-connections-value">--</div>
                <div class="metric-unit" id="mysql-connections-unit">conn</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Active Operations</div>
                <div class="metric-value" id="operations-total-value">--</div>
                <div class="metric-unit" id="operations-total-unit">ops</div>
            </div>
        </div>
        
        <div class="metric-card" style="margin-top: 20px;">
            <div class="metric-title">📊 Estatísticas de Operações</div>
            <table class="operations-table" id="operations-table">
                <tr><th>Carregando...</th></tr>
            </table>
        </div>
        
        <div class="refresh-info">
            🔄 Atualização automática a cada 5 segundos | ⏰ Última atualização: <span id="last-update">--</span>
        </div>
    </div>
    
    <script>
        // Atualiza timestamp
        setInterval(() => {
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }, 1000);
    </script>
</body>
</html>
        """
        
        self._send_response(200, html_content, 'text/html')
    
    def _serve_metrics(self):
        """Serve métricas em JSON"""
        try:
            if performance_monitor.running:
                metrics_data = performance_monitor.get_dashboard_data()
            else:
                metrics_data = {
                    'status': 'monitoring_disabled',
                    'system_metrics': {},
                    'operation_stats': {},
                    'active_alerts': [],
                    'table_stats': {}
                }
            
            self._send_response(200, json.dumps(metrics_data, default=str), 'application/json')
        except Exception as e:
            error_data = {'error': str(e), 'timestamp': datetime.now().isoformat()}
            self._send_response(500, json.dumps(error_data), 'application/json')
    
    def _serve_stats(self):
        """Serve estatísticas detalhadas"""
        try:
            # Tenta criar uma instância temporária para obter stats
            db = MonitoredDatabaseManager(enable_monitoring=False)
            stats_data = db.get_comprehensive_stats()
            
            self._send_response(200, json.dumps(stats_data, default=str), 'application/json')
        except Exception as e:
            error_data = {'error': str(e), 'timestamp': datetime.now().isoformat()}
            self._send_response(500, json.dumps(error_data), 'application/json')
    
    def _serve_alerts(self):
        """Serve informações de alertas"""
        try:
            if performance_monitor.running:
                alert_data = {
                    'active_alerts': performance_monitor.alert_manager.get_active_alerts(),
                    'recent_alerts': performance_monitor.alert_manager.alert_history[-5:],
                    'total_rules': len(performance_monitor.alert_manager.rules)
                }
            else:
                alert_data = {
                    'active_alerts': [],
                    'recent_alerts': [],
                    'total_rules': 0,
                    'status': 'monitoring_disabled'
                }
            
            self._send_response(200, json.dumps(alert_data, default=str), 'application/json')
        except Exception as e:
            error_data = {'error': str(e), 'timestamp': datetime.now().isoformat()}
            self._send_response(500, json.dumps(error_data), 'application/json')
    
    def _serve_health(self):
        """Serve status de saúde do sistema"""
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': performance_monitor.running,
                'uptime_seconds': (datetime.now() - performance_monitor.collector.start_time).total_seconds() if performance_monitor.running else 0
            }
            
            self._send_response(200, json.dumps(health_data), 'application/json')
        except Exception as e:
            error_data = {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self._send_response(500, json.dumps(error_data), 'application/json')
    
    def _serve_404(self):
        """Serve página 404"""
        content = '{"error": "Not Found", "code": 404}'
        self._send_response(404, content, 'application/json')
    
    def _send_response(self, status_code: int, content: str, content_type: str):
        """Envia resposta HTTP"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suprime logs automáticos do servidor"""
        pass


class DashboardServer:
    """Servidor do dashboard de performance"""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        
        self.logger = setup_logger("DashboardServer")
    
    def start(self):
        """Inicia o servidor"""
        if self.running:
            return
        
        try:
            self.server = HTTPServer((self.host, self.port), DashboardHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.running = True
            
            self.logger.info(f"Dashboard server iniciado em http://{self.host}:{self.port}")
            print(f"🌐 Dashboard disponível em: http://{self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar servidor: {e}")
            raise
    
    def stop(self):
        """Para o servidor"""
        if not self.running:
            return
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        if self.server_thread:
            self.server_thread.join(timeout=5)
        
        self.running = False
        self.logger.info("Dashboard server parado")
    
    def is_running(self) -> bool:
        """Verifica se o servidor está rodando"""
        return self.running


# Instância global
dashboard_server = DashboardServer()


if __name__ == "__main__":
    # Teste do dashboard
    print("🧪 Iniciando teste do dashboard...")
    
    # Inicia monitor de performance
    if not performance_monitor.running:
        performance_monitor.start()
    
    # Inicia servidor
    dashboard_server.start()
    
    try:
        print("Dashboard rodando... Pressione Ctrl+C para parar")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando servidor...")
        dashboard_server.stop()
        performance_monitor.stop()
        print("✅ Servidor parado")