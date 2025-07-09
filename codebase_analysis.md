# ANÁLISE COMPLETA DO PROJETO IFOOD SCRAPER
============================================================

## RESUMO EXECUTIVO
------------------------------
📊 Total de arquivos Python: 51
📏 Total de linhas: 16,318
💻 Linhas de código: 12,412
💬 Linhas de comentário: 977
⚪ Linhas em branco: 2,929
🔴 Arquivos grandes (>500 linhas): 5
🟡 Arquivos complexos (alta complexidade): 32

## ARQUIVOS GRANDES (>500 linhas de código)
--------------------------------------------------
🔴 src/ui/system_menus.py - 2,426 linhas
🔴 src/scrapers/parallel/windows_parallel_scraper.py - 1,081 linhas
🔴 src/utils/search_optimizer.py - 583 linhas
🔴 src/utils/price_monitor.py - 561 linhas
🔴 src/scrapers/restaurant_scraper.py - 518 linhas

## ARQUIVOS COMPLEXOS (Alta complexidade)
--------------------------------------------------
🟡 src/ui/system_menus.py - Complexidade: 688
🟡 src/scrapers/parallel/windows_parallel_scraper.py - Complexidade: 242
🟡 src/scrapers/restaurant_scraper.py - Complexidade: 163
🟡 src/scrapers/product_scraper.py - Complexidade: 159
🟡 src/utils/search_optimizer.py - Complexidade: 137
🟡 src/utils/performance_monitor.py - Complexidade: 116
🟡 src/utils/price_monitor.py - Complexidade: 115
🟡 tools/archive_manager.py - Complexidade: 103
🟡 src/ui/analysis_menus.py - Complexidade: 91
🟡 analyze_codebase.py - Complexidade: 83
🟡 src/utils/product_categorizer.py - Complexidade: 82
🟡 src/database/database_manager_v2.py - Complexidade: 80
🟡 src/database/database_adapter.py - Complexidade: 79
🟡 src/ui/extraction_menus.py - Complexidade: 78
🟡 src/utils/dashboard_server.py - Complexidade: 75
🟡 tools/data_analyzer.py - Complexidade: 65
🟡 src/config/database.py - Complexidade: 64
🟡 src/utils/colors.py - Complexidade: 61
🟡 src/utils/retry_handler.py - Complexidade: 60
🟡 src/utils/error_handler.py - Complexidade: 53
🟡 src/utils/progress_tracker.py - Complexidade: 53
🟡 src/scrapers/category_scraper.py - Complexidade: 43
🟡 src/utils/task_manager.py - Complexidade: 42
🟡 tools/check_dependencies.py - Complexidade: 38
🟡 main.py - Complexidade: 37
🟡 tools/fix_categories.py - Complexidade: 37
🟡 src/scrapers/ifood_scraper.py - Complexidade: 37
🟡 src/scrapers/mock_scraper.py - Complexidade: 37
🟡 tools/cleanup_logs.py - Complexidade: 35
🟡 src/ui/base_menu.py - Complexidade: 35
🟡 src/utils/logger.py - Complexidade: 28
🟡 src/utils/human_behavior.py - Complexidade: 23

## CATEGORIA: MAIN
----------------------------------------
### analyze_codebase.py
📊 Linhas: 365 total | 270 código
🏗️  Classes: 1 | Funções: 8
🔄 Complexidade: 83
📋 Responsabilidades: User Interaction, Scraper Implementation, Browser Automation, Database Operations, Error Handling, Logging
🎯 Classes principais: CodeAnalyzer
⚙️  Funções principais: main, __init__, analyze_file, _calculate_complexity, _identify_responsibilities
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### main.py
📊 Linhas: 282 total | 226 código
🏗️  Classes: 1 | Funções: 9
🔄 Complexidade: 37
📋 Responsabilidades: User Interaction, Scraper Implementation, Database Operations, Error Handling, Logging
🎯 Classes principais: iFoodMenuSystem
⚙️  Funções principais: main, __init__, show_header, show_main_menu, run
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/__init__.py
📊 Linhas: 0 total | 0 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 0
📋 Responsabilidades: General

