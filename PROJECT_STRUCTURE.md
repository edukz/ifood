# Estrutura do Projeto iFood Scraper V2

## 📁 Estrutura Final Organizada

```
ifood/
│
├── 📄 main.py                     # Ponto de entrada principal
├── 📄 README.md                   # Documentação principal
├── 📄 cleanup_project.py          # Script de limpeza (executar uma vez)
├── 📄 .env                        # Configurações do banco V2
├── 📄 .env.example               # Exemplo de configurações
│
├── 📁 src/                        # Código fonte principal
│   ├── 📁 config/                 # Configurações
│   │   ├── settings.py           # Configurações gerais
│   │   ├── database.py           # Configuração do banco (legado)
│   │   └── browser_config.py     # Configuração do navegador
│   │
│   ├── 📁 database/               # Sistema de banco V2 ✨
│   │   ├── database_manager_v2.py # Gerenciador principal V2
│   │   └── database_adapter.py    # Adaptador de compatibilidade
│   │
│   ├── 📁 models/                 # Modelos de dados
│   │   ├── category.py           # Modelo de categoria
│   │   ├── restaurant.py         # Modelo de restaurante
│   │   └── product.py            # Modelo de produto
│   │
│   ├── 📁 scrapers/               # Scrapers principais
│   │   ├── ifood_scraper.py      # Base para todos os scrapers
│   │   ├── category_scraper.py   # Extrator de categorias
│   │   ├── restaurant_scraper.py # Extrator de restaurantes
│   │   ├── product_scraper.py    # Extrator de produtos
│   │   │
│   │   ├── 📁 optimized/         # Scrapers otimizados
│   │   │   ├── fast_restaurant_scraper.py      # Versão rápida
│   │   │   └── ultra_fast_parallel_scraper.py  # Versão paralela
│   │   │
│   │   └── 📁 parallel/          # Scrapers paralelos
│   │       ├── real_parallel_restaurant_scraper.py
│   │       └── windows_parallel_scraper.py
│   │
│   ├── 📁 ui/                     # Interface do usuário
│   │   ├── base_menu.py          # Menu base
│   │   ├── extraction_menus.py   # Menus de extração
│   │   ├── system_menus.py       # Menus do sistema
│   │   └── analysis_menus.py     # Menus de análise
│   │
│   └── 📁 utils/                  # Utilitários
│       ├── logger.py             # Sistema de logs
│       ├── error_handler.py      # Tratamento de erros
│       ├── helpers.py            # Funções auxiliares
│       ├── human_behavior.py     # Simulação de comportamento humano
│       ├── retry_handler.py      # Sistema de retry
│       ├── performance_monitor.py # Monitor de performance
│       ├── progress_tracker.py   # Rastreador de progresso
│       ├── search_optimizer.py   # Otimizador de busca
│       ├── task_manager.py       # Gerenciador de tarefas
│       ├── price_monitor.py      # Monitor de preços
│       ├── product_categorizer.py # Categorizador de produtos
│       └── dashboard_server.py   # Servidor de dashboard
│
├── 📁 database/                   # Esquemas e documentação
│   ├── schema_v2_clean.sql       # Schema principal V2
│   └── README_V2.md              # Documentação do banco V2
│
├── 📁 tests/                      # Testes automatizados
│   ├── 📁 unit/                  # Testes unitários
│   ├── 📁 integration/           # Testes de integração
│   └── benchmark_batch_insert.py # Benchmarks
│
├── 📁 tools/                      # Ferramentas auxiliares
│   ├── analyze_deduplication.py  # Análise de duplicatas
│   ├── archive_manager.py        # Gerenciador de arquivo
│   ├── check_dependencies.py     # Verificador de dependências
│   ├── check_restaurants_count.py # Contador de restaurantes
│   ├── cleanup_logs.py           # Limpador de logs
│   ├── data_analyzer.py          # Analisador de dados
│   ├── fix_categories.py         # Corretor de categorias
│   ├── migrate_data_structure.py # Migrador de estrutura
│   └── refresh_search_indexes.py # Atualizador de índices
│
├── 📁 docs/                       # Documentação
│   ├── COMO_USAR.md              # Como usar o sistema
│   ├── FLOW_ANALISE.md           # Análise de fluxo
│   └── MELHORIAS_IMPLEMENTADAS.md # Melhorias
│
├── 📁 logs/                       # Logs do sistema
│   └── ifood_scraper_YYYYMMDD.log # Logs diários
│
├── 📁 cache/                      # Cache do sistema
│   └── 📁 search_indexes/        # Índices de busca
│
├── 📁 config/                     # Configurações externas
│   └── requirements.txt          # Dependências Python
│
├── 📁 data/                       # Dados do sistema
│   └── price_history.db          # Histórico de preços (SQLite)
│
└── 📁 archive/                    # Arquivos arquivados
    ├── 📁 compressed_data/        # Dados comprimidos
    └── 📁 backup_old_data/        # Backup de dados antigos
```

