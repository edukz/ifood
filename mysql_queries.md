# 🗄️ Consultas MySQL - iFood Scraper Database

## 📌 Conexão ao MySQL

### Via Terminal:
```bash
mysql -h localhost -u ifood_user -p ifood_scraper_v2
```

### Credenciais padrão:
- **Host**: localhost
- **Porta**: 3306
- **Usuário**: ifood_user
- **Senha**: ifood_password
- **Database**: ifood_scraper_v2

## 📊 Queries Essenciais - Visão Geral dos Dados

### 1. **RESUMO GERAL (Estatísticas Principais)**
```sql
-- Visão geral de todos os dados salvos
SELECT 
    'Categorias' as tabela,
    COUNT(*) as total,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as ativos,
    DATE(MAX(created_at)) as ultima_atualizacao
FROM categories
UNION ALL
SELECT 
    'Restaurantes' as tabela,
    COUNT(*) as total,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as ativos,
    DATE(MAX(created_at)) as ultima_atualizacao
FROM restaurants
UNION ALL
SELECT 
    'Produtos' as tabela,
    COUNT(*) as total,
    COUNT(CASE WHEN is_available = TRUE THEN 1 END) as ativos,
    DATE(MAX(created_at)) as ultima_atualizacao
FROM products;
```

### 2. **DADOS RECENTES (Últimas 24 horas)**
```sql
-- Tudo que foi salvo nas últimas 24 horas
SELECT 
    'Categoria' as tipo,
    name,
    city,
    created_at
FROM categories 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'Restaurante' as tipo,
    name,
    city,
    created_at
FROM restaurants 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'Produto' as tipo,
    CONCAT(name, ' - R$ ', price) as name,
    '' as city,
    created_at
FROM products 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY created_at DESC;
```

### 3. **VISÃO CONSOLIDADA (Categoria → Restaurante → Produto)**
```sql
-- Dados completos: categoria → restaurante → produtos
SELECT 
    c.name as categoria,
    r.name as restaurante,
    r.city,
    r.rating,
    COUNT(p.id) as total_produtos,
    COALESCE(AVG(p.price), 0) as preco_medio,
    r.created_at as restaurante_criado
FROM categories c
JOIN restaurants r ON c.id = r.category_id
LEFT JOIN products p ON r.id = p.restaurant_id
WHERE c.is_active = TRUE AND r.is_active = TRUE
GROUP BY c.id, r.id
ORDER BY c.name, r.name
LIMIT 50;
```

### 4. **ANÁLISE POR CIDADE**
```sql
-- Estatísticas completas por cidade
SELECT 
    city,
    COUNT(DISTINCT c.id) as categorias,
    COUNT(DISTINCT r.id) as restaurantes,
    COUNT(p.id) as produtos,
    AVG(r.rating) as rating_medio,
    MIN(r.created_at) as primeiro_scraping,
    MAX(r.last_scraped) as ultimo_scraping
FROM categories c
JOIN restaurants r ON c.id = r.category_id
LEFT JOIN products p ON r.id = p.restaurant_id
GROUP BY city
ORDER BY restaurantes DESC;
```

### 5. **TOP CATEGORIAS (Mais Populares)**
```sql
-- Categorias com mais restaurantes e produtos
SELECT 
    c.name as categoria,
    COUNT(DISTINCT r.id) as total_restaurantes,
    COUNT(p.id) as total_produtos,
    AVG(r.rating) as rating_medio,
    COALESCE(AVG(p.price), 0) as preco_medio_produtos
FROM categories c
JOIN restaurants r ON c.id = r.category_id
LEFT JOIN products p ON r.id = p.restaurant_id
WHERE c.is_active = TRUE AND r.is_active = TRUE
GROUP BY c.id, c.name
ORDER BY total_restaurantes DESC
LIMIT 20;
```

