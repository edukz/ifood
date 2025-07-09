@echo off
echo ============================================================
echo    SETUP DO BANCO DE DADOS IFOOD SCRAPER V3
echo ============================================================
echo.

REM Navegue para o diretório correto
cd /d "%~dp0\.."

echo Executando script SQL para criar o banco de dados...
echo.

REM Execute o script SQL diretamente
mysql -u root -pDedolas1901* < database\create_database.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Banco de dados criado com sucesso!
    echo.
    echo 📋 Detalhes:
    echo    - Banco: ifood_scraper_v3
    echo    - Usuario: ifood_user
    echo    - Senha: ifood_password
    echo.
    echo As credenciais ja estao configuradas no arquivo .env
) else (
    echo.
    echo ❌ Erro ao criar o banco de dados.
    echo Verifique se o MySQL esta rodando e a senha do root esta correta.
)

echo.
pause