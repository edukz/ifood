# 🍔 iFood Data Scraper & Analytics Platform

Uma plataforma profissional para extração, análise e monitoramento de dados da plataforma iFood, desenvolvida com arquitetura modular, banco de dados MySQL e interface de usuário avançada.

## 🚀 Características Principais

- **🏗️ Arquitetura Modular**: Sistema organizado com separação de responsabilidades
- **🗄️ Banco de Dados MySQL**: Armazenamento robusto com pool de conexões
- **🎯 Interface Unificada**: Sistema de menus modular com scrapy unitário
- **📊 Analytics Avançado**: Monitoramento de preços e análise de tendências
- **🔍 Sistema de Busca**: Otimização e indexação inteligente
- **🤖 Comportamento Humano**: Simula ações humanas para evitar detecção
- **🛡️ Sistema de Retry**: Tratamento robusto de erros com circuit breaker
- **📈 Monitoramento**: Performance e progresso em tempo real

## 🏗️ Estrutura do Projeto

```
ifood/
├── main.py                     # 🎯 Ponto de entrada - Sistema unificado
├── README.md                   # 📖 Documentação principal
├── .env.example               # ⚙️ Exemplo de configuração
├── src/                       # 💻 Código fonte
│   ├── config/                # ⚙️ Configurações
│   │   ├── settings.py        # 🔧 Configurações gerais
│   │   ├── browser_config.py  # 🌐 Configurações do navegador
│   │   └── database.py        # 🗄️ Configurações MySQL
│   ├── database/              # 🗄️ Gerenciadores de banco
│   │   ├── database_manager_v2.py # 📊 Gerenciador MySQL V2
│   │   └── database_adapter.py    # 🔄 Adaptador de compatibilidade
│   ├── models/                # 🏷️ Modelos de dados
│   │   ├── category.py        # 📂 Modelo de categoria
│   │   ├── restaurant.py      # 🏪 Modelo de restaurante
│   │   └── product.py         # 🍽️ Modelo de produto
│   ├── scrapers/              # 🕷️ Scrapers especializados
│   │   ├── base.py            # 🔧 Classe base
│   │   ├── category_scraper.py # 📂 Extração de categorias
│   │   ├── restaurant_scraper.py # 🏪 Extração de restaurantes
│   │   ├── product_scraper.py  # 🍽️ Extração de produtos
│   │   ├── optimized/         # ⚡ Scrapers otimizados
│   │   └── parallel/          # 🔄 Scrapers paralelos
│   ├── ui/                    # 🖥️ Interface de usuário
│   │   ├── base_menu.py       # 🔧 Classe base dos menus
│   │   ├── extraction_menus.py # 📊 Menus de extração
│   │   ├── analysis_menus.py   # 📈 Menus de análise
│   │   └── system_menus.py     # ⚙️ Menus do sistema
│   └── utils/                 # 🛠️ Utilitários
│       ├── logger.py          # 📝 Sistema de logs
│       ├── helpers.py         # 🔧 Funções auxiliares
│       ├── retry_handler.py   # 🔄 Sistema de retry
│       ├── performance_monitor.py # 📊 Monitor de performance
│       ├── price_monitor.py    # 💰 Monitoramento de preços
│       ├── product_categorizer.py # 🏷️ Categorização automática
│       ├── search_optimizer.py # 🔍 Otimização de busca
│       └── dashboard_server.py # 📊 Servidor de dashboard
├── database/                  # 🗄️ Sistema de banco de dados
│   ├── README_V2.md           # 📖 Documentação do banco
│   ├── complete_database_setup.sql # 🔧 Setup completo
│   ├── schema_v2_clean.sql    # 📊 Schema MySQL V2
│   └── create_database.sql    # 🔨 Criação do banco
├── cache/                     # 📦 Sistema de cache
│   └── search_indexes/        # 🔍 Índices de busca
├── tests/                     # 🧪 Testes automatizados
├── config/                    # ⚙️ Configurações
│   └── requirements.txt       # 📋 Dependências Python
├── data/                      # 📊 Dados persistidos
│   └── price_history.db       # 💰 Histórico de preços
├── logs/                      # 📝 Arquivos de log
├── tools/                     # 🔧 Ferramentas auxiliares
│   ├── check_dependencies.py  # ✅ Verificador de dependências
│   ├── archive_manager.py     # 📦 Gerenciador de arquivos
│   ├── migrate_data_structure.py # 🔄 Migração de dados
│   └── refresh_search_indexes.py # 🔍 Atualização de índices
└── archive/                   # 📦 Arquivos arquivados
    ├── compressed_data/       # 🗜️ Dados comprimidos
    └── screenshots/           # 📸 Screenshots de debug
```

