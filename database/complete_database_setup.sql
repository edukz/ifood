-- ===================================================================
-- COMPLETAR CRIAÇÃO DAS TABELAS FALTANTES
-- ===================================================================

USE ifood_scraper_v3;

-- Verificar quais tabelas já existem
SHOW TABLES;

-- ===================================================================
-- 4. HISTÓRICO DE PREÇOS (se não existe)
-- ===================================================================
CREATE TABLE IF NOT EXISTS price_history (
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
-- 5. TABELA DE DETALHES DOS RESTAURANTES
-- ===================================================================
CREATE TABLE IF NOT EXISTS restaurant_details (
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
CREATE TABLE IF NOT EXISTS reviews (
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
CREATE TABLE IF NOT EXISTS extraction_logs (
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
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserir configurações padrão (se não existirem)
INSERT IGNORE INTO system_config (config_key, config_value, description) VALUES
('version', '3.0', 'Versão do schema do banco de dados'),
('enable_price_tracking', 'true', 'Habilitar rastreamento de mudanças de preço'),
('chunk_size', '500', 'Tamanho do lote para processamento em batch'),
('duplicate_check_enabled', 'true', 'Habilitar verificação de duplicatas'),
('review_scraping_enabled', 'true', 'Habilitar coleta de reviews'),
('max_reviews_per_restaurant', '100', 'Número máximo de reviews por restaurante');

-- ===================================================================
-- CRIAR/ATUALIZAR PERMISSÕES DO USUÁRIO
-- ===================================================================

-- Recriar usuário com permissões corretas
DROP USER IF EXISTS 'ifood_user'@'localhost';
DROP USER IF EXISTS 'ifood_user'@'%';

CREATE USER 'ifood_user'@'localhost' IDENTIFIED BY 'ifood_password';
CREATE USER 'ifood_user'@'%' IDENTIFIED BY 'ifood_password';

-- Dar todas as permissões
GRANT ALL PRIVILEGES ON ifood_scraper_v3.* TO 'ifood_user'@'localhost';
GRANT ALL PRIVILEGES ON ifood_scraper_v3.* TO 'ifood_user'@'%';

-- Aplicar mudanças
FLUSH PRIVILEGES;

-- Verificar resultado final
SHOW TABLES;
SELECT 'Setup completo! Tabelas criadas e permissões configuradas.' as Status;