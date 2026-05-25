import pandas as pd
import numpy as np
from pandas.api.types import is_datetime64_any_dtype
from src.extract.pendencias import df_depara


# =========================
# 📝 ESTE ARQUIVO É RESPONSÁVEL POR TRATAR OS DADOS QUE VEM DO ARQUIVO DE PENDENCIAS DO BANCO, TRATANDO DADOS INDESEJADOS,
# CRIANDO NOVAS COLUNAS E CHAVES PARA CONCILIAÇÃO.
# =========================

COLUNAS_DEMO = {"Empresa", "Data", "Valor", "Aut", "Loc Cia", "Cartao"}


def tratar_dados(df, df_email):
    df = _normalizar_layout_demo(df)

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
    df['Taxa de Embarque'] = pd.to_numeric(df['Taxa de Embarque'], errors='coerce').fillna(0.0)
    
    # Força asterisco nas colunas Classe e data ida, pois não vem formatado do bradesco
    df['Classe'] = '**********'
    df['Data Ida'] = '**********'

    df['Valor Total'] = pd.to_numeric(df['Valor Total'], errors='coerce')

    # Cria Valor Total str para não alterar a configuração da coluna de valor original
    df['Valor Total str'] = df['Valor Total'].apply(
        lambda x: f"{x:.2f}" if pd.notnull(x) else ''
    )

    df = _aplicar_squads(df, df_email)

    #==============================================
    # CRIA COLUNA DE DATA DE FECHAMENTO, DIAS RESTANTES E SETA EMISSOR
    # COMO VAZIO PARA PREENCHIMENTO POSTERIOR
    #==============================================

    data_execucao = pd.Timestamp.today().normalize()
    hoje = pd.Timestamp.today().normalize()

    df['Aging Corte'] = pd.to_numeric(df['Aging Corte'], errors='coerce').fillna(0)

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

    if not is_datetime64_any_dtype(df['Data de Emissão']):
        df['Data de Emissão'] = pd.to_datetime(df['Data de Emissão'], errors='coerce', dayfirst=True)
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


def _normalizar_layout_demo(df):
    if not (COLUNAS_DEMO.issubset(df.columns) and 'Nome da Empresa' not in df.columns):
        return df.copy()

    df = df.copy()
    loc_cia = df['Loc Cia'].fillna('').astype(str).str.upper()

    colunas_demo = {
        'MatchID': range(1, len(df) + 1),
        'Aging Venda': 0,
        'Aging Corte': 10,
        'Nº Cliente/COMP': df['Empresa'].astype(str).str.strip(),
        'Cartão': df['Cartao'].astype(str).str.strip(),
        'Agência': '',
        'Nome da Empresa': df['Empresa'].astype(str).str.strip(),
        'Autorização': df['Aut'].astype(str).str.strip(),
        'Data de Emissão': pd.to_datetime(df['Data'], errors='coerce'),
        'Valor Total': pd.to_numeric(df['Valor'], errors='coerce'),
        'Valor Bilhete (Travel)': pd.to_numeric(df['Valor'], errors='coerce'),
        'Cia Aérea': '001',
        'Nome da Cia Aérea': 'CIA DEMO *' + loc_cia,
        'Ticket': '',
        'Débito/Fee': 0,
        'Desconto/Rebate': 0,
        'Centro de Custo': '',
        'Data Ida': '',
        'Data Volta': '',
        'Passageiro': df.get('Passageiro', ''),
        'Trecho Voado': '',
        'Classe': '',
        'Departamento': '',
        'Matricula': '',
        'Requisição': '',
        'Solicitante': '',
        'Aprovador': '',
        'Localizador': '',
        'Livre 1': '',
        'Livre 2': '',
        'Livre 3': '',
        'Empresa Empregado': '',
        'Taxa de Embarque': 0,
        'Taxa de Repasse': 0,
        'Tipo': 'DEMO',
    }

    for coluna, valor in colunas_demo.items():
        if coluna not in df.columns:
            df[coluna] = valor

    return df


def _normalizar_comp(serie):
    return serie.where(serie.notna(), '').astype(str).str.strip()


def _aplicar_squads(df, df_email):
    df = df.copy()
    df_email = df_email.copy()

    df['Nº Cliente/COMP'] = _normalizar_comp(df['Nº Cliente/COMP'])
    df_email['Nº Cliente/COMP'] = _normalizar_comp(df_email['Nº Cliente/COMP'])

    df['SQUADS'] = df.merge(
        df_email[['Nº Cliente/COMP', 'SQUADS']],
        on='Nº Cliente/COMP',
        how='left'
    )['SQUADS']

    if df['SQUADS'].isna().all() and 'Empresa' in df.columns:
        df['SQUADS'] = df['Empresa'].astype(str).str.strip()

    return df
