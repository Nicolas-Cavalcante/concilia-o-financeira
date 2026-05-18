import pandas as pd
import numpy as np
from datetime import datetime
from src.extract.pendencias import df_depara


# =========================
# 📝 ESTE ARQUIVO É RESPONSÁVEL POR TRATAR OS DADOS QUE VEM DO ARQUIVO DE PENDENCIAS DO BANCO, TRATANDO DADOS INDESEJADOS,
# CRIANDO NOVAS COLUNAS E CHAVES PARA CONCILIAÇÃO.
# =========================

def tratar_dados(df, df_email):

    #==============================================
    # TRATA COLUNAS PARA CRIAÇÃO DE CHAVES E AJUSTES NO ARQUIVO FINAL
    #==============================================
    col = df['Nome da Cia Aérea'].fillna('')

    rloc_asterisco = col.str.extract(r"\*([A-Z0-9]{6})")
    rloc_final = col.str.extract(r"([A-Z0-9]{6})$")

    df['RLOC_CIA_TRATADO'] = rloc_asterisco[0].combine_first(rloc_final[0])

    df['Cia Aérea'] = df['Cia Aérea'].astype(str)
    df['Ticket'] = df['Ticket'].astype(str).str.strip().str.upper()

    mask_cia = df['Cia Aérea'].isin(['127', '577', '957'])
    mask_ticket = df['Ticket'].str.contains(r'^(?=.*[A-Z])(?=.*\d)[A-Z0-9]+$', regex=True)

    df['Ticket'] = df['Ticket'].fillna('')

    df['RLOC_CIA_CORRETO'] = ''
    df.loc[mask_cia, 'RLOC_CIA_CORRETO'] = df.loc[mask_cia, 'RLOC_CIA_TRATADO']
    df.loc[~mask_cia & mask_ticket, 'RLOC_CIA_CORRETO'] = df.loc[~mask_cia & mask_ticket, 'Ticket']

    df['RLOC_CIA_CORRETO'] = np.where(
        df['RLOC_CIA_CORRETO'] == '',
        df['RLOC_CIA_TRATADO'],
        df['RLOC_CIA_CORRETO']
        )

    df['RLOC_CIA_CORRETO'] = df['RLOC_CIA_CORRETO'].fillna('')

    # Ajusta taxa de embarque para float, igualando dados entre df_sql x df_planilha
    df['Taxa de Embarque'] = df['Taxa de Embarque'].astype(float)
    
    # Força asterisco nas colunas Classe e data ida, pois não vem formatado do bradesco
    df['Classe'] = '**********'
    df['Data Ida'] = '**********'

    # Cria Valor Total str para não alterar a configuração da coluna de valor original
    df['Valor Total str'] = df['Valor Total'].apply(
        lambda x: f"{x:.2f}" if pd.notnull(x) else x
    )

    df['Valor Total'] = df['Valor Total'].astype(float)

    df['SQUADS'] = df.merge(
        df_email[['Nº Cliente/COMP', 'SQUADS']],
        on='Nº Cliente/COMP',
        how='left'
    )['SQUADS']

    #==============================================
    # CRIA COLUNA DE DATA DE FECHAMENTO, DIAS RESTANTES E SETA EMISSOR
    # COMO VAZIO PARA PREENCHIMENTO POSTERIOR
    #==============================================

    data_execucao = pd.Timestamp.today().normalize()
    hoje = pd.Timestamp.today().normalize()

    # Data de fechamento original
    df['Data Fechamento Cartão'] = data_execucao + pd.to_timedelta(df['Aging Corte'] + 4, unit='D')

    # Ajusta para sexta se cair em fim de semana
    # dayofweek: 5 = sábado, 6 = domingo
    dia_semana = df['Data Fechamento Cartão'].dt.dayofweek
        
    df['Data Fechamento Cartão'] = df['Data Fechamento Cartão'] - pd.to_timedelta(
        np.where(dia_semana == 5, 1,   # sábado → volta 1 dia (sexta)
        np.where(dia_semana == 6, 2,   # domingo → volta 2 dias (sexta)
        0)),                           # dia útil → não mexe
        unit='D'
    )

    df['Dias Restantes'] = (df['Data Fechamento Cartão'] - hoje).dt.days

    df['Data Fechamento Cartão'] = df['Data Fechamento Cartão'].dt.strftime('%d/%m/%Y')

    df['Data de Emissão'] = df['Data de Emissão'].dt.strftime('%d/%m/%Y')

    df['Emissor'] = ''

    #==============================================
    # CRIA CHAVES DE CONCILIAÇÃO DO ARQUIVO
    #==============================================

    # Cria Chave Aut + Data + Valor como KEY 1
    df['Chave Aut + Data + Valor'] = (
        df['Autorização'].astype(str) +
        df['Data de Emissão'].astype(str) +
        df['Valor Total str']
    )

    # Cria Chave Aut + Data + Valor como KEY 2
    df['Chave nr_aut + Data + Valor'] = (
        df['Autorização'].astype(str) +
        df['Data de Emissão'].astype(str) +
        df['Valor Total str']
    )

    # Cria chave Cartão + Data + Valor como KEY 3
    df['Chave Loc Cia + Data + Valor'] = (
        df['RLOC_CIA_CORRETO'].astype(str) +
        df['Data de Emissão'].astype(str) +
        df['Valor Total str']
    )

    # Cria chave Cartão + Data + Valor + loc Cia como KEY 4
    df['Chave Cartão + Data + Valor + Loc Cia'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Data de Emissão'].astype(str) +
        df['Valor Total str'] +
        df['RLOC_CIA_CORRETO'].astype(str)
    )

    # Cria chave Cartão + Valor + Loc Cia como KEY 5
    df['Chave Cartão + Valor + Loc Cia'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Valor Total str'] +
        df['RLOC_CIA_CORRETO'].astype(str)
    )

    # Cria Chave de registro para o log_micro
    df['chave_registro'] = (
        df['Nome da Empresa'].astype(str) +
        df['Chave Aut + Data + Valor'].astype(str)
    )
   
    return df