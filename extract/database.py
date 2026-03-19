import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import calendar

def carregar_sql():

    server = 'msdwbi01.befly.com.br'
    database = 'DW_FLYTOUR'
    username = 'bi.dataquality_fbt'
    password = 'G7@kP2#q'

    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    )
    # Hoje com horário zerado
    hoje = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    # Primeiro dia do mês atual
    primeiro_dia_mes_atual = hoje.replace(day=1)

    # Volta 1 dia → cai no mês anterior
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)

    # Primeiro dia de 2 meses atrás
    primeiro_dia_dois_meses_atras = ultimo_dia_mes_anterior.replace(day=1) - timedelta(days=1)
    primeiro_dia_dois_meses_atras = primeiro_dia_dois_meses_atras.replace(day=1)

    # Último dia do mês atual
    ultimo_dia_mes_atual = hoje.replace(
        day=calendar.monthrange(hoje.year, hoje.month)[1],
        hour=23, minute=59, second=59
    )

    data_inicial = primeiro_dia_dois_meses_atras
    data_final = ultimo_dia_mes_atual

   # ===== QUERY SQL =====
    query = f"""
        select 
            SO.nr_cartao_mascarado,
            SO.dt_movimento,
            SO.vl_online_cliente,
            concat(SO.nr_cartao_mascarado, SO.dt_movimento, SO.vl_online_cliente) AS [Chave Cartão],
            concat(SO.nr_cartao_mascarado, SO.dt_movimento, SO.vl_online_cliente, SO.loc_reserva) AS [Chave Cartão + LOC CIA],
            concat(SO.nr_cartao_mascarado, SO.vl_online_cliente, SO.loc_reserva) AS [Chave Cartão Sem data],
            SO.loc_reserva AS Localizador,
            SO.INFOS AS OS,
            SO.id_nro_bilhete AS Bilhete,
            SO.ds_centro_custo_cliente AS [Centro de Custo],
            SO.nm_passageiro AS [Nome do Passageiro],
            SO.matricula AS Matricula,
            SO.ds_solicitante AS [Nome do Solicitante],
            SO.INFAPROVADOR AS Aprovador,
            SO.dsc_rota AS Trecho,
            SO.INFDIVISAO AS Departamento
        from
        (select 
            RIGHT(nr_cartao_mascarado, 3) AS nr_cartao_mascarado,
            FORMAT(dt_movimento, 'yyyy-MM-dd') AS dt_movimento, 
            CAST(vl_online_cliente + ISNULL(vl_taxa_embarque,0) AS DECIMAL(18,2)) AS vl_online_cliente,
            loc_reserva,
            INFOS,
            CAST(id_nro_bilhete AS VARCHAR(50)) AS id_nro_bilhete,
            ds_centro_custo_cliente,
            DP.nm_passageiro,
            matricula,
            DS.ds_solicitante,
            INFAPROVADOR,
            DR.dsc_rota,
            INFDIVISAO
        from fato_aereo FT
            left join dim_passageiro DP ON FT.id_passageiro = DP.id_passageiro 
            left join dim_contato_solicitante DS ON FT.id_solicitante = DS.id_solicitante
            left join dim_rota DR ON FT.id_rota = DR.id_rota  
            where id_divisao = 2000 
            and nr_cartao_mascarado is not null
            and dt_movimento between '{data_inicial}' AND '{data_final}'
            ) SO
    """

    df_sql = pd.read_sql(query, conn)

    conn.close()

    return df_sql