### 6. **TOP RESTAURANTES (Mais Produtos)**
```sql
-- Restaurantes com mais produtos salvos
SELECT 
    r.name as restaurante,
    c.name as categoria,
    r.city,
    r.rating,
    COUNT(p.id) as total_produtos,
    COALESCE(AVG(p.price), 0) as preco_medio,
    r.created_at
FROM restaurants r
JOIN categories c ON r.category_id = c.id
LEFT JOIN products p ON r.id = p.restaurant_id
WHERE r.is_active = TRUE
GROUP BY r.id
ORDER BY total_produtos DESC
LIMIT 20;
```

## 📊 Queries Úteis para Restaurantes

### 1. Ver todos os restaurantes (limitado a 20):
```sql
SELECT 
    r.id,
    r.name AS nome,
    r.city AS cidade,
    c.name AS categoria,
    r.rating AS nota,
    r.delivery_time AS tempo_entrega,
    r.delivery_fee AS taxa_entrega,
    r.last_scraped AS ultima_coleta
FROM restaurants r
LEFT JOIN categories c ON r.category_id = c.id
WHERE r.is_active = TRUE
ORDER BY r.rating DESC
LIMIT 20;
```

### 2. Contar total de restaurantes:
```sql
SELECT COUNT(*) AS total_restaurantes 
FROM restaurants 
WHERE is_active = TRUE;
```

### 3. Restaurantes por categoria:
```sql
SELECT 
    c.name AS categoria,
    COUNT(r.id) AS total,
    AVG(r.rating) AS nota_media,
    MIN(r.rating) AS nota_minima,
    MAX(r.rating) AS nota_maxima
FROM categories c
LEFT JOIN restaurants r ON c.id = r.category_id
WHERE r.is_active = TRUE
GROUP BY c.id, c.name
ORDER BY total DESC;
```

### 4. Top 10 restaurantes por nota:
```sql
SELECT 
    name AS restaurante,
    rating AS nota,
    delivery_time AS tempo_entrega,
    delivery_fee AS taxa,
    city AS cidade
FROM restaurants
WHERE is_active = TRUE AND rating > 0
ORDER BY rating DESC, name
LIMIT 10;
```

### 5. Buscar restaurante por nome:
```sql
SELECT * FROM restaurants 
WHERE name LIKE '%pizza%' 
AND is_active = TRUE
ORDER BY rating DESC;
```

### 6. Restaurantes por cidade:
```sql
SELECT 
    city AS cidade,
    COUNT(*) AS total,
    AVG(rating) AS nota_media
FROM restaurants
WHERE is_active = TRUE
GROUP BY city
ORDER BY total DESC;
```

### 7. Estatísticas gerais:
```sql
SELECT 
    COUNT(DISTINCT r.id) AS total_restaurantes,
    COUNT(DISTINCT c.id) AS total_categorias,
    COUNT(DISTINCT r.city) AS total_cidades,
    AVG(r.rating) AS nota_media_geral,
    MIN(r.created_at) AS primeira_coleta,
    MAX(r.last_scraped) AS ultima_atualizacao
FROM restaurants r
LEFT JOIN categories c ON r.category_id = c.id
WHERE r.is_active = TRUE;
```

### 8. Restaurantes com melhores taxas de entrega:
```sql
SELECT 
    name,
    delivery_fee,
    rating,
    delivery_time
FROM restaurants
WHERE is_active = TRUE 
    AND delivery_fee IS NOT NULL
    AND delivery_fee NOT LIKE '%Grátis%'
ORDER BY CAST(REPLACE(REPLACE(delivery_fee, 'R$ ', ''), ',', '.') AS DECIMAL(10,2))
LIMIT 20;
```

### 9. Ver detalhes completos de um restaurante:
```sql
SELECT 
    r.*,
    c.name AS categoria_nome
FROM restaurants r
LEFT JOIN categories c ON r.category_id = c.id
WHERE r.name = 'Nome do Restaurante'
AND r.is_active = TRUE;
```

### 10. Restaurantes mais recentes (últimas 24h):
```sql
SELECT 
    r.name,
    c.name AS categoria,
    r.rating,
    r.created_at
FROM restaurants r
LEFT JOIN categories c ON r.category_id = c.id
WHERE r.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
AND r.is_active = TRUE
ORDER BY r.created_at DESC;
```