## 🚀 Instalação e Configuração

### 1. **Dependências do Sistema**

```bash
# Ubuntu/Debian
sudo apt-get install mysql-server python3-pip python3-venv

# Verificar MySQL
sudo systemctl status mysql
```

### 2. **Configuração do Banco de Dados**

```bash
# Criar banco de dados
mysql -u root -p
CREATE DATABASE ifood_scraper_v3;
CREATE USER 'ifood_user'@'localhost' IDENTIFIED BY 'sua_senha';
GRANT ALL PRIVILEGES ON ifood_scraper_v3.* TO 'ifood_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. **Instalação do Python**

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r config/requirements.txt

# Configurar Playwright
playwright install
```

### 4. **Configuração do Ambiente**

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

**Exemplo de .env:**
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=ifood_user
DB_PASSWORD=sua_senha
DB_NAME=ifood_scraper_v3
DEFAULT_CITY="São Paulo"
HEADLESS_MODE=true
```

### 5. **Verificação da Instalação**

```bash
# Verificar dependências
python tools/check_dependencies.py

# Testar conexão com banco
python -c "from src.database.database_adapter import get_database_manager; print('✅ Conexão OK')"
```

## 🎯 Como Usar

### **Sistema de Menus Unificado**

Execute o sistema principal:

```bash
python main.py
```

**Menu Principal:**
```
🎯 MENU PRINCIPAL:
1. 🔧 Scrapy Unitário
2. 🚀 Execução Paralela
3. 🔍 Sistema de Busca
4. 🏪 Visualizar Restaurantes
5. 📊 Relatórios e Análises
6. ⚙️ Configurações
7. 📋 Status do Sistema
8. ℹ️ Informações do Sistema
0. 🚪 Sair
```

### **1. Scrapy Unitário (Recomendado)**

**Fluxo recomendado:**
```
1. Scrapy Unitário (opção 1)
   └── 1.1 - Extrair Categorias
   └── 1.2 - Extrair Restaurantes
   └── 1.3 - Extrair Produtos
