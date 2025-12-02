# 🇧🇷 Gerador de Dados Brasileiros Realistas

Gere nomes, endereços, CPFs, CNPJs e outros documentos brasileiros que são **proporcionais à distribuição populacional real** e baseados **exclusivamente em dados existentes e verificados**. Cada nome gerado existe nos registros históricos brasileiros, e as localizações são amostradas proporcionalmente à população de cada região. Ao mesmo tempo, como a alocação das entidades é distrbuída aleatoreamente e a formação dos nomes, nomes do meio e sobrenomes foi feita independentemente, é **impossível** que haja qualquer possibilidade de identificar uma pessoa específica.

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
uv run ptbr_sampler.cli sample --qty 1

# Gere apenas documentos específicos
uv run ptbr_sampler.cli sample --only-cpf --only-rg --qty 3
```

### Todas as Opções da CLI

#### Opções Básicas
```bash
--qty, -q                  Número de amostras a serem geradas (padrão: 1)
--all, -a                  Incluir todos os dados possíveis nas amostras geradas
--save-to-jsonl, -sj       Salvar amostras geradas em um arquivo JSONL
--append, -ap              Anexar ao arquivo JSONL em vez de sobrescrever (padrão: True)
--batch, -b                Máximo de amostras por lote antes de salvar (processa grandes solicitações em pequenos lotes) (padrão: 50)
--batch-size, -bs          Número de itens a serem processados em cada lote (padrão: 100)
--workers, -w              Número de workers a serem usados para chamadas de API (padrão: 100)
--easy, -e                 Modo fácil com quantidade inteira (ativa chamadas API, todos os dados e salva automaticamente)
```

#### Opções de Localização
```bash
--city-only, -c            Retornar apenas nomes de cidades
--state-abbr-only, -sa     Retornar apenas abreviações de estados
--state-full-only, -sf     Retornar apenas nomes completos de estados
--only-cep, -oc            Retornar apenas CEP
--cep-without-dash, -nd    Retornar CEP sem traço
--make-api-call, -mac      Fazer chamadas API para obter dados reais de CEP em vez de gerar dados de endereço sintéticos
```

#### Opções de Nome
```bash
--time-period, -t          Período de tempo para amostragem de nomes (padrão: UNTIL_2010)
--return-only-name, -rn    Retornar apenas o nome sem localização
--name-raw, -r             Retornar nomes em formato bruto (maiúsculas)
--only-surname, -s         Retornar apenas sobrenome
--top-40, -t40             Usar apenas os 40 sobrenomes mais comuns
--one-surname, -os         Retornar apenas um sobrenome em vez de dois
--always-middle, -am       Sempre incluir um nome do meio
--only-middle, -om         Retornar apenas nome do meio
```

#### Opções de Documento
```bash
--only-document, -od       Retornar apenas documentos
--always-cpf, -ac          Sempre incluir CPF (padrão: True)
--always-pis, -ap          Sempre incluir PIS
--always-cnpj, -acn        Sempre incluir CNPJ
--always-cei, -ace         Sempre incluir CEI
--always-rg, -ar           Sempre incluir RG (padrão: True)
--always-phone, -aph       Sempre incluir número de telefone (padrão: True)
--only-cpf, -ocpf          Retornar apenas CPF
--only-pis, -op            Retornar apenas PIS
--only-cnpj, -ocn          Retornar apenas CNPJ
--only-cei, -oce           Retornar apenas CEI
--only-rg, -or             Retornar apenas RG
--only-fone, -of           Retornar apenas número de telefone
--include-issuer, -ii      Incluir emissor no RG (padrão: True)
```

#### Opções de Fonte de Dados
```bash
--json-path, -j            Caminho para o arquivo JSON de dados de cidades e CEPs (padrão: ptbr_sampler/data/cities_with_ceps.json)
--names-path, -np          Caminho para o arquivo JSON de dados de primeiros nomes (padrão: ptbr_sampler/data/names_data.json)
--middle-names-path, -mnp  Caminho para o arquivo JSON de nomes do meio (padrão: ptbr_sampler/data/middle_names.json)
--surnames-path, -sp       Caminho para o arquivo JSON de sobrenomes (padrão: ptbr_sampler/data/surnames_data.json)
--locations-path, -lp      Caminho para o arquivo JSON de dados de localizações (padrão: ptbr_sampler/data/locations_data.json)
```

### API Python

```python
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.br_name_class import BrazilianNameSampler, TimePeriod
from ptbr_sampler.document_sampler import DocumentSampler

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

## 📊 Datasets Disponíveis

O projeto utiliza diversos datasets cuidadosamente preparados para garantir a geração de dados estatisticamente precisos e realistas:

### 🏙️ Dados de Localização
- **cities_with_ceps.json** (27MB): Contém informações detalhadas sobre cidades brasileiras, incluindo:
  - Nome da cidade
  - Estado (nome completo e abreviação)
  - População
  - Faixas de CEP associadas
  - Informações geográficas
  - Dados usados para amostragem ponderada por população

- **locations_data.json** (19MB): Dataset expandido com informações adicionais de localização:
  - Bairros
  - Logradouros
  - CEPs específicos
  - Informações complementares para geração de endereços completos

### 👤 Dados de Nomes
- **names_data.json** (17MB): Contém primeiros nomes brasileiros organizados por:
  - Frequência histórica
  - Distribuição por períodos de tempo (de 1930 a 2010)
  - Dados de popularidade para amostragem realista
  
- **middle_names.json** (141KB): Coleção de nomes do meio comuns no Brasil:
  - Nomes tradicionalmente usados como nomes do meio
  - Frequências relativas
  
- **surnames_data.json** (5.5MB): Base de dados de sobrenomes brasileiros:
  - Sobrenomes mais comuns
  - Frequências e distribuições
  - Sobrenomes compostos
  - Regras para prefixos (de, da, dos, etc.)

Todos os datasets foram compilados a partir de dados oficiais e registros históricos, garantindo alta fidelidade estatística para a geração de dados pessoais brasileiros.

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
- [Interface de Linha de Comando](#interface-de-linha-de-comando)
- [Datasets Disponíveis](#datasets-disponíveis)
- [Retorno de Dados](#retorno-de-dados-em-dicionários)
- [Testes e Validação](#testes-e-validação)
- [Instalação e Dependências](#instalação-e-dependências)
- [Exemplos de Uso](#exemplos-de-uso)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.