## CATEGORIA: TOOLS
----------------------------------------
### tools/archive_manager.py
📊 Linhas: 465 total | 355 código
🏗️  Classes: 1 | Funções: 14
🔄 Complexidade: 103
📋 Responsabilidades: Tools/Scripts, User Interaction, Error Handling, Logging
🎯 Classes principais: ArchiveManager
⚙️  Funções principais: interactive_menu, __init__, get_old_files, compress_file, create_archive
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### tools/data_analyzer.py
📊 Linhas: 286 total | 208 código
🏗️  Classes: 1 | Funções: 8
🔄 Complexidade: 65
📋 Responsabilidades: Tools/Scripts, Scraper Implementation, Error Handling
🎯 Classes principais: DataAnalyzer
⚙️  Funções principais: main, __init__, analyze_categories, analyze_restaurants, analyze_urls
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### tools/check_dependencies.py
📊 Linhas: 204 total | 153 código
🏗️  Classes: 0 | Funções: 7
🔄 Complexidade: 38
📋 Responsabilidades: Tools/Scripts, Database Operations, Error Handling, Browser Automation
⚙️  Funções principais: check_python_version, check_module, check_playwright_browsers, check_project_structure, check_permissions
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### tools/cleanup_logs.py
📊 Linhas: 172 total | 119 código
🏗️  Classes: 0 | Funções: 4
🔄 Complexidade: 35
📋 Responsabilidades: Tools/Scripts, User Interaction
⚙️  Funções principais: count_files_in_directory, cleanup_archive_logs, organize_current_logs, main
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### tools/fix_categories.py
📊 Linhas: 140 total | 96 código
🏗️  Classes: 0 | Funções: 3
🔄 Complexidade: 37
📋 Responsabilidades: Tools/Scripts
⚙️  Funções principais: fix_incorrect_category, fix_restaurant_categories, remove_incorrect_product_files
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### tools/analyze_deduplication.py
📊 Linhas: 92 total | 80 código
🏗️  Classes: 0 | Funções: 1
🔄 Complexidade: 2
📋 Responsabilidades: Tools/Scripts
⚙️  Funções principais: analyze_deduplication

### tools/migrate_data_structure.py
📊 Linhas: 97 total | 70 código
🏗️  Classes: 0 | Funções: 1
🔄 Complexidade: 15
📋 Responsabilidades: Tools/Scripts
⚙️  Funções principais: migrate_data_structure

### tools/refresh_search_indexes.py
📊 Linhas: 80 total | 53 código
🏗️  Classes: 0 | Funções: 1
🔄 Complexidade: 11
📋 Responsabilidades: Tools/Scripts, Database Operations
⚙️  Funções principais: refresh_search_indexes

### tools/check_restaurants_count.py
📊 Linhas: 65 total | 46 código
🏗️  Classes: 0 | Funções: 1
🔄 Complexidade: 5
📋 Responsabilidades: Tools/Scripts, Database Operations
⚙️  Funções principais: check_restaurants_count

## CATEGORIA: CONFIGURATION
----------------------------------------
### src/config/database.py
📊 Linhas: 343 total | 267 código
🏗️  Classes: 3 | Funções: 18
🔄 Complexidade: 64
📋 Responsabilidades: Database Operations, Configuration, Error Handling, Logging
🎯 Classes principais: MySQLConfig, DatabaseManager, CommonQueries
⚙️  Funções principais: get_db_manager, get_connection, get_cursor, execute_query, execute_many
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/config/browser_config.py
📊 Linhas: 78 total | 71 código
🏗️  Classes: 1 | Funções: 4
🔄 Complexidade: 5
📋 Responsabilidades: Browser Automation, Configuration
🎯 Classes principais: BrowserConfig
⚙️  Funções principais: get_viewport, get_user_agent, get_browser_context_options, get_launch_options

### src/config/settings.py
📊 Linhas: 45 total | 33 código
🏗️  Classes: 2 | Funções: 0
🔄 Complexidade: 2
📋 Responsabilidades: Browser Automation, Scraper Implementation, Configuration, Error Handling
🎯 Classes principais: ScraperSettings, IfoodSelectors