## 🗑️ Arquivos que serão REMOVIDOS na limpeza:

### Arquivos de Teste Temporários (Raiz):
- `apply_migration.py`
- `fix_fulltext_indexes.py`
- `setup_database_v2.py`
- `setup_database_v2_simple.py`
- `test_database_v2.py`
- `test_duplicate_prevention.py`
- `test_duplicate_prevention_fixed.py`
- `update_imports.py`

### Pasta database/ (manter apenas essenciais):
- `add_unique_hash_column.sql`
- `backup_and_cleanup.py`
- `backup_and_cleanup.sql`
- `check_duplicates_only.sql`
- `check_mysql_status.py`
- `check_stats.sql`
- `check_table_structure.sql`
- `cleanup_migration_files.py`
- `fix_duplicate_prevention.sql`
- `fix_duplicate_prevention_v2.sql`
- `migration_report.txt`
- `mysql_schema_fixed.sql`
- `python_duplicate_prevention.py`
- `queries_uteis.sql`
- `quick_setup.py`
- `remove_duplicates.sql`
- `reset_database_complete.sql`
- `reset_database_simple.sql`
- `upsert_queries.sql`
- `use_url_as_unique.sql`

### Screenshots e Debug:
- `archive/screenshots/` (pasta inteira)
- `archive/debug_scripts/` (pasta inteira)
- `archive/deprecated/` (pasta inteira)
- `archive/old_logs/` (pasta inteira)

### Utils Desnecessários:
- `src/utils/database.py` (versão antiga)
- `src/utils/database_mysql_monitored.py` (versão antiga)
- `src/utils/upsert_manager.py` (incorporado no V2)
- `src/utils/hash_generator.py` (incorporado no V2)
- `src/utils/restaurant_deduplicator.py` (incorporado no V2)

### Scrapers Duplicados:
- `src/scrapers/optimized/simple_parallel_wrapper.py`

### Logs Antigos:
- Manter apenas os logs dos últimos 3 dias

### Cache Antigo:
- `cache/search_indexes/*.db` (será recriado automaticamente)

## ✅ Sistema Após Limpeza:

### 🎯 **Funcionalidades Principais:**
- ✅ Sistema de banco V2 com prevenção de duplicatas
- ✅ Rastreamento automático de preços
- ✅ Scrapers otimizados e paralelos
- ✅ Interface de usuário organizada
- ✅ Sistema de logs e monitoramento
- ✅ Ferramentas de análise e manutenção

### 🔧 **Como Usar:**
1. Execute a limpeza: `python cleanup_project.py`
2. Execute o sistema: `python main.py`
3. Use os scrapers através da interface
4. Monitore através dos logs e ferramentas

### 📊 **Benefícios:**
- 📉 **Projeto 70% menor** em tamanho
- 🚀 **Código mais limpo** e organizado
- 🔧 **Manutenção facilitada**
- 📚 **Documentação atualizada**
- 🎯 **Foco no essencial**