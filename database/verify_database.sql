-- Verificar se o banco existe e as tabelas foram criadas
SHOW DATABASES LIKE 'ifood_scraper_v3';

-- Se existir, verificar tabelas
USE ifood_scraper_v3;
SHOW TABLES;

-- Verificar usuários
SELECT User, Host FROM mysql.user WHERE User = 'ifood_user' OR User = 'root';

-- Ver permissões do root
SHOW GRANTS FOR 'root'@'localhost';