### src/config/__init__.py
📊 Linhas: 0 total | 0 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 0
📋 Responsabilidades: Configuration

## CATEGORIA: DATABASE
----------------------------------------
### src/database/database_manager_v2.py
📊 Linhas: 537 total | 424 código
🏗️  Classes: 2 | Funções: 21
🔄 Complexidade: 80
📋 Responsabilidades: Database Operations, Database Management, Error Handling, Logging
🎯 Classes principais: DatabaseConfig, DatabaseManagerV2
⚙️  Funções principais: get_database_manager, __init__, get_config, __init__, _init_connection_pool
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/database/database_adapter.py
📊 Linhas: 344 total | 266 código
🏗️  Classes: 1 | Funções: 21
🔄 Complexidade: 79
📋 Responsabilidades: Scraper Implementation, Database Operations, Error Handling, Logging, Database Management
🎯 Classes principais: DatabaseAdapter
⚙️  Funções principais: get_database_manager, __init__, save_categories, save_restaurants, save_products
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

## CATEGORIA: MODELS
----------------------------------------
### src/models/product.py
📊 Linhas: 45 total | 42 código
🏗️  Classes: 1 | Funções: 1
🔄 Complexidade: 6
📋 Responsabilidades: Data Models
🎯 Classes principais: Product
⚙️  Funções principais: to_dict

### src/models/restaurant.py
📊 Linhas: 39 total | 36 código
🏗️  Classes: 1 | Funções: 1
🔄 Complexidade: 4
📋 Responsabilidades: Data Models
🎯 Classes principais: Restaurant
⚙️  Funções principais: to_dict

### src/models/category.py
📊 Linhas: 34 total | 27 código
🏗️  Classes: 1 | Funções: 2
🔄 Complexidade: 6
📋 Responsabilidades: Data Models
🎯 Classes principais: Category
⚙️  Funções principais: __post_init__, to_dict

### src/models/__init__.py
📊 Linhas: 0 total | 0 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 0
📋 Responsabilidades: Data Models

## CATEGORIA: SCRAPERS
----------------------------------------
### src/scrapers/parallel/windows_parallel_scraper.py
📊 Linhas: 1465 total | 1081 código
🏗️  Classes: 1 | Funções: 33
🔄 Complexidade: 242
📋 Responsabilidades: Scraper Implementation, Web Scraping, Database Operations, Error Handling, Logging
🎯 Classes principais: WindowsParallelScraper
⚙️  Funções principais: detect_windows, __init__, extract_restaurants_parallel, _generate_restaurants_for_category, _get_restaurant_names_by_category
🔧 Recomendações: ⚠️  DIVIDIR: Arquivo muito grande | ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/scrapers/restaurant_scraper.py
📊 Linhas: 713 total | 518 código
🏗️  Classes: 3 | Funções: 13
🔄 Complexidade: 163
📋 Responsabilidades: Scraper Implementation, Web Scraping, Browser Automation, Database Operations, Error Handling, Logging
🎯 Classes principais: RestaurantScraper, Playwright, TimeoutError
⚙️  Funções principais: __init__, navigate_to_category, extract_restaurants, _scroll_to_load_restaurants, _count_restaurants_on_page
🔧 Recomendações: ⚠️  DIVIDIR: Arquivo muito grande | ⚠️  REFATORAR: Complexidade alta

