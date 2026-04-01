import pandas as pd
from datetime import datetime

def tratar_dados(df):

    col = df['Nome da Cia Aérea'].fillna('')

    rloc_asterisco = col.str.extract(r"\*([A-Z0-9]{6})")
    rloc_final = col.str.extract(r"([A-Z0-9]{6})$")

    df['RLOC_CIA_TRATADO'] = rloc_asterisco[0].combine_first(rloc_final[0])

    df['Cia Aérea'] = df['Cia Aérea'].astype(str)
    df['Ticket'] = df['Ticket'].astype(str).str.strip().str.upper()

    mask_cia = df['Cia Aérea'].isin(['127', '577', '957'])
    mask_ticket = df['Ticket'].str.contains(r'^(?=.*[A-Z])(?=.*\d)[A-Z0-9]+$', regex=True)

    df['RLOC_CIA_CORRETO'] = ''
    df.loc[mask_cia, 'RLOC_CIA_CORRETO'] = df.loc[mask_cia, 'RLOC_CIA_TRATADO']
    df.loc[~mask_cia & mask_ticket, 'RLOC_CIA_CORRETO'] = df.loc[~mask_cia & mask_ticket, 'Ticket']

    df['Valor Total'] = df['Valor Total'].apply(
        lambda x: f"{x:.2f}" if pd.notnull(x) else x
    )

    df['Chave Cartão'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Data de Emissão'].astype(str) +
        df['Valor Total']
    )

    df['Chave Cartão + LOC CIA'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Data de Emissão'].astype(str) +
        df['Valor Total'] +
        df['RLOC_CIA_CORRETO']
    )

    df['Chave Cartão Sem data'] = (
        df['Cartão'].astype(str).str[-3:] +
        df['Valor Total'] +
        df['RLOC_CIA_CORRETO']
    )

    #Cria coluna data de fechamento
    data_execucao = pd.Timestamp.today().normalize()

    df['Data Fechamento Cartão'] = data_execucao + pd.to_timedelta(df['Aging Corte'] + 4, unit='D')

    return df