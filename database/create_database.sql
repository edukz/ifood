-- ===================================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS IFOOD SCRAPER V3
-- ===================================================================

-- Dropar banco se existir e criar novo
DROP DATABASE IF EXISTS ifood_scraper_v3;
CREATE DATABASE ifood_scraper_v3 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE ifood_scraper_v3;

-- ===================================================================
-- 1. TABELA DE CATEGORIAS
-- ===================================================================
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

-- ===================================================================
-- 2. TABELA DE RESTAURANTES
-- ===================================================================
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

-- ===================================================================
-- 3. TABELA DE PRODUTOS
-- ===================================================================
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

-- ===================================================================
-- 4. HISTÓRICO DE PREÇOS
-- ===================================================================
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

-- ===================================================================
-- 5. TABELA DE DETALHES DOS RESTAURANTES (Reviews e Info Extra)
-- ===================================================================
CREATE TABLE restaurant_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT UNIQUE NOT NULL,
    
    -- Estatísticas gerais
    total_reviews INT DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    
    -- Informações detalhadas
    description TEXT,
    specialties JSON,
    amenities JSON,
    cuisine_types JSON,
    
    -- Horários detalhados por dia
    schedule_monday VARCHAR(50),
    schedule_tuesday VARCHAR(50),
    schedule_wednesday VARCHAR(50),
    schedule_thursday VARCHAR(50),
    schedule_friday VARCHAR(50),
    schedule_saturday VARCHAR(50),
    schedule_sunday VARCHAR(50),
    
    -- Controle
    has_reviews BOOLEAN DEFAULT FALSE,
    has_schedule BOOLEAN DEFAULT FALSE,
    last_review_scraped TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_has_reviews (has_reviews),
    INDEX idx_has_schedule (has_schedule)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- 6. TABELA DE REVIEWS/AVALIAÇÕES
-- ===================================================================
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    
    -- Informações do review
    reviewer_name VARCHAR(255),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_date DATE,
    
    -- Metadados
    is_verified BOOLEAN DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    
    -- Controle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_rating (rating),
    INDEX idx_review_date (review_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================================
-- 7. LOG DE EXTRAÇÃO
-- ===================================================================
CREATE TABLE extraction_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    extraction_type ENUM('category', 'restaurant', 'product', 'review', 'detail') NOT NULL,
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

-- ===================================================================
-- 8. CONFIGURAÇÕES DO SISTEMA
-- ===================================================================
CREATE TABLE system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserir configurações padrão
INSERT INTO system_config (config_key, config_value, description) VALUES
('version', '3.0', 'Versão do schema do banco de dados'),
('enable_price_tracking', 'true', 'Habilitar rastreamento de mudanças de preço'),
('chunk_size', '500', 'Tamanho do lote para processamento em batch'),
('duplicate_check_enabled', 'true', 'Habilitar verificação de duplicatas'),
('review_scraping_enabled', 'true', 'Habilitar coleta de reviews'),
('max_reviews_per_restaurant', '100', 'Número máximo de reviews por restaurante');

-- ===================================================================
-- 9. VIEWS ÚTEIS
-- ===================================================================

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

-- View de restaurantes com detalhes completos
CREATE VIEW restaurants_full AS
SELECT 
    r.*,
    c.name as category_name,
    rd.total_reviews,
    rd.has_reviews,
    rd.has_schedule,
    rd.last_review_scraped,
    (SELECT COUNT(*) FROM products WHERE restaurant_id = r.id) as product_count
FROM restaurants r
JOIN categories c ON r.category_id = c.id
LEFT JOIN restaurant_details rd ON r.id = rd.restaurant_id;

-- ===================================================================
-- 10. STORED PROCEDURES
-- ===================================================================

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

-- Procedure para obter estatísticas de scraping
CREATE PROCEDURE get_scraping_stats(
    IN p_days INT
)
BEGIN
    SELECT 
        COUNT(DISTINCT CASE WHEN rd.id IS NOT NULL THEN r.id END) as restaurants_with_details,
        COUNT(DISTINCT CASE WHEN rd.has_schedule = TRUE THEN r.id END) as restaurants_with_schedules,
        COUNT(DISTINCT CASE WHEN rd.has_reviews = TRUE THEN r.id END) as restaurants_with_reviews,
        COUNT(DISTINCT rv.id) as total_reviews,
        MAX(rd.updated_at) as last_detail_update,
        MAX(rd.last_review_scraped) as last_review_scraped
    FROM restaurants r
    LEFT JOIN restaurant_details rd ON r.id = rd.restaurant_id
    LEFT JOIN reviews rv ON r.id = rv.restaurant_id
    WHERE r.created_at >= DATE_SUB(NOW(), INTERVAL p_days DAY);
END$$

DELIMITER ;

-- ===================================================================
-- 11. FUNÇÕES ÚTEIS
-- ===================================================================

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

-- ===================================================================
-- 12. CRIAR USUÁRIO E PERMISSÕES
-- ===================================================================

-- Criar usuário se não existir
CREATE USER IF NOT EXISTS 'ifood_user'@'localhost' IDENTIFIED BY 'ifood_password';
CREATE USER IF NOT EXISTS 'ifood_user'@'%' IDENTIFIED BY 'ifood_password';

-- Dar permissões
GRANT ALL PRIVILEGES ON ifood_scraper_v3.* TO 'ifood_user'@'localhost';
GRANT ALL PRIVILEGES ON ifood_scraper_v3.* TO 'ifood_user'@'%';
FLUSH PRIVILEGES;

-- ===================================================================
-- MENSAGEM FINAL
-- ===================================================================
SELECT 'Banco de dados ifood_scraper_v3 criado com sucesso!' as message;