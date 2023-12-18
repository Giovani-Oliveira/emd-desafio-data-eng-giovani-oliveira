

SELECT codigo_onibus,
       -- PostGIS precisa estar instalado
       ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')', 4326) AS posicao,
       velocidade
from raw.tb_brt_gps