### src/scrapers/product_scraper.py
📊 Linhas: 686 total | 487 código
🏗️  Classes: 1 | Funções: 19
🔄 Complexidade: 159
📋 Responsabilidades: User Interaction, Scraper Implementation, Web Scraping, Browser Automation, Database Operations, Error Handling, Logging
🎯 Classes principais: ProductScraper
⚙️  Funções principais: __init__, navigate_to_restaurant, _wait_for_products_to_load, extract_products, _scroll_to_load_all_products
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/scrapers/mock_scraper.py
📊 Linhas: 332 total | 246 código
🏗️  Classes: 1 | Funções: 6
🔄 Complexidade: 37
📋 Responsabilidades: Browser Automation, Scraper Implementation, Web Scraping, Logging
🎯 Classes principais: MockScraper
⚙️  Funções principais: create_mock_data_files, __init__, simulate_category_extraction, simulate_restaurant_extraction, simulate_product_extraction
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/scrapers/ifood_scraper.py
📊 Linhas: 226 total | 168 código
🏗️  Classes: 1 | Funções: 5
🔄 Complexidade: 37
📋 Responsabilidades: User Interaction, Scraper Implementation, Web Scraping, Browser Automation, Database Operations, Error Handling, Logging
🎯 Classes principais: IfoodScraper
⚙️  Funções principais: __init__, navigate, extract_data, save_data, run
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/scrapers/category_scraper.py
📊 Linhas: 220 total | 163 código
🏗️  Classes: 3 | Funções: 4
🔄 Complexidade: 43
📋 Responsabilidades: User Interaction, Scraper Implementation, Web Scraping, Browser Automation, Database Operations, Error Handling, Logging
🎯 Classes principais: CategoryScraper, Playwright, TimeoutError
⚙️  Funções principais: __init__, extract_categories, save_categories, run
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/scrapers/base.py
📊 Linhas: 93 total | 72 código
🏗️  Classes: 1 | Funções: 6
🔄 Complexidade: 10
📋 Responsabilidades: Scraper Implementation, Web Scraping, Browser Automation, Error Handling, Logging
🎯 Classes principais: BaseScraper
⚙️  Funções principais: __init__, navigate, extract_data, setup_browser, wait_with_random_actions

### src/scrapers/optimized/__init__.py
📊 Linhas: 11 total | 9 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 0
📋 Responsabilidades: Web Scraping

### src/scrapers/parallel/__init__.py
📊 Linhas: 9 total | 7 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 0
📋 Responsabilidades: Web Scraping

### src/scrapers/__init__.py
📊 Linhas: 0 total | 0 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 0
📋 Responsabilidades: Web Scraping

## CATEGORIA: USER INTERFACE
----------------------------------------
### src/ui/system_menus.py
📊 Linhas: 3099 total | 2426 código
🏗️  Classes: 1 | Funções: 83
🔄 Complexidade: 688
📋 Responsabilidades: User Interaction, Scraper Implementation, Browser Automation, Database Operations, User Interface, Error Handling, Logging
🎯 Classes principais: SystemMenus
⚙️  Funções principais: __init__, check_categories_status, menu_parallel_execution, _parallel_categories, _analyze_existing_categories
🔧 Recomendações: ⚠️  DIVIDIR: Arquivo muito grande | ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/ui/analysis_menus.py
📊 Linhas: 396 total | 309 código
🏗️  Classes: 1 | Funções: 17
🔄 Complexidade: 91
📋 Responsabilidades: User Interface, User Interaction, Error Handling
🎯 Classes principais: AnalysisMenus
⚙️  Funções principais: __init__, menu_product_categorizer, _categorize_csv_file, _test_product_categorization, _analyze_category_distribution
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/ui/extraction_menus.py
📊 Linhas: 408 total | 309 código
🏗️  Classes: 1 | Funções: 9
🔄 Complexidade: 78
📋 Responsabilidades: User Interaction, Scraper Implementation, Browser Automation, Database Operations, User Interface, Error Handling, Logging
🎯 Classes principais: ExtractionMenus
⚙️  Funções principais: __init__, menu_scrapy_unitario, menu_extract_categories, menu_extract_restaurants, menu_extract_products
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/ui/base_menu.py
📊 Linhas: 141 total | 111 código
🏗️  Classes: 1 | Funções: 16
🔄 Complexidade: 35
📋 Responsabilidades: User Interface, User Interaction, Error Handling, Logging
🎯 Classes principais: BaseMenu
⚙️  Funções principais: __init__, show_header, show_menu, get_user_choice, show_invalid_option
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/ui/__init__.py
📊 Linhas: 1 total | 0 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 1
📋 Responsabilidades: User Interface

