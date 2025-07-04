# iFood Web Scraper

Um scraper profissional para extrair dados de categorias e restaurantes da plataforma iFood, desenvolvido com Playwright para simular comportamento humano e evitar detecção.

## Características Principais

- **Arquitetura Modular**: Organização profissional com separação de responsabilidades
- **Comportamento Humano**: Simula ações humanas com delays aleatórios e movimentos de mouse
- **Controle de Duplicatas**: Sistema de hash MD5 para evitar dados duplicados
- **Organização por Categoria**: Arquivos CSV separados para cada tipo de comida
- **Sistema de Logs Completo**: Rastreamento detalhado de todas as operações
- **Tratamento de Erros Robusto**: Retry automático e screenshots para debug

## Estrutura do Projeto

```
ifood/
├── main.py                    # Ponto de entrada principal
├── INSTALL.md                 # Guia de instalação detalhado
├── .env.example              # Exemplo de variáveis de ambiente
├── .gitignore                # Configurações Git
├── src/                      # Código fonte
│   ├── config/               # Configurações
│   │   ├── settings.py       # Configurações gerais
│   │   └── browser_config.py # Configurações do navegador
│   ├── models/               # Modelos de dados
│   │   ├── category.py       # Modelo de categoria
│   │   └── restaurant.py     # Modelo de restaurante
│   ├── scrapers/             # Scrapers especializados
│   │   ├── base.py          # Classe base
│   │   ├── ifood_scraper.py # Scraper principal
│   │   ├── category_scraper.py # Extração de categorias
│   │   └── restaurant_scraper.py # Extração de restaurantes
│   └── utils/                # Utilitários
│       ├── database.py       # Gerenciamento de dados
│       ├── error_handler.py  # Tratamento de erros
│       ├── human_behavior.py # Simulação humana
│       ├── helpers.py        # Funções auxiliares
│       └── logger.py         # Sistema de logs
├── config/                   # Arquivos de configuração
│   └── requirements.txt      # Dependências Python
├── data/                     # Dados extraídos (CSV e JSON)
├── logs/                     # Arquivos de log atuais
├── docs/                     # Documentação adicional
│   ├── CORRECOES_APLICADAS.md
│   ├── MELHORIAS_DADOS.md
│   └── MELHORIAS_POPUP.md
├── examples/                 # Exemplos de uso
│   └── basic_usage.py        # Exemplo básico completo
├── tools/                    # Ferramentas auxiliares
│   ├── check_dependencies.py # Verificador de dependências
│   └── data_analyzer.py      # Analisador de dados
├── archive/                  # Arquivos antigos
│   ├── old_logs/            # Logs históricos
│   └── screenshots/         # Screenshots de erro
└── temp_data/               # Dados temporários
```

## Instalação

Para instalação completa e detalhada, consulte o [Guia de Instalação](INSTALL.md).

### Instalação Rápida

```bash
# 1. Instalar dependências
pip install -r config/requirements.txt

# 2. Configurar Playwright
playwright install
sudo playwright install-deps  # Linux/WSL

# 3. Verificar instalação
python tools/check_dependencies.py
```

## Uso

### 1. Extrair Categorias

Coleta todas as categorias de comida disponíveis na cidade:

```bash
python main.py --mode categories --city "Nome da Cidade"
```

**Exemplo:**
```bash
python main.py --mode categories --city "São Paulo"
```

### 2. Extrair Restaurantes 🎯

Coleta dados dos restaurantes de uma categoria específica:

```bash
python main.py --mode restaurants --city "Nome da Cidade"
```

O sistema apresentará um menu interativo para selecionar a categoria desejada.

## Dados Extraídos

### Categorias
- **Nome**: Nome da categoria (ex: "Japonesa", "Italiana")
- **URL**: Link direto para a categoria
- **Slug**: Identificador único
- **Cidade**: Cidade de origem
- **Ícone**: URL do ícone da categoria

### Restaurantes 🚀
- **Nome**: Nome do restaurante
- **Categoria**: Tipo de comida
- **Avaliação**: Rating de 0 a 5 estrelas
- **Tempo de Entrega**: Tempo estimado (ex: "30-40 min")
- **Taxa de Entrega**: Custo de entrega (ex: "Grátis", "R$ 4,99")
- **Distância**: Distância do restaurante (ex: "1.2 km")
- **URL**: Link direto para o cardápio do restaurante
- **Endereço**: Localização (quando disponível)

### Produtos/Cardápio 🍽️
- **Nome**: Nome do produto/prato
- **Descrição**: Detalhes e ingredientes
- **Preço**: Valor atual de venda
- **Preço Original**: Valor antes de promoções
- **Categoria**: Tipo de produto (entrada, prato principal, etc)
- **Disponibilidade**: Se está disponível para pedido
- **Imagem**: URL da foto do produto
- **Tempo de Preparo**: Quando informado
- **Calorias**: Informação nutricional
- **Tags**: Promoção, Vegano, Novo, etc

## Arquivos Gerados

### Estrutura de Dados Organizada 📁

```
data/
├── categories/                              # 📂 Categorias de comida
│   └── ifood_data_categories.csv           #     Lista completa de categorias
├── restaurants/                             # 🏪 Dados dos restaurantes
│   ├── ifood_data_restaurantes_japonesa.csv #     Restaurantes japoneses
│   ├── ifood_data_restaurantes_italiana.csv #     Restaurantes italianos
│   └── ifood_data_restaurantes_brasileira.csv #   Restaurantes brasileiros
├── products/                                # 🍽️ Cardápios e produtos
│   ├── ifood_data_produtos_burger_king.csv #     Cardápio do Burger King
│   ├── ifood_data_produtos_pizza_hut.csv   #     Cardápio da Pizza Hut
│   └── ifood_data_produtos_sushi_house.csv #     Cardápio do Sushi House
└── ifood_data_metadata.json                # 📊 Estatísticas gerais
```