```

**Submenu Scrapy Unitário:**
```
🔧 SCRAPY UNITÁRIO:
1. 🏷️ Extrair Categorias
2. 🏪 Extrair Restaurantes  
3. 🍕 Extrair Produtos
0. 🔙 Voltar
```

### **2. Execução Paralela**

Para processar múltiplas categorias simultaneamente:

```
🚀 EXECUÇÃO PARALELA:
1. 🏷️ Extrair categorias em paralelo
2. 🏪 Extrair restaurantes em paralelo
3. 🍕 Extrair produtos em paralelo
4. 🔄 Execução completa (pipeline)
5. ⚙️ Configurar workers
6. 📊 Demonstração de performance
```

### **3. Sistema de Busca**

Sistema de busca otimizada com indexação:

- **Busca por nome**: Encontra restaurantes e produtos
- **Busca por categoria**: Filtra por tipo de comida
- **Busca avançada**: Múltiplos critérios
- **Índices otimizados**: Respostas rápidas

### **4. Análises e Relatórios**

- **📊 Estatísticas gerais**: Totais e distribuições
- **💰 Monitoramento de preços**: Variações e tendências
- **🏷️ Categorização**: Análise de produtos por categoria
- **📈 Relatórios**: Dados estruturados para análise

## 🗄️ Banco de Dados MySQL

### **Estrutura das Tabelas**

```sql
-- 8 tabelas principais
CREATE TABLE categories (...)      -- Categorias de comida
CREATE TABLE restaurants (...)     -- Dados dos restaurantes
CREATE TABLE products (...)        -- Cardápios e produtos
CREATE TABLE price_history (...)   -- Histórico de preços
CREATE TABLE restaurant_details (...) -- Informações detalhadas
CREATE TABLE reviews (...)         -- Avaliações de clientes
CREATE TABLE extraction_logs (...)  -- Logs de extração
CREATE TABLE system_config (...)   -- Configurações do sistema
```

### **Recursos Avançados**

- **Pool de conexões**: Gerenciamento eficiente
- **Retry automático**: Recuperação de falhas
- **Transações**: Consistência de dados
- **Índices otimizados**: Performance aprimorada
- **Backup automático**: Proteção de dados

## 📊 Dados Extraídos

### **Categorias**
- **Nome**: Nome da categoria (ex: "Japonesa", "Italiana")
- **URL**: Link direto para a categoria
- **Slug**: Identificador único
- **Cidade**: Cidade de origem
- **Ícone**: URL do ícone da categoria

### **Restaurantes**
- **Nome**: Nome do restaurante
- **Categoria**: Tipo de comida
- **Avaliação**: Rating de 0 a 5 estrelas
- **Tempo de Entrega**: Tempo estimado
- **Taxa de Entrega**: Custo de entrega
- **Distância**: Distância do restaurante
- **URL**: Link direto para o cardápio
- **Endereço**: Localização completa

### **Produtos**
- **Nome**: Nome do produto/prato
- **Descrição**: Detalhes e ingredientes
- **Preço**: Valor atual e histórico
- **Categoria**: Tipo de produto
- **Disponibilidade**: Status do produto
- **Imagem**: URL da foto
- **Informações nutricionais**: Quando disponível
- **Tags**: Promoção, Vegano, Novo, etc.

## 🔧 Configurações Avançadas

### **Configurações do Sistema**

```python
# src/config/settings.py
SETTINGS = {
    'city': 'São Paulo',
    'headless': True,
    'max_workers': 3,
    'retry_attempts': 3,
    'delay_range': (1, 3),
    'database_pool_size': 5
}
```

### **Configurações do Banco**

```python
# src/config/database.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'ifood_user',
    'password': 'sua_senha',
    'database': 'ifood_scraper_v3',
    'pool_size': 5,
    'retry_attempts': 3
}
```

## 📊 Monitoramento e Analytics

### **Dashboard em Tempo Real**

```bash
# Iniciar dashboard
python src/utils/dashboard_server.py
```

**Funcionalidades:**
- 📊 Estatísticas em tempo real
- 📈 Gráficos de performance
- 💰 Monitoramento de preços
- 🔍 Busca interativa
- 📋 Logs do sistema

### **Relatórios Automáticos**

- **Relatório diário**: Resumo das atividades
- **Análise de preços**: Variações e tendências
- **Performance**: Métricas de extração
- **Qualidade dos dados**: Validação automática

## 🛠️ Ferramentas Auxiliares

### **Verificação e Manutenção**

```bash
# Verificar dependências
python tools/check_dependencies.py

# Migrar estrutura de dados
python tools/migrate_data_structure.py

# Atualizar índices de busca
python tools/refresh_search_indexes.py

# Gerenciar arquivos
python tools/archive_manager.py
```

### **Análise de Dados**

```bash
# Analisar duplicatas
python tools/analyze_deduplication.py

# Verificar contagem de restaurantes
python tools/check_restaurants_count.py

