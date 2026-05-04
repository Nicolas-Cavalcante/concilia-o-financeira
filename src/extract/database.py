import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

def carregar_sql():

    # Usa Load_dotenv para ler o arquivo .env
    server = os.getenv('DB_Server')
    database = os.getenv('DB_Database')
    username = os.getenv('DB_User')
    password = os.getenv('DB_Password')

    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    )
    # Hoje com horário zerado
    hoje = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    # Primeiro dia do mês atual
    meses_atras = 3

    #Calcular o primeiro dia do mês de partida
    ano = hoje.year
    mes = hoje.month

    for _ in range(meses_atras):
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1

    data_inicial = datetime(ano, mes, 1)

    # Último dia do mês atual (para a data final)
    ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
    data_final = hoje.replace(day=ultimo_dia, hour=23, minute=59, second=59)

   # ===== QUERY SQL =====
    query = f"""
        SELECT
            SO.nm_cliente,
            SO.nr_autorizacao_cartao,
            SO.AUTORIZACAOCARTAOAMEX,
            SO.tipo_pagamento,
            SO.loc_reserva AS Localizador,
            SO.INFOS AS OS,
            SO.id_nro_bilhete AS Bilhete,
            SO.nr_cartao_mascarado,
            SO.dt_movimento,
            SO.vl_online_cliente,
            concat(SO.AUTORIZACAOCARTAOAMEX, SO.dt_movimento, SO.vl_online_cliente) AS [Chave Aut + Data + Valor], 
            concat(SO.nr_autorizacao_cartao, SO.dt_movimento, SO.vl_online_cliente) AS [Chave nr_aut + Data + Valor],
            concat(SO.loc_reserva, SO.dt_movimento, SO.vl_online_cliente) AS [Chave Loc Cia + Data + Valor],
            concat(SO.nr_cartao_mascarado, SO.dt_movimento, SO.vl_online_cliente, SO.loc_reserva) AS [Chave Cartão + Data + Valor + Loc Cia],
            concat(SO.nr_cartao_mascarado, SO.vl_online_cliente, SO.loc_reserva) AS [Chave Cartão + Valor + Loc Cia],
            SO.ds_centro_custo_cliente AS [Centro de Custo],
            SO.cod_centro_custo,
            SO.nm_passageiro AS [Nome do Passageiro],
            SO.matricula AS Matricula,
            SO.ds_solicitante AS [Nome do Solicitante],
            SO.INFAPROVADOR AS Aprovador,
            SO.dsc_rota AS Trecho,
            SO.INFDIVISAO AS Departamento,
            SO.INFPOLITICA,
            SO.CONVIDADO,
            SO.nm_emissor AS Emissor
        FROM
        (SELECT
            DC.nm_cliente,
            nr_autorizacao_cartao,
            AUTORIZACAOCARTAOAMEX,
            DTP.dsc_tipo_pagto AS tipo_pagamento,
            loc_reserva,
            INFOS,
            CAST(id_nro_bilhete AS VARCHAR(50)) AS id_nro_bilhete,
            RIGHT(nr_cartao_mascarado, 3) AS nr_cartao_mascarado,
            FORMAT(dt_movimento, 'yyyy-MM-dd') AS dt_movimento, 
            CAST(
                ISNULL(vl_online_cliente, 0) 
                + ISNULL(vl_taxa_embarque, 0) 
                + (ISNULL(vl_tx_du, 0) / 10000.0)
            AS DECIMAL(18,2)) AS vl_online_cliente,
            ds_centro_custo_cliente,
            FA.cod_centro_custo,
            DP.nm_passageiro,
            matricula,
            DS.ds_solicitante,
            INFAPROVADOR,
            DR.dsc_rota,
            INFDIVISAO,
            INFPOLITICA,
            CONVIDADO,
            EM.nm_emissor
        FROM fato_aereo FA
            LEFT JOIN dim_cliente DC ON FA.id_cliente = DC.id_cliente
            LEFT JOIN dim_passageiro DP ON FA.id_passageiro = DP.id_passageiro 
            LEFT JOIN dim_contato_solicitante DS ON FA.id_solicitante = DS.id_solicitante
            LEFT JOIN dim_rota DR ON FA.id_rota = DR.id_rota
            LEFT JOIN dim_emissor EM ON FA.id_emissor = EM.id_emissor
            LEFT JOIN dim_tipo_pagamento DTP ON FA.id_tipo_pagamento = DTP.id_tipo_pagamento
            WHERE FA.id_divisao IN (2000, 7000)
            AND nr_cartao_mascarado is not null
            AND dt_movimento between '{data_inicial}' AND '{data_final}'
            ) SO
    """
    print(f"buscando dados de {data_inicial} até {data_final}")

    df_sql = pd.read_sql(query, conn)

    conn.close()

    return df_sql