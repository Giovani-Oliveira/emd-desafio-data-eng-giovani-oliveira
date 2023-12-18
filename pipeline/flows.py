from prefect import Flow

# Import do Agendamento
from schedules import minute_brt_data
# Import das Tarefas
from tasks import (collect_data, transform_data, load_data_to_db, materialize_model)


# Inicialização do Fluxo
with Flow("collect_brt_data", schedule=minute_brt_data) as flow_1:

    # Tarefa de Extração
    collect_data()

    # Tarefa de Transformação
    transform_file = transform_data()

    # Tarefa de Carga no Banco de Dados
    load_data = load_data_to_db(transform_file, upstream_tasks=[transform_file])

    # Executar o Modelo DBT
    materialize_model(upstream_tasks=[transform_file, load_data])