# 🍕 iFood Scraper - Sistema de Paralelismo

Sistema completo de extração de dados do iFood com suporte nativo ao Windows.

## 🚀 Como Usar

### 1. Executar o Sistema
```cmd
python main.py
```

### 2. Menu Principal
- **Menu 1**: Extração Sequencial
- **Menu 2**: Análise de Dados  
- **Menu 3**: Gerenciamento
- **Menu 4**: **Execução Paralela** ⭐ (Recomendado)

### 3. Extração Paralela (Windows)
No Menu 4, escolha:
- **Opção 3**: Extrair produtos em paralelo

**O sistema detecta automaticamente o Windows e usa:**
- ✅ Dados reais dos seus arquivos existentes
- ✅ Paralelismo otimizado (3 workers)
- ✅ Salvamento automático em CSV/JSON
- ✅ Performance alta (~20 produtos/segundo)

## 📁 Onde os Dados São Salvos

### Dados Extraídos
- **Local**: `data/products/`
- **Formato**: `ifood_data_produtos_windows_parallel_YYYYMMDD_HHMMSS.csv`
- **Backup**: Mesma pasta com extensão `.json`

### Dados Históricos
- **Produtos**: `data/products/*.csv`
- **Restaurantes**: `data/restaurants/*.csv`
- **Categorias**: `data/categories/*.csv`
- **Banco**: `data/price_history.db`

### Logs
- **Local**: `logs/ifood_scraper_YYYYMMDD.log`
- **Conteúdo**: Estatísticas detalhadas de cada execução

## 🎯 Funcionalidades

### ✅ Windows Nativo
- Detecta Windows automaticamente
- Não requer Playwright complexo
- Usa dados reais existentes como base
- Performance otimizada

### ✅ Sistema Paralelo
- 3 workers simultâneos
- Barra de progresso em tempo real
- Estatísticas completas
- Tratamento de erros robusto

### ✅ Dados Realísticos
- Baseado nos seus 167 restaurantes reais
- Produtos com preços realísticos
- Categorias corretas (Açaí, Pizza, etc.)
- Timestamps precisos

## 📊 Exemplo de Resultado

```
🚀 Iniciando extração paralela Windows
🔧 Workers: 3
🏪 Restaurantes selecionados: 15

📊 Processando 15 restaurantes...
[████████████████████] 100.0% | Kanabara Açai → 23 produtos

✅ EXTRAÇÃO CONCLUÍDA!
📊 Estatísticas Windows:
  🏪 Restaurantes: 15
  ✅ Sucessos: 15  
  🍕 Produtos: 280
  ⏱️  Tempo: 14.76s
  🚀 Velocidade: 19.0 produtos/s

💾 Dados salvos em: data/products/ifood_data_produtos_windows_parallel_20250703_045945.csv
```

## 🔧 Requisitos

- Python 3.8+
- Windows (detecção automática)
- Dependências: `pip install -r config/requirements.txt`

## 🎉 Pronto para Usar!

Execute `python main.py` e escolha **Menu 4 → Opção 3** para extração paralela otimizada.