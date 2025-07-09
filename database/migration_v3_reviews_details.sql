-- =================================================================
-- MIGRATION V3 - ADICIONAR REVIEWS E DETALHES
-- =================================================================
-- Este script adiciona as novas tabelas para armazenar:
-- - Detalhes completos do restaurante (descrição, endereço, CNPJ)
-- - Horários de funcionamento
-- - Avaliações dos clientes
-- - Resumo de avaliações
-- =================================================================

USE ifood_scraper_v2;

-- =================================================================
-- 1. TABELA DE DETALHES DO RESTAURANTE
-- =================================================================
CREATE TABLE IF NOT EXISTS restaurant_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT UNIQUE NOT NULL,
    
    -- Descrição completa
    full_description TEXT COMMENT 'Descrição completa do restaurante',
    
    -- Endereço detalhado
    street_address VARCHAR(255) COMMENT 'Rua e número',
    city VARCHAR(100) COMMENT 'Cidade',
    state VARCHAR(50) DEFAULT 'SP' COMMENT 'Estado',
    cep VARCHAR(10) COMMENT 'CEP formatado',
    full_address TEXT COMMENT 'Endereço completo concatenado',
    
    -- Informações legais
    cnpj VARCHAR(20) COMMENT 'CNPJ do estabelecimento',
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_cnpj (cnpj),
    INDEX idx_cep (cep),
    FULLTEXT idx_description (full_description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Detalhes adicionais dos restaurantes';

-- =================================================================
-- 2. TABELA DE HORÁRIOS DE FUNCIONAMENTO
-- =================================================================
CREATE TABLE IF NOT EXISTS restaurant_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    
    -- Dia da semana
    day_of_week ENUM('Segunda-feira', 'Terça-feira', 'Quarta-feira', 
                     'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo') NOT NULL,
    day_number TINYINT NOT NULL COMMENT '1=Segunda, 7=Domingo',
    
    -- Horários
    opening_time TIME COMMENT 'Horário de abertura',
    closing_time TIME COMMENT 'Horário de fechamento',
    schedule_text VARCHAR(100) COMMENT 'Texto original do horário',
    is_closed BOOLEAN DEFAULT FALSE COMMENT 'Se está fechado neste dia',
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    UNIQUE KEY unique_restaurant_day (restaurant_id, day_of_week),
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_day_number (day_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Horários de funcionamento dos restaurantes';

-- =================================================================
-- 3. TABELA DE AVALIAÇÕES
-- =================================================================
CREATE TABLE IF NOT EXISTS restaurant_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    
    -- Dados da avaliação
    customer_name VARCHAR(100) NOT NULL COMMENT 'Nome do cliente',
    rating DECIMAL(2,1) NOT NULL COMMENT 'Nota de 0.0 a 5.0',
    review_date DATE COMMENT 'Data da avaliação',
    review_text TEXT COMMENT 'Comentário do cliente',
    
    -- Controle de duplicação
    review_hash VARCHAR(64) UNIQUE COMMENT 'Hash MD5 para evitar duplicatas',
    
    -- Metadados
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_rating (rating),
    INDEX idx_date (review_date),
    INDEX idx_customer (customer_name),
    FULLTEXT idx_review_text (review_text)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Avaliações individuais dos clientes';

-- =================================================================
-- 4. TABELA DE RESUMO DE AVALIAÇÕES
-- =================================================================
CREATE TABLE IF NOT EXISTS restaurant_reviews_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT UNIQUE NOT NULL,
    
    -- Estatísticas gerais
    total_reviews INT DEFAULT 0 COMMENT 'Total de avaliações',
    total_reviews_text VARCHAR(100) COMMENT 'Texto original do total',
    average_rating DECIMAL(3,2) DEFAULT 0.00 COMMENT 'Média das avaliações',
    last_review_date DATE COMMENT 'Data da última avaliação',
    
    -- Distribuição de ratings
    rating_5_count INT DEFAULT 0 COMMENT 'Quantidade de 5 estrelas',
    rating_4_count INT DEFAULT 0 COMMENT 'Quantidade de 4 estrelas',
    rating_3_count INT DEFAULT 0 COMMENT 'Quantidade de 3 estrelas',
    rating_2_count INT DEFAULT 0 COMMENT 'Quantidade de 2 estrelas',
    rating_1_count INT DEFAULT 0 COMMENT 'Quantidade de 1 estrela',
    
    -- Percentuais
    rating_5_percent DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Percentual de 5 estrelas',
    rating_4_percent DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Percentual de 4 estrelas',
    rating_3_percent DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Percentual de 3 estrelas',
    rating_2_percent DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Percentual de 2 estrelas',
    rating_1_percent DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Percentual de 1 estrela',
    
    -- Metadados
    last_scraped TIMESTAMP NULL COMMENT 'Última vez que foi coletado',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_average_rating (average_rating),
    INDEX idx_total_reviews (total_reviews)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Resumo estatístico das avaliações';

-- =================================================================
-- 5. VIEWS PARA FACILITAR CONSULTAS
-- =================================================================

-- View completa do restaurante com todos os detalhes
CREATE OR REPLACE VIEW v_restaurant_complete AS
SELECT 
    r.*,
    rd.full_description,
    rd.street_address,
    rd.city as detail_city,
    rd.state,
    rd.cep,
    rd.full_address,
    rd.cnpj,
    rs.total_reviews,
    rs.average_rating as review_average,
    rs.last_review_date,
    c.name as category_name,
    c.slug as category_slug
FROM restaurants r
LEFT JOIN restaurant_details rd ON r.id = rd.restaurant_id
LEFT JOIN restaurant_reviews_summary rs ON r.id = rs.restaurant_id
LEFT JOIN categories c ON r.category_id = c.id;

-- View de horários formatados
CREATE OR REPLACE VIEW v_restaurant_schedules AS
SELECT 
    rs.restaurant_id,
    r.name as restaurant_name,
    rs.day_of_week,
    rs.day_number,
    CASE 
        WHEN rs.is_closed THEN 'Fechado'
        ELSE rs.schedule_text
    END as schedule,
    rs.opening_time,
    rs.closing_time,
    rs.is_closed
FROM restaurant_schedules rs
JOIN restaurants r ON rs.restaurant_id = r.id
ORDER BY rs.restaurant_id, rs.day_number;

-- View de top avaliações recentes
CREATE OR REPLACE VIEW v_recent_reviews AS
SELECT 
    rr.id,
    r.name as restaurant_name,
    rr.customer_name,
    rr.rating,
    rr.review_date,
    rr.review_text,
    rr.scraped_at
FROM restaurant_reviews rr
JOIN restaurants r ON rr.restaurant_id = r.id
WHERE rr.review_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY rr.review_date DESC, rr.rating DESC;

-- =================================================================
-- 6. STORED PROCEDURES PARA ATUALIZAÇÃO
-- =================================================================

DELIMITER $$

-- Procedure para atualizar resumo de avaliações
CREATE PROCEDURE sp_update_review_summary(IN p_restaurant_id INT)
BEGIN
    DECLARE v_total INT;
    DECLARE v_avg DECIMAL(3,2);
    DECLARE v_last_date DATE;
    
    -- Calcular estatísticas
    SELECT 
        COUNT(*),
        IFNULL(AVG(rating), 0),
        MAX(review_date)
    INTO v_total, v_avg, v_last_date
    FROM restaurant_reviews
    WHERE restaurant_id = p_restaurant_id;
    
    -- Inserir ou atualizar resumo
    INSERT INTO restaurant_reviews_summary (
        restaurant_id, total_reviews, average_rating, last_review_date,
        rating_5_count, rating_4_count, rating_3_count, rating_2_count, rating_1_count
    )
    SELECT 
        p_restaurant_id,
        v_total,
        v_avg,
        v_last_date,
        SUM(CASE WHEN rating >= 4.5 THEN 1 ELSE 0 END),
        SUM(CASE WHEN rating >= 3.5 AND rating < 4.5 THEN 1 ELSE 0 END),
        SUM(CASE WHEN rating >= 2.5 AND rating < 3.5 THEN 1 ELSE 0 END),
        SUM(CASE WHEN rating >= 1.5 AND rating < 2.5 THEN 1 ELSE 0 END),
        SUM(CASE WHEN rating < 1.5 THEN 1 ELSE 0 END)
    FROM restaurant_reviews
    WHERE restaurant_id = p_restaurant_id
    ON DUPLICATE KEY UPDATE
        total_reviews = VALUES(total_reviews),
        average_rating = VALUES(average_rating),
        last_review_date = VALUES(last_review_date),
        rating_5_count = VALUES(rating_5_count),
        rating_4_count = VALUES(rating_4_count),
        rating_3_count = VALUES(rating_3_count),
        rating_2_count = VALUES(rating_2_count),
        rating_1_count = VALUES(rating_1_count);
    
    -- Atualizar percentuais
    UPDATE restaurant_reviews_summary
    SET 
        rating_5_percent = CASE WHEN total_reviews > 0 THEN (rating_5_count * 100.0 / total_reviews) ELSE 0 END,
        rating_4_percent = CASE WHEN total_reviews > 0 THEN (rating_4_count * 100.0 / total_reviews) ELSE 0 END,
        rating_3_percent = CASE WHEN total_reviews > 0 THEN (rating_3_count * 100.0 / total_reviews) ELSE 0 END,
        rating_2_percent = CASE WHEN total_reviews > 0 THEN (rating_2_count * 100.0 / total_reviews) ELSE 0 END,
        rating_1_percent = CASE WHEN total_reviews > 0 THEN (rating_1_count * 100.0 / total_reviews) ELSE 0 END,
        last_scraped = NOW()
    WHERE restaurant_id = p_restaurant_id;
END$$

-- Procedure para processar horário texto
CREATE PROCEDURE sp_parse_schedule_time(
    IN p_schedule_text VARCHAR(100),
    OUT p_opening_time TIME,
    OUT p_closing_time TIME,
    OUT p_is_closed BOOLEAN
)
BEGIN
    DECLARE v_opening VARCHAR(10);
    DECLARE v_closing VARCHAR(10);
    
    SET p_is_closed = FALSE;
    
    -- Verificar se está fechado
    IF p_schedule_text LIKE '%Fechado%' OR p_schedule_text = '' THEN
        SET p_is_closed = TRUE;
        SET p_opening_time = NULL;
        SET p_closing_time = NULL;
    ELSE
        -- Extrair horários (formato: "12:30 às 23:30")
        SET v_opening = SUBSTRING_INDEX(p_schedule_text, ' às ', 1);
        SET v_closing = SUBSTRING_INDEX(p_schedule_text, ' às ', -1);
        
        -- Converter para TIME
        SET p_opening_time = STR_TO_TIME(v_opening, '%H:%i');
        SET p_closing_time = STR_TO_TIME(v_closing, '%H:%i');
    END IF;
END$$

DELIMITER ;

-- =================================================================
-- 7. TRIGGERS PARA MANTER INTEGRIDADE
-- =================================================================

DELIMITER $$

-- Trigger para calcular hash da review e evitar duplicatas
CREATE TRIGGER before_insert_review
BEFORE INSERT ON restaurant_reviews
FOR EACH ROW
BEGIN
    -- Criar hash único baseado em restaurant_id + customer_name + date + rating
    SET NEW.review_hash = MD5(CONCAT(
        NEW.restaurant_id, '|',
        NEW.customer_name, '|',
        IFNULL(NEW.review_date, ''), '|',
        NEW.rating
    ));
END$$

DELIMITER ;

-- =================================================================
-- 8. ÍNDICES ADICIONAIS PARA PERFORMANCE
-- =================================================================

-- Índices para queries comuns
CREATE INDEX idx_reviews_restaurant_date ON restaurant_reviews(restaurant_id, review_date DESC);
CREATE INDEX idx_schedules_restaurant_day ON restaurant_schedules(restaurant_id, day_number);

-- =================================================================
-- 9. DADOS DE EXEMPLO PARA TESTE
-- =================================================================

-- Inserir alguns dados de teste (comentado por padrão)
/*
-- Exemplo de detalhes do restaurante
INSERT INTO restaurant_details (restaurant_id, full_description, street_address, city, cep, cnpj)
VALUES (1, 'Descrição completa do restaurante...', 'Rua Exemplo, 123', 'Birigui', '16200-000', '12.345.678/0001-90');

-- Exemplo de horários
INSERT INTO restaurant_schedules (restaurant_id, day_of_week, day_number, opening_time, closing_time, schedule_text)
VALUES 
(1, 'Segunda-feira', 1, '11:00:00', '23:00:00', '11:00 às 23:00'),
(1, 'Terça-feira', 2, '11:00:00', '23:00:00', '11:00 às 23:00');

-- Exemplo de avaliações
INSERT INTO restaurant_reviews (restaurant_id, customer_name, rating, review_date, review_text)
VALUES 
(1, 'João Silva', 5.0, '2024-01-15', 'Excelente comida!'),
(1, 'Maria Santos', 4.5, '2024-01-14', 'Muito bom, recomendo');

-- Atualizar resumo
CALL sp_update_review_summary(1);
*/

-- =================================================================
-- FIM DA MIGRATION
-- =================================================================