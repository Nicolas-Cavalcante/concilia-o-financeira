import calendar
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import EXEC_DIR


COLUNAS_CHAVE = [
    "Chave Aut + Data + Valor",
    "Chave nr_aut + Data + Valor",
    "Chave Loc Cia + Data + Valor",
    "Chave Cartão + Data + Valor + Loc Cia",
    "Chave Cartão + Valor + Loc Cia",
    "dt_movimento",
]


def carregar_sql():
    data_inicial, data_final = _calcular_periodo_consulta()

    if _usar_sqlite_demo():
        df_sql = _carregar_sqlite(data_inicial, data_final)
    else:
        df_sql = _carregar_sql_server(data_inicial, data_final)

    return _normalizar_retorno_sql(df_sql)


def _calcular_periodo_consulta():
    hoje = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    meses_atras = 3

    ano = hoje.year
    mes = hoje.month

    for _ in range(meses_atras):
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1

    data_inicial = datetime(ano, mes, 1)
    ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
    data_final = hoje.replace(day=ultimo_dia, hour=23, minute=59, second=59)

    return data_inicial, data_final


def _env(nome):
    valor = os.getenv(nome)
    return valor.strip() if valor else ""


def _flag_ativa(valor):
    return str(valor).strip().lower() in {"1", "true", "yes", "sim", "s"}


def _usar_sqlite_demo():
    engine = (
        _env("DB_Engine")
        or _env("DB_ENGINE")
        or _env("DB_Mode")
        or _env("DB_MODE")
    ).lower()

    if engine:
        return engine in {"sqlite", "sqlite3", "demo", "local"}

    if _flag_ativa(os.getenv("DEMO_MODE")) or _flag_ativa(os.getenv("USE_DEMO_DB")):
        return True

    return not _env("DB_Server")


def _resolver_demo_db_path():
    db_path = Path(_env("DB_SQLITE_PATH") or "demo.db")
    if not db_path.is_absolute():
        db_path = EXEC_DIR / db_path
    return db_path


def _carregar_sqlite(data_inicial, data_final):
    db_path = _resolver_demo_db_path()

    if not db_path.exists():
        raise FileNotFoundError(
            f"Banco SQLite demo não encontrado em: {db_path}. "
            "Gere o arquivo com generate_mock_data.py ou ajuste DB_SQLITE_PATH no .env."
        )

    query = """
        SELECT
            empresa AS nm_cliente,
            nr_aut AS nr_autorizacao_cartao,
            aut AS AUTORIZACAOCARTAOAMEX,
            'Cartão demo' AS tipo_pagamento,
            loc_cia AS Localizador,
            'DEMO-' || id AS OS,
            CAST(bilhete AS TEXT) AS Bilhete,
            CAST(cartao AS TEXT) AS nr_cartao_mascarado,
            strftime('%d/%m/%Y', data) AS dt_movimento,
            printf('%.2f', valor) AS vl_online_cliente,
            CAST(aut AS TEXT) || strftime('%d/%m/%Y', data) || printf('%.2f', valor)
                AS [Chave Aut + Data + Valor],
            CAST(nr_aut AS TEXT) || strftime('%d/%m/%Y', data) || printf('%.2f', valor)
                AS [Chave nr_aut + Data + Valor],
            CAST(loc_cia AS TEXT) || strftime('%d/%m/%Y', data) || printf('%.2f', valor)
                AS [Chave Loc Cia + Data + Valor],
            CAST(cartao AS TEXT) || strftime('%d/%m/%Y', data) || printf('%.2f', valor) || CAST(loc_cia AS TEXT)
                AS [Chave Cartão + Data + Valor + Loc Cia],
            CAST(cartao AS TEXT) || printf('%.2f', valor) || CAST(loc_cia AS TEXT)
                AS [Chave Cartão + Valor + Loc Cia],
            'Centro demo' AS [Centro de Custo],
            'CC-DEMO' AS cod_centro_custo,
            passageiro AS [Nome do Passageiro],
            '000000' AS Matricula,
            'Solicitante demo' AS [Nome do Solicitante],
            'Aprovador demo' AS Aprovador,
            trecho AS Trecho,
            'Departamento demo' AS Departamento,
            '' AS INFPOLITICA,
            '' AS CONVIDADO,
            'Emissor demo' AS Emissor,
            'Y' AS sgl_classe,
            strftime('%d/%m/%Y', data) AS [Data Ida],
            0.0 AS vl_taxa_embarque
        FROM transacoes
        WHERE date(data) BETWEEN date(?) AND date(?)
    """

    with sqlite3.connect(db_path) as conn:
        if not conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'transacoes'"
        ).fetchone():
            raise ValueError("O demo.db não possui a tabela esperada: transacoes.")

        return pd.read_sql(
            query,
            conn,
            params=(data_inicial.date().isoformat(), data_final.date().isoformat()),
        )