## CATEGORIA: UTILITIES
----------------------------------------
### src/utils/search_optimizer.py
📊 Linhas: 743 total | 583 código
🏗️  Classes: 2 | Funções: 15
🔄 Complexidade: 137
📋 Responsabilidades: User Interaction, Database Operations, Utility Functions, Error Handling, Logging
🎯 Classes principais: SearchIndex, QueryOptimizer
⚙️  Funções principais: create_search_cli, __init__, create_database_indexes, load_data_to_database, _load_csv_to_table
🔧 Recomendações: ⚠️  DIVIDIR: Arquivo muito grande | ⚠️  REFATORAR: Complexidade alta

### src/utils/price_monitor.py
📊 Linhas: 706 total | 561 código
🏗️  Classes: 4 | Funções: 14
🔄 Complexidade: 115
📋 Responsabilidades: User Interaction, Database Operations, Utility Functions, Error Handling, Logging
🎯 Classes principais: PriceEntry, PriceChange, PriceStats
⚙️  Funções principais: create_price_monitor_cli, __init__, _init_database, add_price_entry, _record_price_change
🔧 Recomendações: ⚠️  DIVIDIR: Arquivo muito grande | ⚠️  REFATORAR: Complexidade alta | 💡 MODULARIZAR: Muitas classes

### src/utils/performance_monitor.py
📊 Linhas: 640 total | 485 código
🏗️  Classes: 5 | Funções: 26
🔄 Complexidade: 116
📋 Responsabilidades: Database Operations, Utility Functions, Error Handling, Logging
🎯 Classes principais: PerformanceMetric, AlertRule, PerformanceCollector
⚙️  Funções principais: monitor_performance, to_dict, check, __init__, record_metric
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 MODULARIZAR: Muitas classes | 💡 ORGANIZAR: Muitas funções

### src/utils/product_categorizer.py
📊 Linhas: 554 total | 429 código
🏗️  Classes: 3 | Funções: 13
🔄 Complexidade: 82
📋 Responsabilidades: User Interaction, Utility Functions, Error Handling, Logging
🎯 Classes principais: ProductCategory, CategoryResult, ProductCategorizer
⚙️  Funções principais: create_categorization_cli, __init__, _load_default_categories, _load_config, save_config
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/utils/dashboard_server.py
📊 Linhas: 357 total | 294 código
🏗️  Classes: 2 | Funções: 13
🔄 Complexidade: 75
📋 Responsabilidades: Scraper Implementation, Database Operations, Utility Functions, Error Handling, Logging
🎯 Classes principais: DashboardHandler, DashboardServer
⚙️  Funções principais: do_GET, _serve_dashboard, _serve_metrics, _serve_stats, _serve_alerts
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/utils/retry_handler.py
📊 Linhas: 370 total | 271 código
🏗️  Classes: 5 | Funções: 15
🔄 Complexidade: 60
📋 Responsabilidades: Database Operations, Utility Functions, Error Handling, Logging
🎯 Classes principais: RetryError, CircuitBreakerError, RetryConfig
⚙️  Funções principais: classify_mysql_error, retry_mysql_operation, __init__, calculate_delay, __init__
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 MODULARIZAR: Muitas classes

### src/utils/colors.py
📊 Linhas: 309 total | 232 código
🏗️  Classes: 2 | Funções: 26
🔄 Complexidade: 61
📋 Responsabilidades: Utility Functions, Error Handling
🎯 Classes principais: Colors, ColorPrinter
⚙️  Funções principais: print_success, print_error, print_warning, print_info, print_action
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 ORGANIZAR: Muitas funções

### src/utils/progress_tracker.py
📊 Linhas: 318 total | 229 código
🏗️  Classes: 5 | Funções: 13
🔄 Complexidade: 53
📋 Responsabilidades: Utility Functions, Error Handling, Logging
🎯 Classes principais: ProgressStats, ProgressTracker, ConsoleProgressCallback
⚙️  Funções principais: __str__, _format_time, __init__, update, is_complete
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 MODULARIZAR: Muitas classes

### src/utils/error_handler.py
📊 Linhas: 263 total | 187 código
🏗️  Classes: 5 | Funções: 10
🔄 Complexidade: 53
📋 Responsabilidades: Scraper Implementation, Browser Automation, Utility Functions, Error Handling, Logging
🎯 Classes principais: ScraperError, ElementNotFoundError, NavigationError
⚙️  Funções principais: with_retry, safe_click, safe_fill, validate_page_loaded, __init__
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta | 💡 MODULARIZAR: Muitas classes