### 11. Duplicatas potenciais (mesmo nome):
```sql
SELECT 
    name,
    COUNT(*) as quantidade,
    GROUP_CONCAT(DISTINCT city) as cidades,
    GROUP_CONCAT(DISTINCT category_id) as categorias
FROM restaurants
WHERE is_active = TRUE
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY quantidade DESC;
```

### 12. Exportar para CSV direto do MySQL:
```sql
SELECT 
    r.id,
    r.name,
    r.city,
    c.name AS category,
    r.rating,
    r.delivery_time,
    r.delivery_fee,
    r.distance,
    r.address,
    r.phone,
    r.url,
    r.last_scraped
FROM restaurants r
LEFT JOIN categories c ON r.category_id = c.id
WHERE r.is_active = TRUE
INTO OUTFILE '/tmp/restaurantes_export.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

## 🔍 Queries Avançadas

### Ver relacionamento categoria-restaurante:
```sql
SELECT 
    c.name AS categoria,
    r.name AS restaurante,
    r.rating,
    r.unique_key
FROM restaurants r
INNER JOIN categories c ON r.category_id = c.id
WHERE c.name IN ('Pizza', 'Italiana')
ORDER BY c.name, r.rating DESC;
```

### Análise de horários de funcionamento:
```sql
SELECT 
    name,
    opening_hours,
    CASE 
        WHEN opening_hours LIKE '%24h%' THEN '24 horas'
        WHEN opening_hours IS NULL THEN 'Não informado'
        ELSE 'Horário específico'
    END AS tipo_horario
FROM restaurants
WHERE is_active = TRUE
LIMIT 20;
```

### Produtos por restaurante (se você tiver extraído produtos):
```sql
SELECT 
    r.name AS restaurante,
    COUNT(p.id) AS total_produtos,
    AVG(p.price) AS preco_medio
FROM restaurants r
LEFT JOIN products p ON r.id = p.restaurant_id
WHERE r.is_active = TRUE AND p.is_available = TRUE
GROUP BY r.id, r.name
HAVING COUNT(p.id) > 0
ORDER BY total_produtos DESC
LIMIT 20;
```

## 🔥 Queries Avançadas para Análise

### 1. **PRODUTOS MAIS CAROS POR CATEGORIA**
```sql
-- Top 5 produtos mais caros de cada categoria
SELECT 
    c.name as categoria,
    r.name as restaurante,
    p.name as produto,
    p.price as preco,
    p.description
FROM products p
JOIN restaurants r ON p.restaurant_id = r.id
JOIN categories c ON r.category_id = c.id
WHERE p.is_available = TRUE AND p.price > 0
ORDER BY c.name, p.price DESC;
```

### 2. **ANÁLISE DE PREÇOS (Estatísticas)**
```sql
-- Estatísticas de preços por categoria de produto
SELECT 
    p.category as categoria_produto,
    COUNT(*) as total_produtos,
    MIN(p.price) as preco_min,
    MAX(p.price) as preco_max,
    AVG(p.price) as preco_medio,
    STDDEV(p.price) as desvio_padrao
FROM products p
WHERE p.is_available = TRUE AND p.price > 0
GROUP BY p.category
ORDER BY preco_medio DESC;
```

### 3. **HISTÓRICO DE PREÇOS (Se tiver)**
```sql
-- Produtos com mudança de preço
SELECT 
    p.name as produto,
    r.name as restaurante,
    p.price as preco_atual,
    ph.price as preco_anterior,
    ph.changed_at as data_mudanca,
    ROUND(((p.price - ph.price) / ph.price) * 100, 2) as percentual_mudanca
FROM products p
JOIN restaurants r ON p.restaurant_id = r.id
JOIN price_history ph ON p.id = ph.product_id
WHERE p.price != ph.price
ORDER BY percentual_mudanca DESC
LIMIT 20;
```

### 4. **BUSCA AVANÇADA (Full-text)**
```sql
-- Busca por nome ou descrição de produto
SELECT 
    p.name as produto,
    r.name as restaurante,
    c.name as categoria,
    p.price,
    p.description,
    MATCH(p.name, p.description) AGAINST('pizza margherita' IN BOOLEAN MODE) as relevancia
