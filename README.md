# 🇧🇷 Gerador de Dados Brasileiros Realistas

Gere nomes, endereços, CPFs, CNPJs e outros documentos brasileiros que são **proporcionais à distribuição populacional real** e baseados **exclusivamente em dados existentes e verificados**. Cada nome gerado existe nos registros históricos brasileiros, e as localizações são amostradas proporcionalmente à população de cada região.

*Read it in English: [English](README.en.md)*

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Características Principais

- 📍 **Geração de Localizações**: Endereços brasileiros realistas com amostragem ponderada por população
- 👤 **Geração de Nomes**: Nomes brasileiros historicamente precisos com amostragem específica por período
- 📄 **Geração de Documentos**: Documentos brasileiros válidos (CPF, RG, PIS, CNPJ, CEI)
- 🎯 **Precisão Estatística**: Baseado em dados demográficos reais e estatísticas históricas
- 🔧 **Saída Flexível**: Dados estruturados em vários formatos (CLI, dicionários Python, pronto para API)
- ⚡ **Alto Desempenho**: Amostragem eficiente com pesos pré-calculados
- 🧪 **Completamente Testado**: Conjunto abrangente de testes para confiabilidade

## 🚀 Perfeito Para

- 🏢 **Aplicações Empresariais**: Gere dados de teste realistas para aplicações no mercado brasileiro
- 🧪 **Testes**: Crie conjuntos de dados diversos para testes abrangentes de aplicações
- 📊 **Ciência de Dados**: Gere amostras estatisticamente precisas para análise e modelagem
- 🎓 **Educação**: Aprenda sobre formatos de documentos brasileiros e regras de validação
- 🔄 **Desenvolvimento de APIs**: Dados estruturados prontos para uso em respostas de API

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/ptbr-sampler.git
cd ptbr-sampler

# Instale as dependências (recomenda-se usar um ambiente virtual)
uv sync
```

## 🎯 Início Rápido

### Interface de Linha de Comando

```bash
# Gere um perfil completo (nome, localização, documentos)
uv run src.cli sample --qty 1

# Gere apenas documentos específicos
uv run src.cli sample --only-cpf --only-rg --qty 3
```

### API Python

```python
from src.br_location_class import BrazilianLocationSampler
from src.br_name_class import BrazilianNameSampler, TimePeriod
from src.document_sampler import DocumentSampler

# Inicialize os amostradores
location_sampler = BrazilianLocationSampler("data/cities_with_ceps.json")
name_sampler = BrazilianNameSampler("data/names_data.json", 
                                   middle_names_path="data/middle_names.json")
doc_sampler = DocumentSampler()

# Gere os dados
state_name, state_abbr, city_name = location_sampler.get_state_and_city()
name_components = name_sampler.get_random_name(
    time_period=TimePeriod.UNTIL_2010,
    return_components=True
)

# Obtenha a saída formatada
result = {
    "name": name_components.first_name,
    "middle_name": name_components.middle_name,
    "surnames": name_components.surname,
    "city": city_name,
    "state": state_name,
    "state_abbr": state_abbr,
    "cep": location_sampler.format_full_location(
        city_name, state_name, state_abbr
    ).split(',')[-1].strip(),
    "cpf": doc_sampler.generate_cpf(),
    "rg": doc_sampler.generate_rg(state_abbr)
}
```

## 🎛️ Funcionalidades em Detalhes

### Geração de Localização
- Seleção de estados e cidades ponderada por população
- Geração realista de CEPs
- Formatação flexível da saída
- Suporte para filtragem por região específica

### Geração de Nomes
- Amostragem baseada em períodos históricos
- Suporte para nomes completos, nomes do meio e sobrenomes
- Opções de formatação (título, maiúsculas)
- Opção de lista dos 40 sobrenomes mais comuns

### Geração de Documentos
- CPF (Cadastro de Pessoas Físicas)
- RG (Registro Geral) com formatos específicos por estado
- PIS (Programa de Integração Social)
- CNPJ (Cadastro Nacional da Pessoa Jurídica)
- CEI (Cadastro Específico do INSS)

### Saída de Dados
- Formato de dicionário estruturado
- CLI com formatação rica
- Suporte para geração em lote
- Campos de saída personalizáveis

## 🏗️ Estrutura do Projeto

```plaintext
src
├── br_location_class.py         # Amostragem de localização
├── br_name_class.py             # Amostragem de nomes
├── br_rg_class.py              # Geração de RG
├── cli.py                      # Interface de linha de comando
├── document_sampler.py         # Geração de documentos
├── __init__.py                 # Inicialização do pacote
└── utils/                      # Funções utilitárias
    ├── cpf.py                  # Manipulação de CPF
    ├── pis.py                  # Manipulação de PIS
    ├── cnpj.py                 # Manipulação de CNPJ
    ├── cei.py                  # Manipulação de CEI
    ├── util.py                 # Funções auxiliares
    └── __init__.py
```

## 🧪 Testes

Conjunto abrangente de testes cobrindo todos os componentes:

```bash
uv run pytest
```

## 📚 Requisitos

- Python 3.9+
- Dependências:
  - Typer (framework CLI)
  - Rich (formatação de terminal)
  - pytest (testes)

## 📖 Documentação

Documentação detalhada para todas as funcionalidades e componentes:

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Interface de Linha de Comando](#interface-de-linha-de-comando-cli)
- [Retorno de Dados](#retorno-de-dados-em-dicionários)
- [Testes e Validação](#testes-e-validação)
- [Instalação e Dependências](#instalação-e-dependências)
- [Exemplos de Uso](#exemplos-de-uso)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.
