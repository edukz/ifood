-- ===================================================================
-- SCRIPT PARA VERIFICAR TABELAS CRIADAS
-- ===================================================================

-- Usar o banco de dados
USE ifood_scraper_v3;

-- 1. Listar todas as tabelas
SHOW TABLES;

-- 2. Contar quantas tabelas existem
SELECT COUNT(*) as total_tabelas 
FROM information_schema.tables 
WHERE table_schema = 'ifood_scraper_v3';

-- 3. Listar tabelas com detalhes (tamanho, linhas, etc)
SELECT 
    table_name AS 'Tabela',
    table_rows AS 'Linhas',
    ROUND(data_length/1024/1024, 2) AS 'Tamanho (MB)',
    create_time AS 'Criada em'
FROM information_schema.tables
WHERE table_schema = 'ifood_scraper_v3'
ORDER BY table_name;

-- 4. Verificar estrutura de uma tabela específica (exemplo: restaurants)
DESCRIBE restaurants;

-- 5. Verificar se as views foram criadas
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'ifood_scraper_v3';

-- 6. Verificar stored procedures
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'ifood_scraper_v3' 
AND routine_type = 'PROCEDURE';

-- 7. Status geral do banco
SELECT 
    'Tabelas' as Tipo, COUNT(*) as Quantidade 
FROM information_schema.tables 
WHERE table_schema = 'ifood_scraper_v3' AND table_type = 'BASE TABLE'
UNION ALL
SELECT 
    'Views', COUNT(*) 
FROM information_schema.views 
WHERE table_schema = 'ifood_scraper_v3'
UNION ALL
SELECT 
    'Procedures', COUNT(*) 
FROM information_schema.routines 
WHERE routine_schema = 'ifood_scraper_v3' AND routine_type = 'PROCEDURE';