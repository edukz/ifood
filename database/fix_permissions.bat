@echo off
echo ============================================================
echo    CORRIGINDO PERMISSOES DO USUARIO MYSQL
echo ============================================================
echo.

cd /d "%~dp0"

echo Executando correcao de permissoes...
mysql -u root -pDedolas1901* < fix_permissions.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Permissoes corrigidas com sucesso!
    echo.
    echo O usuario ifood_user agora tem acesso ao banco ifood_scraper_v3
) else (
    echo.
    echo ❌ Erro ao corrigir permissoes
)

echo.
pause