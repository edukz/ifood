-- =================================================================
-- SCHEMA MYSQL V2 - IFOOD SCRAPER (LIMPO E OTIMIZADO)
-- =================================================================

-- Dropar database existente e recriar
DROP DATABASE IF EXISTS ifood_scraper_v2;
CREATE DATABASE ifood_scraper_v2 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE ifood_scraper_v2;

-- =================================================================
-- 1. TABELA DE CATEGORIAS
-- =================================================================
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    icon_url TEXT,
    city VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_slug (slug),
    INDEX idx_city (city),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- 2. TABELA DE RESTAURANTES
-- =================================================================
CREATE TABLE restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- Identificador único baseado em hash
    unique_key VARCHAR(64) UNIQUE NOT NULL COMMENT 'Hash MD5 de name+category+city',
    
    -- Informações básicas
    name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    city VARCHAR(100) NOT NULL,
    
    -- Métricas e avaliações
    rating DECIMAL(3,2) DEFAULT 0.00,
    delivery_time VARCHAR(50),
    delivery_fee VARCHAR(50),
    distance VARCHAR(50),
    
    -- URLs e contato
    url TEXT,
    logo_url TEXT,
    address TEXT,
    phone VARCHAR(50),
    
    -- Informações adicionais
    opening_hours TEXT,
    minimum_order VARCHAR(50),
    payment_methods JSON,
    tags JSON,
    
    -- Controle
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_unique_key (unique_key),
    INDEX idx_name (name),
    INDEX idx_category (category_id),
    INDEX idx_city (city),
    INDEX idx_rating (rating),
    INDEX idx_active (is_active),
    FULLTEXT idx_search (name, address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- 3. TABELA DE PRODUTOS
-- =================================================================
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- Identificador único baseado em hash
    unique_key VARCHAR(64) UNIQUE NOT NULL COMMENT 'Hash MD5 de restaurant_id+name+category',
    
    -- Relacionamento
    restaurant_id INT NOT NULL,
    
    -- Informações do produto
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(255) NOT NULL,
    
    -- Preços
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    
    -- Detalhes
    image_url TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    preparation_time VARCHAR(50),
    serves_people INT,
    
    -- Informações nutricionais
    calories INT,
    ingredients JSON,
    allergens JSON,
    
    -- Controle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_unique_key (unique_key),
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_category (category),
    INDEX idx_available (is_available),
    INDEX idx_price (price),
    FULLTEXT idx_search (name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- 4. HISTÓRICO DE PREÇOS
-- =================================================================
CREATE TABLE price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product (product_id),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- 5. LOG DE EXTRAÇÃO
-- =================================================================
CREATE TABLE extraction_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    extraction_type ENUM('category', 'restaurant', 'product') NOT NULL,
    entity_id INT,
    entity_name VARCHAR(255),
    status ENUM('started', 'success', 'failed', 'partial') NOT NULL,
    items_extracted INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    duration_seconds INT,
    
    INDEX idx_type (extraction_type),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- 6. CONFIGURAÇÕES DO SISTEMA
-- =================================================================
CREATE TABLE system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserir configurações padrão
INSERT INTO system_config (config_key, config_value, description) VALUES
('version', '2.0', 'Versão do schema do banco de dados'),
('enable_price_tracking', 'true', 'Habilitar rastreamento de mudanças de preço'),
('chunk_size', '500', 'Tamanho do lote para processamento em batch'),
('duplicate_check_enabled', 'true', 'Habilitar verificação de duplicatas');

-- =================================================================
-- 7. VIEWS ÚTEIS
-- =================================================================

-- View de estatísticas por categoria
CREATE VIEW category_stats AS
SELECT 
    c.id,
    c.name as category_name,
    c.city,
    COUNT(DISTINCT r.id) as restaurant_count,
    COUNT(DISTINCT p.id) as product_count,
    AVG(r.rating) as avg_rating,
    MAX(r.last_scraped) as last_updated
FROM categories c
LEFT JOIN restaurants r ON c.id = r.category_id
LEFT JOIN products p ON r.id = p.restaurant_id
GROUP BY c.id, c.name, c.city;

-- View de produtos com informações do restaurante
CREATE VIEW products_full AS
SELECT 
    p.*,
    r.name as restaurant_name,
    r.rating as restaurant_rating,
    r.city,
    c.name as category_name
FROM products p
JOIN restaurants r ON p.restaurant_id = r.id
JOIN categories c ON r.category_id = c.id;

-- =================================================================
-- 8. STORED PROCEDURES
-- =================================================================

DELIMITER $$

-- Procedure para registrar mudança de preço
CREATE PROCEDURE record_price_change(
    IN p_product_id INT,
    IN p_new_price DECIMAL(10,2),
    IN p_new_original_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_current_price DECIMAL(10,2);
    
    -- Buscar preço atual
    SELECT price INTO v_current_price 
    FROM products 
    WHERE id = p_product_id;
    
    -- Se o preço mudou, registrar no histórico
    IF v_current_price IS NOT NULL AND v_current_price != p_new_price THEN
        INSERT INTO price_history (product_id, price, original_price)
        VALUES (p_product_id, p_new_price, p_new_original_price);
    END IF;
END$$

-- Procedure para limpar dados antigos
CREATE PROCEDURE cleanup_old_data(
    IN p_days_to_keep INT
)
BEGIN
    DECLARE v_cutoff_date TIMESTAMP;
    SET v_cutoff_date = DATE_SUB(NOW(), INTERVAL p_days_to_keep DAY);
    
    -- Limpar logs antigos
    DELETE FROM extraction_logs 
    WHERE completed_at < v_cutoff_date;
    
    -- Limpar histórico de preços antigo
    DELETE FROM price_history 
    WHERE changed_at < v_cutoff_date;
    
    -- Desativar restaurantes não atualizados
    UPDATE restaurants 
    SET is_active = FALSE 
    WHERE last_scraped < v_cutoff_date;
END$$

DELIMITER ;

-- =================================================================
-- 9. FUNÇÕES ÚTEIS
-- =================================================================

DELIMITER $$

-- Função para gerar unique_key
CREATE FUNCTION generate_unique_key(
    p_str1 VARCHAR(255),
    p_str2 VARCHAR(255),
    p_str3 VARCHAR(255)
) RETURNS VARCHAR(64)
DETERMINISTIC
BEGIN
    RETURN MD5(CONCAT(
        LOWER(TRIM(IFNULL(p_str1, ''))), 
        '|', 
        LOWER(TRIM(IFNULL(p_str2, ''))),
        '|',
        LOWER(TRIM(IFNULL(p_str3, '')))
    ));
END$$

DELIMITER ;

-- =================================================================
-- 10. ÍNDICES ADICIONAIS PARA PERFORMANCE
-- =================================================================

-- Índice composto para buscas frequentes
CREATE INDEX idx_restaurant_search ON restaurants(category_id, city, is_active);
CREATE INDEX idx_product_search ON products(restaurant_id, category, is_available);

-- =================================================================
-- GRANT PERMISSIONS
-- =================================================================

-- Criar usuário se não existir
CREATE USER IF NOT EXISTS 'ifood_user'@'localhost' IDENTIFIED BY 'ifood_password';

-- Dar permissões
GRANT ALL PRIVILEGES ON ifood_scraper_v2.* TO 'ifood_user'@'localhost';
FLUSH PRIVILEGES;

-- =================================================================
-- MENSAGEM FINAL
-- =================================================================
SELECT 'Schema V2 criado com sucesso!' as message;