import glob
import json
import os
import requests
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import pandas as pd
import subprocess

import prefect
from prefect import task
from prefect.triggers import all_successful
from prefect.engine.signals import SKIP

from sqlalchemy import create_engine
from sqlalchemy.schema import CreateSchema
from constants import Constants

current_folder = os.getcwd()

@task(max_retries=3, retry_delay=timedelta(seconds=10))
def collect_data() -> None:
    """
        Coleta de Dados.
        Faz uma solicitação à API e salva o resultado em um arquivo .json.
    """

    # Solicitação à API
    logger = prefect.context.get("logger")
    api_url = Constants.API_URL
    response = requests.get(api_url)
    logger.info("Coletando dados da API...")

    # Retorna um sinal FAIL em caso de falha no lado da API
    response.raise_for_status()

    # Nome e Diretório do Arquivo de Saída
    c_time = str(datetime.now().timestamp())[0:10]
    json_filename = ("brt_"+c_time+".json")
    output_path = os.path.join(current_folder,'output')
    json_path = os.path.join(output_path, json_filename)

    # Salvar o resultado em um .json
    with open(json_path, "w") as outfile:
        json.dump(response.json().get('veiculos'), outfile)

    logger.info("Arquivo JSON criado!")


@task(max_retries=2, retry_delay=timedelta(seconds=60))
def transform_data() -> str:
    """
        Tratamento de Dados.
        Coletar a lista de json gerada, agregar em um Pandas Dataframe.
        Converter a data para UNIX.
        Remover colunas não utilizadas e renomear algumas colunas.
        Gerar arquivo .csv.

        Returna:
            csv_filename: str contendo o nome e diretório do arquivo .csv gerado.
    """

    # Coletar os nomes dos arquivos .json existentes em uma lista
    json_dir = os.path.join(current_folder,'output')
    json_path = os.path.join(json_dir, '*.json')
    json_file_list = glob.glob(json_path)

    # Definir nome e diretório do arquivo .csv de saída
    c_time = str(datetime.now().timestamp())[0:10]
    name_part = ("brt_data_"+c_time+".csv")
    output_path = os.path.join(current_folder,'output')
    csv_filename = os.path.join(output_path, name_part)
    json_df_list = []

    # Condição que gera um sinal SKIP para a execução do fluxo
    # Isso garante que a função seja executada a cada 10 arquivos
    if len(json_file_list) < 10:
        raise SKIP(message='Não há dados suficientes para carga no banco de dados')

    # Coletar e concatenar objetos JSON em um DataFrame
    for p in json_file_list:
        json_df = pd.read_json(p)
        json_df['datahoracoleta'] = datetime.fromtimestamp(int(p[-15:-5]))
        json_df_list.append(json_df)
        os.remove(p)

    df = pd.concat(json_df_list)

    # Tratamento de data e hora para UNIX
    df['date'] = pd.to_datetime(df['dataHora'], unit='ms').dt.tz_localize('UTC').apply(
        lambda x: x.astimezone(tzlocal())).dt.date
    df['hour'] = pd.to_datetime(df['dataHora'], unit='ms').dt.tz_localize('UTC').apply(
        lambda x: x.astimezone(tzlocal())).dt.time

    # Remover colunas não utilizadas e renomear algumas colunas utilizadas
    df.drop(columns=['dataHora', 'id_migracao_trajeto', 'direcao'], inplace=True)
    df.rename(columns={'codigo': 'codigo_onibus', 'date': 'dataposicao', 'hour': 'horaposicao'}, inplace=True)
    df.to_csv(csv_filename, index=False)

    return csv_filename


@task(max_retries=2, retry_delay=timedelta(seconds=20), trigger=all_successful)
def load_data_to_db(filename: str) -> None:
    """
        Carregar o arquivo .csv no banco de dados postgres.
        Só é executado quando transform_data() é executado com sucesso.

        Args:
            filename : str contendo o nome e diretório do arquivo .csv para carga no banco de dados

    """

    # Criar mecanismo para inserção SQL
    postgres_url = Constants.DB_ENGINE
    engine = create_engine(postgres_url)
    with engine.connect() as connection:
        connection.execute(CreateSchema("raw", if_not_exists=True))
        connection.commit()
    logger = prefect.context.get("logger")

    # Ler arquivo .csv
    df = pd.read_csv(filename)
    logger.info(f"Arquivo carregado: {filename}")
    logger.info(f"Tamanho: {len(df)} linhas inseridas")

    # Carregar na tabela raw.tb_brt_gps

    df.to_sql("tb_brt_gps", engine, schema='raw', if_exists='append', index=False)


@task(max_retries=2, retry_delay=timedelta(seconds=20), trigger=all_successful, skip_on_upstream_skip=True)
def materialize_model():
    """
        Tarefa para executar o modelo dbt automaticamente.
        Gera uma tabela derivada do banco de dados PostgreSQL.
        Executa apenas quando load_data_to_db() e transform_data() são executados com sucesso.

    """
    path = os.path.join(current_folder,'project_1')
    os.chdir(path)
    dbt_profile = "project_1"
    subprocess.run(['dbt', 'run', '--profiles-dir', os.getcwd(), '--profile', dbt_profile, '--models', 'brt_info'])
    os.chdir(current_folder)
