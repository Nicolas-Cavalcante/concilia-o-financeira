import pandas as pd
from datetime import datetime
from src.extract.pendencias import df_depara

def tratar_dados(df):

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

    df['RLOC_CIA_CORRETO'] = df['RLOC_CIA_CORRETO'].fillna('')

    df['Valor Total'] = df['Valor Total'].apply(
        lambda x: f"{x:.2f}" if pd.notnull(x) else x
    )

    df['sigla_grupo'] = df.merge(
        df_depara,
        on='Nome da Empresa',
        how='left'
    )

    # Cria Chave Aut + Data + Valor como KEY 1
    df['Chave Aut + Data + Valor'] = (
        df['Autorização'].astype(str) +
        df['Data de Emissão'].astype(str) +
        df['Valor Total']
    )

    # Cria chave Cartão + Data + Valor como KEY 2
    df['Chave Loc Cia + Data + Valor'] = (
        df['RLOC_CIA_CORRETO'].astype(str) +
        df['Data de Emissão'].astype(str) +
        df['Valor Total']
    )

    # Cria chave Cartão + Data + Valor como KEY 3
    df['Chave Cartão + Data + Valor'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Data de Emissão'].astype(str) +
        df['Valor Total']
    )

    # Cria chave Cartão + Data + Valor + loc Cia como KEY 4
    df['Chave Cartão + Data + Valor + Loc Cia'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Data de Emissão'].astype(str) +
        df['Valor Total'] +
        df['RLOC_CIA_CORRETO'].astype(str)
    )

    # Cria chave Cartão + Valor + Loc Cia como KEY 5
    df['Chave Cartão + Valor + Loc Cia'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Valor Total'] +
        df['RLOC_CIA_CORRETO'].astype(str)
    )

    df['Chave Sigla + Aut + Valor'] = (
        df['sigla_grupo'].astype(str) +
        df['Autorização'].astype(str) + 
        df['Valor Total']
    )

    # Cria Chave de registro para o log_micro
    df['chave_registro'] = (
        df['Nome da Empresa'].astype(str) +
        df['Chave Aut + Data + Valor'].astype(str)
    )

    #Cria coluna data de fechamento
    data_execucao = pd.Timestamp.today().normalize()
    hoje = pd.Timestamp.today().normalize()

    df['Data Fechamento Cartão'] = data_execucao + pd.to_timedelta(df['Aging Corte'] + 4, unit='D')
    df['Dias Restantes'] = (df['Data Fechamento Cartão'] - hoje).dt.days

    df['Emissor'] = ''


    return df