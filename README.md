# Desafio de Data Engineer - EMD

## Descrição do desafio

Neste desafio você deverá capturar, estruturar, armazenar e transformar dados de uma API instantânea. A API consiste nos dados de GPS do BRT que são gerados na hora da consulta com o último sinal transmitido por cada veículo.

Para o desafio, será necessário construir uma pipeline que captura os dados minuto a minuto e gera um arquivo no formato CSV. O arquivo gerado deverá conter no mínimo 10 minutos de dados capturados (estruture os dados da maneira que achar mais conveniente), então carregue os dados para uma tabela no Postgres. Por fim, crie uma tabela derivada usando o DBT. A tabela derivada deverá conter o ID do onibus, posição e sua a velocidade.

A pipeline deverá ser construída subindo uma instância local do Prefect (em Python). Utilize a versão *0.15.9* do Prefect.

## Solução proposta
 Cria-se um pipeline de dados que faz uma consulta a cada minuto, total de 10 consultas, a
 API de GPS do BRT. Cada consulta gera um arquivo `.json` com a data que foi realizada a 
 consulta e as informações coletadas. A cada 10 arquivos `.json` gerados
 (representando 10 minutos de dados capturados) é gerado um arquivo `.csv` 
 contendo as informações agregadas. Esse arquivo `.csv` então é
 carregado numa tabela em um banco de dados PostgreSQL inicializado localmente
 na tabela chamada `raw.tb_brt_gps`, e por fim, uma tabela derivada é gerada usando o DBT com o nome `raw.brt_info` 


## Estrutura do projeto

- `output/` - Diretório onde são gravados os arquivos .json e .csv;
- `project_1/` - Contém todos os arquivos relacionados ao dbt;
  - `dbt_project.yml` - Informa que materializa tabelas;
  - `profiles.yml` - Informações para login do banco de dados;
  - `models/` - Diretório com Querys usadas pelo dbt;
    - `brt_info.sql` - Query para criação da tabela derivada;
- `pipeline/` - Contém os arquivos relacionados a execução do pipeline pelo Prefect;
  - `constants.py` - Declaração dos valores constantes para o projeto;
  - `flows.py` - Declaração do Fluxo;
  - `run.py` - Código para iniciar o Fluxo;
  - `schedules.py` - Declaração do Schedule;
  - `tasks.py` - Declaração das Tarefas;
- `requirements.txt` - Bibliotecas (incluso versão) necessárias para rodar o código localmente;


## Configuração do ambiente de execução
    
### Requisitos

- Código desenvolvido e testado em um ambiente virtual no Windows
- Python 3.10.x
- `pip`
- `PostgreSQL`
- `PostGIS`
- `dbt-postgres`

## Executando a pipeline

- (Opcional) Crie e ative um ambiente virtual usando venv
- Instale as dependências definidas em `requirements.txt` com o comando:
```
pip install -r requirements.txt
 ```
- Abra e execute o arquivo `run.py` na pasta `pipeline` do projeto:
- Diretório padrão para rodar localmente é a pasta em que todas as pastas presentes estão alocadas

## Links de referência

- Documentação [Prefect](https://docs-v1.prefect.io/)
- Documentação [DBT](https://docs.getdbt.com/docs/introduction)
- Instalar e configurar o
   [Prefect Server](https://docs.prefect.io/orchestration/getting-started/install.html)
   locamente com um [Docker Agent](https://docs.prefect.io/orchestration/agents/docker.html)
- Construir a pipeline de captura da [API do
   BRT](https://dados.mobilidade.rio/gps/brt)
- Repositório pipelines do [Escritorio de Dados](https://github.com/prefeitura-rio/pipelines)
- Repositório de modelos DBT do [Escritorio de Dados](https://github.com/prefeitura-rio/queries-datario)

