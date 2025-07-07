# Sistema de Banco de Dados V2 - iFood Scraper

## 🚀 Visão Geral

O novo sistema de banco de dados V2 foi completamente reescrito para ser mais limpo, eficiente e confiável. Principais melhorias:

- ✅ **Prevenção de duplicatas** usando chaves únicas baseadas em hash MD5
- ✅ **Rastreamento de preços** com histórico completo
- ✅ **Pool de conexões** para melhor performance
- ✅ **Schema otimizado** com índices apropriados
- ✅ **Logs de extração** para rastreabilidade
- ✅ **Sistema de configuração** flexível

## 📋 Estrutura do Banco

### Tabelas Principais

1. **categories** - Categorias de restaurantes
   - Chave única: `slug`
   - Índices: slug, city, is_active

2. **restaurants** - Informações dos restaurantes
   - Chave única: `unique_key` (hash MD5 de name+category+city)
   - Índices: name, category_id, city, rating, etc.

3. **products** - Produtos/itens do cardápio
   - Chave única: `unique_key` (hash MD5 de restaurant_id+name+category)
   - Índices: restaurant_id, category, price, etc.

4. **price_history** - Histórico de mudanças de preço
   - Registra todas as alterações de preço dos produtos

5. **extraction_logs** - Logs de extração
   - Rastreia todas as operações de scraping

6. **system_config** - Configurações do sistema

### Views Úteis

- **category_stats** - Estatísticas por categoria
- **products_full** - Produtos com informações completas

## 🔧 Instalação

### 1. Criar o banco de dados

```bash
# Executar o script de setup
python setup_database_v2.py
```

Isso irá:
- Criar o banco `ifood_scraper_v2`
- Criar todas as tabelas e índices
- Configurar usuário e permissões
- Atualizar arquivo `.env`

### 2. Testar a instalação

```bash
# Executar testes
python test_database_v2.py
```

### 3. Migrar dados existentes (opcional)

```bash
# Se você tem dados no banco antigo
python migrate_data_v2.py
```

## 💻 Uso

### Usando o novo DatabaseManagerV2

```python
from src.database.database_manager_v2 import get_database_manager

# Obter instância
db = get_database_manager()

# Salvar categorias
result = db.save_categories([
    {
        'name': 'Pizza',
        'slug': 'pizza',
        'url': 'https://...',
        'icon_url': 'https://...'
    }
], city='São Paulo')

# Salvar restaurantes
result = db.save_restaurants([
    {
        'nome': 'Pizza Hut',
        'avaliacao': 4.5,
        'tempo_entrega': '30-40 min',
        'taxa_entrega': 'R$ 5,99',
        'url': 'https://...'
    }
], category='Pizza', city='São Paulo')

# Salvar produtos
result = db.save_products([
    {
        'nome': 'Pizza Margherita',
        'descricao': 'Molho, mussarela...',
        'preco': 'R$ 45,90',
        'categoria_produto': 'Pizzas'
    }
], restaurant_name='Pizza Hut', category='Pizza', city='São Paulo')
```

### Usando com código existente (Adaptador)

Para manter compatibilidade com scrapers existentes:

```python
# Em vez de:
# from src.utils.database import get_database_manager

# Use:
from src.database.database_adapter import get_database_manager

# O resto do código continua funcionando!
db = get_database_manager()
db.save_restaurants(restaurants, category, city)
```

## 🔍 Prevenção de Duplicatas

O sistema previne duplicatas automaticamente usando chaves únicas:

- **Restaurantes**: Hash MD5 de (nome + categoria + cidade)
- **Produtos**: Hash MD5 de (restaurant_id + nome + categoria_produto)

Exemplo:
```
Pizza Hut + Pizza + São Paulo = "a1b2c3d4e5f6..."
```

Se tentar inserir o mesmo restaurante novamente, ele será **atualizado** em vez de duplicado.

## 📊 Rastreamento de Preços

Sempre que um produto tem seu preço alterado:
1. O novo preço é salvo na tabela `products`
2. A mudança é registrada em `price_history`
3. Você pode consultar o histórico completo

```python
# Buscar histórico de preços
with db.get_cursor() as (cursor, _):
    cursor.execute("""
        SELECT * FROM price_history 
        WHERE product_id = %s 
        ORDER BY changed_at DESC
    """, (product_id,))
    history = cursor.fetchall()
```

## 🛠️ Configuração

### Arquivo .env

```env
# Banco de dados
DB_HOST=localhost
DB_PORT=3306
DB_USER=ifood_user
DB_PASSWORD=ifood_password
DB_NAME=ifood_scraper_v2
DB_POOL_SIZE=5

# Sistema
ENABLE_PRICE_TRACKING=true
CHUNK_SIZE=500
DUPLICATE_CHECK_ENABLED=true
```

### Configurações no banco

```sql
-- Ver configurações
SELECT * FROM system_config;

-- Alterar configuração
UPDATE system_config 
SET config_value = '1000' 
WHERE config_key = 'chunk_size';
```

## 📈 Monitoramento

### Estatísticas do sistema

```python
# Obter estatísticas
stats = db.get_statistics()
print(f"Categorias: {stats['categories']}")
print(f"Restaurantes ativos: {stats['active_restaurants']}")
print(f"Produtos disponíveis: {stats['available_products']}")
```

### Logs de extração

```python
# Iniciar log
log_id = db.log_extraction('restaurant', 'Pizza', 'started')

# ... fazer extração ...

# Finalizar log
db.update_extraction_log(log_id, 'success', items=25)
```

## 🧹 Manutenção

### Limpar dados antigos

```sql
-- Procedure para limpeza
CALL cleanup_old_data(30); -- Remove dados com mais de 30 dias
```

### Remover duplicatas

```python
# Remover duplicatas existentes
deleted = db.cleanup_duplicates()
print(f"Removidas {deleted} duplicatas")
```

## ❓ Troubleshooting

### Erro: "Table doesn't exist"

Execute o script de setup novamente:
```bash
python setup_database_v2.py
```

### Erro: "Duplicate key"

Isso é normal! Significa que a prevenção de duplicatas está funcionando.

### Performance lenta

1. Verifique os índices
2. Aumente o pool de conexões no .env
3. Use batch operations

## 🔄 Migração do sistema antigo

Para migrar do banco antigo:

1. Faça backup do banco atual
2. Execute `python migrate_data_v2.py`
3. Verifique os dados migrados
4. Atualize os imports nos scrapers

## 📝 Changelog

### v2.0 (2024-01)
- Sistema completamente reescrito
- Prevenção de duplicatas com hash MD5
- Rastreamento de histórico de preços
- Pool de conexões
- Logs de extração
- Schema otimizado