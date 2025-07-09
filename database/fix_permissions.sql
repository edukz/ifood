-- ===================================================================
-- SCRIPT PARA CORRIGIR PERMISSÕES DO USUÁRIO
-- ===================================================================

-- Conectar como root primeiro
-- Execute este script com: mysql -u root -pDedolas1901* < fix_permissions.sql

-- Verificar se o banco existe
USE ifood_scraper_v3;

-- Recriar usuário com permissões corretas
DROP USER IF EXISTS 'ifood_user'@'localhost';
DROP USER IF EXISTS 'ifood_user'@'%';

-- Criar usuário novamente
CREATE USER 'ifood_user'@'localhost' IDENTIFIED BY 'ifood_password';
CREATE USER 'ifood_user'@'%' IDENTIFIED BY 'ifood_password';

-- Dar todas as permissões no banco ifood_scraper_v3
GRANT ALL PRIVILEGES ON ifood_scraper_v3.* TO 'ifood_user'@'localhost';
GRANT ALL PRIVILEGES ON ifood_scraper_v3.* TO 'ifood_user'@'%';

-- Aplicar mudanças
FLUSH PRIVILEGES;

-- Verificar permissões
SHOW GRANTS FOR 'ifood_user'@'localhost';

-- Testar conexão
SELECT USER(), DATABASE();
SELECT 'Permissões corrigidas com sucesso!' as Status;