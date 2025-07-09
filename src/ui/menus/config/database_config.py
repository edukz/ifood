#!/usr/bin/env python3
"""
Database Configuration - Database connection and optimization settings
"""

import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from src.config.database import execute_query, get_connection
from .config_base import ConfigBase


class DatabaseConfig(ConfigBase):
    """Database configuration management"""
    
    def __init__(self, session_stats: Dict[str, Any], data_dir: Path):
        super().__init__("Configuração do Banco de Dados", session_stats, data_dir)
        load_dotenv()
    
    def show_database_menu(self):
        """Show database configuration menu"""
        current_config = {
            "Host": "DB_HOST",
            "Porta": "DB_PORT", 
            "Database": "DB_NAME",
            "Usuário": "DB_USER",
            "Pool de conexões": "DB_POOL_SIZE"
        }
        
        options = [
            "1. 🌐 Alterar host/porta",
            "2. 🏷️ Alterar nome do banco",
            "3. 👤 Alterar credenciais",
            "4. 🔄 Configurar pool de conexões",
            "5. 🧪 Testar conexão",
            "6. 📊 Verificar status do banco",
            "7. 🔧 Otimizar banco de dados"
        ]
        
        self._show_config_menu("🔧 CONFIGURAÇÕES DO BANCO DE DADOS", options, current_config)
        choice = self.get_user_choice(7)
        
        if choice == "1":
            self._change_host_port()
        elif choice == "2":
            self._change_database_name()
        elif choice == "3":
            self._change_credentials()
        elif choice == "4":
            self._configure_pool()
        elif choice == "5":
            self._test_connection()
        elif choice == "6":
            self._check_database_status()
        elif choice == "7":
            self._optimize_database()
        elif choice == "0":
            return
        else:
            self.show_invalid_option()
    
    def _change_host_port(self):
        """Change database host and port"""
        print("\n🌐 ALTERAR HOST/PORTA DO BANCO")
        print("═" * 40)
        
        current_host = self._get_env_var("DB_HOST", "localhost")
        current_port = self._get_env_var("DB_PORT", "3306")
        
        print(f"Host atual: {current_host}")
        print(f"Porta atual: {current_port}")
        
        new_host = input("\n🌐 Novo host (Enter para manter atual): ").strip()
        if not new_host:
            new_host = current_host
        
        new_port = self._validate_numeric_input("\n🔌 Nova porta (Enter para manter atual): ", 1, 65535)
        if new_port is None:
            new_port = int(current_port)
        
        if self._confirm_action(f"alterar host para '{new_host}' e porta para '{new_port}'"):
            success = True
            if new_host != current_host:
                success &= self._update_env_file("DB_HOST", new_host)
            if str(new_port) != current_port:
                success &= self._update_env_file("DB_PORT", str(new_port))
            
            if success:
                self.show_success("Host e porta atualizados! Reinicie o sistema para aplicar as mudanças.")
    
    def _change_database_name(self):
        """Change database name"""
        print("\n🏷️ ALTERAR NOME DO BANCO")
        print("═" * 30)
        
        current_name = self._get_env_var("DB_NAME", "ifood_scraper_v3")
        print(f"Nome atual: {current_name}")
        
        new_name = input("\n🏷️ Novo nome do banco: ").strip()
        if not new_name:
            self.show_error("Nome do banco não pode ser vazio")
            return
        
        if self._confirm_action(f"alterar nome do banco para '{new_name}'"):
            if self._update_env_file("DB_NAME", new_name):
                self.show_success("Nome do banco atualizado! Reinicie o sistema para aplicar as mudanças.")
    
    def _change_credentials(self):
        """Change database credentials"""
        print("\n👤 ALTERAR CREDENCIAIS DO BANCO")
        print("═" * 40)
        
        current_user = self._get_env_var("DB_USER", "root")
        print(f"Usuário atual: {current_user}")
        
        new_user = input("\n👤 Novo usuário (Enter para manter atual): ").strip()
        if not new_user:
            new_user = current_user
        
        if new_user != current_user:
            new_password = input("🔐 Nova senha: ").strip()
            if not new_password:
                self.show_error("Senha não pode ser vazia")
                return
        else:
            change_password = self._validate_boolean_input("🔐 Alterar senha? (s/n): ")
            if change_password:
                new_password = input("🔐 Nova senha: ").strip()
                if not new_password:
                    self.show_error("Senha não pode ser vazia")
                    return
            else:
                new_password = None
        
        if self._confirm_action("alterar credenciais do banco"):
            success = True
            if new_user != current_user:
                success &= self._update_env_file("DB_USER", new_user)
            if new_password:
                success &= self._update_env_file("DB_PASSWORD", new_password)
            
            if success:
                self.show_success("Credenciais atualizadas! Reinicie o sistema para aplicar as mudanças.")
    
    def _configure_pool(self):
        """Configure database connection pool"""
        print("\n🔄 CONFIGURAR POOL DE CONEXÕES")
        print("═" * 40)
        
        current_pool_size = int(self._get_env_var("DB_POOL_SIZE", "5"))
        current_max_overflow = int(self._get_env_var("DB_MAX_OVERFLOW", "10"))
        current_pool_timeout = int(self._get_env_var("DB_POOL_TIMEOUT", "30"))
        
        print(f"Tamanho atual do pool: {current_pool_size}")
        print(f"Max overflow atual: {current_max_overflow}")
        print(f"Timeout atual: {current_pool_timeout}s")
        
        new_pool_size = self._validate_numeric_input("\n🔄 Novo tamanho do pool (1-50): ", 1, 50)
        if new_pool_size is None:
            new_pool_size = current_pool_size
        
        new_max_overflow = self._validate_numeric_input(f"🔄 Novo max overflow (0-{new_pool_size * 2}): ", 0, new_pool_size * 2)
        if new_max_overflow is None:
            new_max_overflow = current_max_overflow
        
        new_pool_timeout = self._validate_numeric_input("⏱️ Novo timeout (10-300s): ", 10, 300)
        if new_pool_timeout is None:
            new_pool_timeout = current_pool_timeout
        
        if self._confirm_action("atualizar configurações do pool"):
            success = True
            if new_pool_size != current_pool_size:
                success &= self._update_env_file("DB_POOL_SIZE", str(new_pool_size))
            if new_max_overflow != current_max_overflow:
                success &= self._update_env_file("DB_MAX_OVERFLOW", str(new_max_overflow))
            if new_pool_timeout != current_pool_timeout:
                success &= self._update_env_file("DB_POOL_TIMEOUT", str(new_pool_timeout))
            
            if success:
                self.show_success("Pool de conexões configurado! Reinicie o sistema para aplicar as mudanças.")
    
    def _test_connection(self):
        """Test database connection"""
        print("\n🧪 TESTAR CONEXÃO COM BANCO")
        print("═" * 35)
        
        try:
            self.show_info("Testando conexão com banco de dados...")
            
            # Test connection using current settings
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    self.show_success("✅ Conexão com banco estabelecida com sucesso!")
                    
                    # Show connection details
                    print("\n📋 Detalhes da conexão:")
                    print(f"  Host: {self._get_env_var('DB_HOST', 'localhost')}")
                    print(f"  Porta: {self._get_env_var('DB_PORT', '3306')}")
                    print(f"  Database: {self._get_env_var('DB_NAME', 'ifood_scraper_v3')}")
                    print(f"  Usuário: {self._get_env_var('DB_USER', 'root')}")
                else:
                    self.show_error("❌ Falha na consulta de teste")
            else:
                self.show_error("❌ Falha ao conectar com banco de dados")
                
        except Exception as e:
            self.show_error(f"❌ Erro ao testar conexão: {str(e)}")
    
    def _check_database_status(self):
        """Check database status and information"""
        print("\n📊 STATUS DO BANCO DE DADOS")
        print("═" * 35)
        
        try:
            conn = get_connection()
            if not conn:
                self.show_error("Não foi possível conectar ao banco")
                return
            
            cursor = conn.cursor()
            
            # Database version
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"📋 Versão do MySQL: {version}")
            
            # Database size
            db_name = self._get_env_var("DB_NAME", "ifood_scraper_v3")
            cursor.execute(f"""
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
                FROM information_schema.tables 
                WHERE table_schema = '{db_name}'
            """)
            size_result = cursor.fetchone()
            size_mb = size_result[0] if size_result and size_result[0] else 0
            print(f"💾 Tamanho do banco: {size_mb} MB")
            
            # Table count
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = '{db_name}'
            """)
            table_count = cursor.fetchone()[0]
            print(f"📊 Número de tabelas: {table_count}")
            
            # Connection status
            cursor.execute("SHOW STATUS LIKE 'Connections'")
            connections = cursor.fetchone()[1]
            print(f"🔗 Total de conexões: {connections}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.show_error(f"Erro ao verificar status: {str(e)}")
    
    def _optimize_database(self):
        """Optimize database performance"""
        print("\n🔧 OTIMIZAR BANCO DE DADOS")
        print("═" * 30)
        
        if not self._confirm_action("otimizar o banco de dados (pode demorar)"):
            return
        
        try:
            conn = get_connection()
            if not conn:
                self.show_error("Não foi possível conectar ao banco")
                return
            
            cursor = conn.cursor()
            db_name = self._get_env_var("DB_NAME", "ifood_scraper_v3")
            
            # Get all tables
            cursor.execute(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{db_name}' 
                AND table_type = 'BASE TABLE'
            """)
            tables = cursor.fetchall()
            
            if not tables:
                self.show_warning("Nenhuma tabela encontrada para otimizar")
                return
            
            self.show_info(f"Otimizando {len(tables)} tabelas...")
            
            optimized_count = 0
            for (table_name,) in tables:
                try:
                    cursor.execute(f"OPTIMIZE TABLE {db_name}.{table_name}")
                    optimized_count += 1
                    print(f"  ✅ {table_name} otimizada")
                except Exception as e:
                    print(f"  ❌ Erro ao otimizar {table_name}: {str(e)}")
            
            cursor.close()
            conn.close()
            
            self.show_success(f"Otimização concluída! {optimized_count}/{len(tables)} tabelas otimizadas.")
            
        except Exception as e:
            self.show_error(f"Erro durante otimização: {str(e)}")
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get database configuration statistics"""
        stats = self.get_base_statistics()
        
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                
                # Database size
                db_name = self._get_env_var("DB_NAME", "ifood_scraper_v3")
                cursor.execute(f"""
                    SELECT 
                        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb,
                        COUNT(*) as table_count
                    FROM information_schema.tables 
                    WHERE table_schema = '{db_name}'
                """)
                result = cursor.fetchone()
                
                stats.update({
                    'database_size_mb': result[0] if result and result[0] else 0,
                    'table_count': result[1] if result and result[1] else 0,
                    'connection_available': True
                })
                
                cursor.close()
                conn.close()
            else:
                stats['connection_available'] = False
                
        except Exception as e:
            stats['connection_error'] = str(e)
            stats['connection_available'] = False
        
        return stats