FROM products p
JOIN restaurants r ON p.restaurant_id = r.id
JOIN categories c ON r.category_id = c.id
WHERE MATCH(p.name, p.description) AGAINST('pizza margherita' IN BOOLEAN MODE)
ORDER BY relevancia DESC
LIMIT 20;
```

### 5. **ANÁLISE DE PERFORMANCE DOS SCRAPERS**
```sql
-- Logs de extração por tipo
SELECT 
    extraction_type as tipo,
    status,
    COUNT(*) as total,
    AVG(duration_seconds) as tempo_medio_seg,
    SUM(items_extracted) as items_totais,
    MAX(started_at) as ultima_execucao
FROM extraction_logs
GROUP BY extraction_type, status
ORDER BY extraction_type, status;
```

### 6. **MONITORAMENTO DE DUPLICATAS**
```sql
-- Verificar possíveis duplicatas por unique_key
SELECT 
    unique_key,
    COUNT(*) as duplicatas,
    GROUP_CONCAT(name SEPARATOR ' | ') as nomes,
    GROUP_CONCAT(city SEPARATOR ' | ') as cidades
FROM restaurants
GROUP BY unique_key
HAVING COUNT(*) > 1
ORDER BY duplicatas DESC;
```

### 7. **EXPORT CUSTOMIZADO (CSV)**
```sql
-- Exportar dados consolidados para análise
SELECT 
    c.name as categoria,
    r.name as restaurante,
    r.city as cidade,
    r.rating as nota,
    r.delivery_time as tempo_entrega,
    r.delivery_fee as taxa_entrega,
    r.distance as distancia,
    COUNT(p.id) as total_produtos,
    COALESCE(AVG(p.price), 0) as preco_medio_produtos,
    r.created_at as data_scraping
FROM categories c
JOIN restaurants r ON c.id = r.category_id
LEFT JOIN products p ON r.id = p.restaurant_id
WHERE c.is_active = TRUE AND r.is_active = TRUE
GROUP BY c.id, r.id
ORDER BY c.name, r.rating DESC
-- Adicione: INTO OUTFILE '/tmp/dados_completos.csv' etc.
```

## 🎯 Queries para Troubleshooting

### 1. **Verificar Integridade dos Dados**
```sql
-- Verificar relacionamentos quebrados
SELECT 
    'Restaurantes sem categoria' as problema,
    COUNT(*) as total
FROM restaurants r
LEFT JOIN categories c ON r.category_id = c.id
WHERE c.id IS NULL
UNION ALL
SELECT 
    'Produtos sem restaurante' as problema,
    COUNT(*) as total
FROM products p
LEFT JOIN restaurants r ON p.restaurant_id = r.id
WHERE r.id IS NULL;
```

### 2. **Limpeza de Dados**
```sql
-- Encontrar registros com dados incompletos
SELECT 
    'Restaurantes sem nome' as problema,
    COUNT(*) as total
FROM restaurants
WHERE name IS NULL OR name = ''
UNION ALL
SELECT 
    'Produtos sem preço' as problema,
    COUNT(*) as total
FROM products
WHERE price IS NULL OR price = 0;
```

## 💡 Dicas

1. **Performance**: Sempre use `LIMIT` em queries exploratórias
2. **Índices**: As colunas `unique_key`, `name`, `city` e `category_id` têm índices
3. **Encoding**: O banco usa `utf8mb4` para suportar emojis e caracteres especiais
4. **Timezone**: Timestamps estão em UTC

## 🛠️ Ferramentas GUI para MySQL

- **MySQL Workbench**: Interface oficial do MySQL
- **DBeaver**: Multiplataforma e gratuito
- **phpMyAdmin**: Interface web
- **HeidiSQL**: Windows, leve e rápido
- **TablePlus**: macOS/Windows, moderno

Para conectar com qualquer ferramenta, use as credenciais acima.