# Corrigir categorias
python tools/fix_categories.py
```

## 🔍 Sistema de Logs

### **Logs Unificados**

```
logs/
└── ifood_scraper_20250709.log    # Todos os logs do dia
```

**Níveis de Log:**
- **INFO**: Operações normais
- **WARNING**: Alertas importantes
- **ERROR**: Erros recuperáveis
- **CRITICAL**: Erros fatais

### **Configuração de Logs**

```python
# Configurações em src/config/settings.py
LOG_CONFIG = {
    'level': 'INFO',
    'retention_days': 7,
    'max_file_size': '10MB',
    'backup_count': 5
}
```

## 🚀 Performance e Otimizações

### **Características de Performance**

- **🔄 Pool de conexões**: MySQL otimizado
- **⚡ Cache inteligente**: Índices de busca
- **🔀 Processamento paralelo**: Múltiplos workers
- **🎯 Retry automático**: Recuperação de falhas
- **📊 Monitoramento**: Métricas em tempo real

### **Benchmarks**

```
📊 Performance Típica:
- Categorias: ~50 por minuto
- Restaurantes: ~200 por minuto
- Produtos: ~1000 por minuto
- Uso de memória: ~100MB
- Conexões DB: Pool de 5 conexões
```

## 🔐 Segurança e Ética

### **Medidas de Segurança**

- **🛡️ Rate limiting**: Delays entre requisições
- **🎭 User-Agent rotation**: Múltiplos navegadores
- **🔄 Retry inteligente**: Evita sobrecarga
- **📊 Monitoramento**: Detecção de anomalias

### **Uso Responsável**

- **✅ Respeitar robots.txt**
- **✅ Implementar delays apropriados**
- **✅ Uso apenas para fins educacionais**
- **✅ Não sobrecarregar servidores**

## 🆕 Melhorias Recentes

### **Versão 2.0 - Principais Mudanças**

- **🗄️ Migração para MySQL**: De SQLite para MySQL
- **🎯 Interface unificada**: Menu scrapy unitário
- **📊 Analytics avançado**: Monitoramento de preços
- **🔍 Sistema de busca**: Indexação otimizada
- **🛡️ Sistema de retry**: Maior robustez
- **📈 Dashboard**: Visualização em tempo real
- **🧹 Código limpo**: Remoção de funcionalidades mortas

### **Funcionalidades Adicionadas**

- **🔧 Scrapy unitário**: Menu unificado de extração
- **💰 Price monitoring**: Rastreamento de preços
- **🏷️ Auto-categorização**: Classificação automática
- **📊 Performance monitor**: Métricas em tempo real
- **🔍 Search optimizer**: Busca otimizada
- **📦 Archive manager**: Gerenciamento de arquivos

## 📚 Documentação Adicional

### **Arquivos de Documentação**

- **📖 README.md**: Documentação principal
- **🗄️ database/README_V2.md**: Documentação do banco
- **📊 PROJECT_STRUCTURE.md**: Estrutura do projeto
- **📋 docs/**: Documentação técnica detalhada

### **Suporte e Troubleshooting**

```bash
# Verificar sistema
python tools/check_dependencies.py

# Verificar banco
python -c "from src.database.database_adapter import get_database_manager; print('OK')"

# Verificar logs
tail -f logs/ifood_scraper_$(date +%Y%m%d).log
```

## 🔮 Desenvolvimento Futuro

### **Roadmap**

- **🌐 API REST**: Interface web completa
- **📱 Mobile app**: Aplicativo móvel
- **🤖 Machine learning**: Predição de preços
- **🔄 Auto-scheduling**: Execução automática
- **📊 BI Dashboard**: Business Intelligence
- **🌍 Multi-região**: Suporte a múltiplas cidades

### **Contribuições**

Para contribuir com o projeto:

1. **Fork** o repositório
2. **Clone** para sua máquina
3. **Crie** uma branch para sua feature
4. **Commit** suas mudanças
5. **Push** para o GitHub
6. **Abra** um Pull Request

## 📄 Licença

Este projeto é desenvolvido para **fins educacionais e de pesquisa**. Use com responsabilidade e respeite os termos de uso dos sites.

## 🎯 Suporte

Para dúvidas ou problemas:

- **🔧 Instalação**: Siga o guia de instalação
- **🗄️ Banco de dados**: Consulte `database/README_V2.md`
- **📊 Análise**: Use as ferramentas em `tools/`
- **📝 Logs**: Verifique `logs/` para debug
- **🔍 Busca**: Sistema de busca integrado

---

**🍔 Desenvolvido com foco em qualidade, performance e ética no web scraping.**

*Sistema iFood Scraper & Analytics Platform v2.0*