### Exemplo de CSV - Restaurantes

```csv
id,nome,categoria,avaliacao,tempo_entrega,taxa_entrega,distancia,url,endereco,extracted_at
abc123,Sushi House,Japonesa,4.8,30-40 min,Grátis,1.2 km,https://ifood.com.br/delivery/...,Rua das Flores 123,2025-07-01T20:30:00
```

## Configurações

### Browser

- **Modo**: Headless por padrão (pode ser alterado)
- **User-Agent**: Simula navegadores reais
- **Viewport**: 1920x1080 para melhor compatibilidade
- **Timeout**: 30 segundos para carregamento de páginas

### Comportamento Humano

- **Delays Aleatórios**: 1-3 segundos entre ações
- **Movimentos de Mouse**: Simulação de interação natural
- **Scroll Inteligente**: Carregamento progressivo de conteúdo
- **Retry Automático**: 3 tentativas em caso de falha

## Sistema de Logs

### Nova Arquitetura de Logs 🎯

O sistema foi otimizado para reduzir a quantidade de arquivos de log:

- **Um arquivo por dia**: Todos os componentes compartilham o mesmo arquivo
- **Rotação automática**: Logs antigos são removidos após 7 dias
- **Consolidação inteligente**: Múltiplas execuções no mesmo dia são agrupadas

### Estrutura de Logs

```
logs/
└── ifood_scraper_20250701.log    # Todos os logs do dia em um único arquivo

archive/
├── old_logs/                      # Logs históricos (limpeza automática)
└── screenshots/                   # Screenshots de erro para debug
```

### Configurações

No arquivo `src/config/settings.py`:
- `log_retention_days`: Dias para manter logs (padrão: 7)
- `log_level`: Nível de log (INFO, DEBUG, WARNING, ERROR)
- `log_to_console`: Mostrar logs no console
- `log_to_file`: Salvar logs em arquivo

### Ferramentas de Manutenção

```bash
# Limpar logs antigos manualmente
python tools/cleanup_logs.py
```

Opções disponíveis:
1. Limpar logs com mais de 7 dias
2. Remover TODOS os logs arquivados
3. Consolidar logs do mesmo dia
4. Limpeza completa (1 + 3)

## Controle de Qualidade

### Prevenção de Duplicatas

- **Hash MD5**: Gerado a partir de nome + categoria + cidade
- **Verificação Automática**: Antes de cada inserção
- **Cache em Memória**: Para verificação rápida

### Validação de Dados

- **Campos Obrigatórios**: Nome e categoria sempre preenchidos
- **Parsing Inteligente**: Extração de dados estruturados
- **Fallback Seguro**: Valores padrão quando dados não disponíveis

## Troubleshooting

### Problemas Comuns

**1. Erro de Dependências do Sistema**
```bash
# Instalar dependências necessárias
sudo apt-get install libnss3 libnspr4 libasound2
```

**2. Timeout de Navegação**
- Verifique a conexão de internet
- Aumente o timeout nas configurações
- Execute em horários de menor tráfego

**3. Elementos Não Encontrados**
- O sistema tenta múltiplos seletores automaticamente
- Screenshots são salvos para análise
- Logs detalhados mostram a causa

### Debug Avançado

- **Screenshots**: Salvos em `archive/` em caso de erro
- **HTML Source**: Capturado para análise posterior
- **Network Logs**: Monitoramento de requisições
- **Verificador**: `python tools/check_dependencies.py`
- **Analisador**: `python tools/data_analyzer.py`

## Limitações e Considerações

### Performance

- **Velocidade**: Limitada pelos delays humanos (necessários para evitar detecção)
- **Memória**: Otimizada para processar grandes volumes
- **Concorrência**: Preparado para paralelização futura

### Ética e Legalidade

- **Respeito ao robots.txt**: Verificar políticas do site
- **Rate Limiting**: Delays implementados para não sobrecarregar servidores
- **Uso Responsável**: Apenas para fins educacionais e de pesquisa

## Estatísticas de Exemplo

Baseado no arquivo de metadados atual:

```json
{
  "statistics": {
    "categories": {
      "total_saved": 15,
      "total_duplicates": 90,
      "last_update": "2025-07-01T20:01:04"
    },
    "restaurants": {
      "total_saved": 156,
      "total_duplicates": 0,
      "last_update": "2025-07-01T20:50:36"
    }
  }
}
```

## Desenvolvimento Futuro

### Ferramentas Disponíveis

- **Verificador de Dependências**: `tools/check_dependencies.py`
- **Analisador de Dados**: `tools/data_analyzer.py`
- **Exemplos de Uso**: `examples/basic_usage.py`

### Melhorias Planejadas

- **Paralelização**: Múltiplas categorias simultaneamente
- **API REST**: Interface web para controle
- **Dashboard**: Visualização dos dados coletados
- **Agendamento**: Execução automática programada

### Contribuições

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## Licença

Este projeto é desenvolvido para fins educacionais. Use com responsabilidade e respeite os termos de uso dos sites.

## Suporte

Para dúvidas ou problemas:

- **Instalação**: Consulte `INSTALL.md`
- **Verificação**: Execute `python tools/check_dependencies.py`
- **Análise**: Use `python tools/data_analyzer.py`
- **Logs**: Verifique `logs/` e `archive/old_logs/`
- **Documentação**: Consulte `docs/` para detalhes técnicos

---

**Desenvolvido com foco em qualidade, performance e ética no web scraping.**