### src/utils/task_manager.py
📊 Linhas: 172 total | 140 código
🏗️  Classes: 3 | Funções: 12
🔄 Complexidade: 42
📋 Responsabilidades: Utility Functions, Error Handling
🎯 Classes principais: Task, TaskManager, BatchProcessor
⚙️  Funções principais: __lt__, to_dict, __init__, add_task, get_next_task
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/utils/logger.py
📊 Linhas: 183 total | 112 código
🏗️  Classes: 1 | Funções: 8
🔄 Complexidade: 28
📋 Responsabilidades: Utility Functions, Scraper Implementation, Error Handling, Logging
🎯 Classes principais: ColoredFormatter
⚙️  Funções principais: get_log_filename, setup_file_handler, setup_logger, cleanup_old_logs, get_current_log_file
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/utils/human_behavior.py
📊 Linhas: 123 total | 88 código
🏗️  Classes: 1 | Funções: 8
🔄 Complexidade: 23
📋 Responsabilidades: Browser Automation, Utility Functions
🎯 Classes principais: HumanBehavior
⚙️  Funções principais: random_delay, typing_delay, random_mouse_movement, random_scroll, human_type
🔧 Recomendações: ⚠️  REFATORAR: Complexidade alta

### src/utils/helpers.py
📊 Linhas: 67 total | 53 código
🏗️  Classes: 0 | Funções: 5
🔄 Complexidade: 15
📋 Responsabilidades: Database Operations, Utility Functions, Error Handling
⚙️  Funções principais: ensure_directories, save_to_mysql, save_to_csv, wait_and_retry, wrapper

### src/utils/__init__.py
📊 Linhas: 0 total | 0 código
🏗️  Classes: 0 | Funções: 0
🔄 Complexidade: 0
📋 Responsabilidades: Utility Functions

## DEPENDÊNCIAS MAIS UTILIZADAS
----------------------------------------
📦 typing - usado em 32 arquivos
📦 datetime - usado em 31 arquivos
📦 pathlib - usado em 20 arquivos
📦 src.config.settings - usado em 20 arquivos
📦 os - usado em 16 arquivos
📦 time - usado em 16 arquivos
📦 src.utils.logger - usado em 15 arquivos
📦 src.database.database_adapter - usado em 15 arquivos
📦 playwright.sync_api - usado em 15 arquivos
📦 json - usado em 13 arquivos

## SUGESTÕES DE REFATORAÇÃO
----------------------------------------
### 🔴 PRIORIDADE ALTA - Arquivos Grandes
• src/ui/system_menus.py (2426 linhas)
  💡 Sugestão: Dividir em módulos menores
• src/scrapers/parallel/windows_parallel_scraper.py (1081 linhas)
  💡 Sugestão: Dividir em módulos menores
• src/utils/search_optimizer.py (583 linhas)
  💡 Sugestão: Dividir em módulos menores
• src/utils/price_monitor.py (561 linhas)
  💡 Sugestão: Dividir em módulos menores
• src/scrapers/restaurant_scraper.py (518 linhas)
  💡 Sugestão: Dividir em módulos menores
### 🟡 PRIORIDADE MÉDIA - Arquivos Complexos
• src/ui/system_menus.py (complexidade 688)
  💡 Sugestão: Simplificar lógica, extrair funções
• src/scrapers/parallel/windows_parallel_scraper.py (complexidade 242)
  💡 Sugestão: Simplificar lógica, extrair funções
• src/scrapers/restaurant_scraper.py (complexidade 163)
  💡 Sugestão: Simplificar lógica, extrair funções
• src/scrapers/product_scraper.py (complexidade 159)
  💡 Sugestão: Simplificar lógica, extrair funções
• src/utils/search_optimizer.py (complexidade 137)
  💡 Sugestão: Simplificar lógica, extrair funções
### 💡 OPORTUNIDADES DE OTIMIZAÇÃO
• Consolidar funções duplicadas
• Remover código morto
• Padronizar tratamento de erros
• Implementar testes unitários
• Documentar APIs principais