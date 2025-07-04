#!/usr/bin/env python3
"""
Verificador de dependências do iFood Scraper
Testa se todas as dependências estão instaladas e funcionando
"""

import sys
import subprocess
import importlib
from pathlib import Path


def check_python_version():
    """Verifica versão do Python"""
    print("🐍 Verificando Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Versão muito antiga")
        print("   📋 Necessário Python 3.8 ou superior")
        return False


def check_module(module_name, package_name=None):
    """Verifica se um módulo está instalado"""
    package_name = package_name or module_name
    
    try:
        importlib.import_module(module_name)
        print(f"   ✅ {package_name} - OK")
        return True
    except ImportError:
        print(f"   ❌ {package_name} - Não instalado")
        print(f"   📋 Instale com: pip install {package_name}")
        return False


def check_playwright_browsers():
    """Verifica se os navegadores do Playwright estão instalados"""
    print("🌐 Verificando navegadores Playwright...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("   ✅ Chromium - OK")
                return True
            except Exception as e:
                print("   ❌ Chromium - Erro ao inicializar")
                print(f"   📋 Execute: playwright install")
                print(f"   📋 Erro: {str(e)[:100]}...")
                return False
                
    except ImportError:
        print("   ❌ Playwright não está instalado")
        return False


def check_project_structure():
    """Verifica estrutura do projeto"""
    print("📁 Verificando estrutura do projeto...")
    
    required_dirs = ['src', 'data', 'logs', 'config']
    required_files = ['main.py', 'README.md']
    
    all_ok = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"   ✅ {dir_name}/ - OK")
        else:
            print(f"   ❌ {dir_name}/ - Não encontrado")
            all_ok = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"   ✅ {file_name} - OK")
        else:
            print(f"   ❌ {file_name} - Não encontrado")
            all_ok = False
    
    return all_ok


def check_permissions():
    """Verifica permissões de escrita"""
    print("🔐 Verificando permissões...")
    
    test_dirs = ['data', 'logs']
    all_ok = True
    
    for dir_name in test_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            test_file = dir_path / '.test_write'
            try:
                test_file.write_text('test')
                test_file.unlink()
                print(f"   ✅ {dir_name}/ - Escrita OK")
            except Exception:
                print(f"   ❌ {dir_name}/ - Sem permissão de escrita")
                all_ok = False
        else:
            print(f"   ⚠️  {dir_name}/ - Diretório não existe")
    
    return all_ok


def test_basic_functionality():
    """Testa funcionalidade básica"""
    print("🧪 Testando funcionalidade básica...")
    
    try:
        # Testa import dos módulos principais
        sys.path.insert(0, str(Path.cwd()))
        
        from src.utils.database import DatabaseManager
        from src.scrapers.category_scraper import CategoryScraper
        from src.scrapers.restaurant_scraper import RestaurantScraper
        
        # Testa criação de objetos
        db = DatabaseManager()
        category_scraper = CategoryScraper("São Paulo", headless=True)
        restaurant_scraper = RestaurantScraper("São Paulo", headless=True)
        
        print("   ✅ Imports principais - OK")
        print("   ✅ Criação de objetos - OK")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste básico: {str(e)}")
        return False


def main():
    """Execução principal"""
    print("🔍 iFood Scraper - Verificador de Dependências")
    print("=" * 55)
    
    all_checks = []
    
    # Executa todas as verificações
    all_checks.append(check_python_version())
    
    print("\n📦 Verificando módulos Python...")
    required_modules = [
        ('playwright', 'playwright'),
        ('pandas', 'pandas'),
        ('pathlib', None),  # Nativo do Python
        ('json', None),     # Nativo do Python
        ('csv', None),      # Nativo do Python
    ]
    
    for module, package in required_modules:
        all_checks.append(check_module(module, package))
    
    print()
    all_checks.append(check_playwright_browsers())
    
    print()
    all_checks.append(check_project_structure())
    
    print()
    all_checks.append(check_permissions())
    
    print()
    all_checks.append(test_basic_functionality())
    
    # Resultado final
    print("\n" + "=" * 55)
    
    if all(all_checks):
        print("🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
        print("✨ O projeto está pronto para uso.")
        print("\n📋 Próximos passos:")
        print("   1. python main.py --help")
        print("   2. python examples/basic_usage.py")
        print("   3. python main.py --mode categories --city 'Sua Cidade'")
    else:
        failed_count = sum(1 for check in all_checks if not check)
        print(f"❌ {failed_count} VERIFICAÇÃO(ÕES) FALHARAM")
        print("🔧 Resolva os problemas acima antes de usar o projeto.")
        print("\n📋 Comandos úteis:")
        print("   pip install -r config/requirements.txt")
        print("   playwright install")
        print("   sudo playwright install-deps")
    
    print("\n" + "=" * 55)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Verificação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante verificação: {e}")
        sys.exit(1)