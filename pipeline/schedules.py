from datetime import timedelta, datetime
from prefect.schedules import IntervalSchedule
import pytz

# Definição do Intervalo de Agendamento
minute_brt_data = IntervalSchedule(
    # Fuso horário utilizado de SP
    start_date=datetime.now(pytz.timezone('America/Sao_Paulo')) + timedelta(seconds=1),
    # Precisa-se de dados de no mínimo 10 pontos.
    end_date=datetime.now(pytz.timezone("America/Sao_Paulo")) + timedelta(minutes=11),
    # Dados capturados de minuto a minuto
    interval=timedelta(minutes=1)
)