def _carregar_sql_server(data_inicial, data_final):
    import pyodbc

    server = _env("DB_Server")
    database = _env("DB_Database")
    username = _env("DB_User")
    password = _env("DB_Password")

    conn = pyodbc.connect(
        f"DRIVER={{SQL Server}};"
        f"SERVER={server};DATABASE={database};"
        f"UID={username};PWD={password}"
    )

    query = f"""
    SELECT
            SO.nm_cliente,
            SO.nr_autorizacao_cartao,
            SO.AUTORIZACAOCARTAOAMEX,
            SO.tipo_pagamento,
            SO.loc_reserva AS Localizador,
            SO.OS,
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
            SO.Departamento,
            SO.INFPOLITICA,
            SO.CONVIDADO,
            SO.nm_emissor AS Emissor,
            SO.sgl_classe,
            SO.[Data Ida],
            SO.vl_taxa_embarque
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
            FORMAT(CONVERT(date, dt_movimento), 'dd/MM/yyyy', 'pt-BR') AS dt_movimento, 
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
            CASE
                WHEN FA.id_divisao = 2000 THEN INFDIVISAO
                ELSE ds_departamento
            END AS Departamento,
            CASE
                WHEN FA.id_divisao = 2000 THEN INFOS
                ELSE nr_requisicao
            END AS OS,
            INFPOLITICA,
            CONVIDADO,
            EM.nm_emissor,
            DCV.sgl_classe,
            FORMAT(CONVERT(date, dt_embarque), 'dd/MM/yyyy', 'pt-BR') AS [Data Ida],
            vl_taxa_embarque
        FROM fato_aereo FA
            LEFT JOIN dim_cliente DC ON FA.id_cliente = DC.id_cliente
            LEFT JOIN dim_passageiro DP ON FA.id_passageiro = DP.id_passageiro 
            LEFT JOIN dim_contato_solicitante DS ON FA.id_solicitante = DS.id_solicitante
            LEFT JOIN dim_rota DR ON FA.id_rota = DR.id_rota
            LEFT JOIN dim_emissor EM ON FA.id_emissor = EM.id_emissor
            LEFT JOIN dim_tipo_pagamento DTP ON FA.id_tipo_pagamento = DTP.id_tipo_pagamento
            LEFT JOIN dim_classe_venda DCV ON FA.id_classe_venda = DCV.id_classe_venda
            WHERE FA.id_divisao IN (2000, 7000)
            AND nr_cartao_mascarado is not null
            AND dt_movimento between '{data_inicial}' AND '{data_final}'
            ) SO
    """

    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()


def _normalizar_retorno_sql(df_sql):
    for coluna in COLUNAS_CHAVE:
        if coluna in df_sql.columns:
            df_sql[coluna] = df_sql[coluna].fillna("").astype(str)

    if "Bilhete" in df_sql.columns:
        df_sql["Bilhete"] = df_sql["Bilhete"].fillna("").astype(str)
        mask_bilhete_numerico = df_sql["Bilhete"].str.fullmatch(r"\d{1,9}", na=False)
        df_sql.loc[mask_bilhete_numerico, "Bilhete"] = (
            df_sql.loc[mask_bilhete_numerico, "Bilhete"].str.zfill(10)
        )

    return df_sql
