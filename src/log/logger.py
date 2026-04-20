import pandas as pd
import os

#==============================================
# 📌 Carrega LOG de Excução detalhado
#==============================================

def registrar_execucao_chaves(path, df_log_chaves):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        try:
            df_hist = pd.read_excel(path)
            df_final = pd.concat([df_hist, df_log_chaves], ignore_index=True)
        except:
            df_final = df_log_chaves
    else:
        df_final = df_log_chaves

    df_final.to_excel(path, index=False)

#==============================================
# 📌 Carrega LOG de Excução detalha
#==============================================

def registra_execucao_detalhada(path, df_log):

    # Garante que a pasta exista
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # =========================
    # CARREGA HISTÓRICO
    # =========================
    if os.path.exists(path):
        try:
            df_hist = pd.read_excel(path)
        except:
            df_hist = pd.DataFrame()
    else:
        df_hist = pd.DataFrame()

    # =========================
    # ENCONTRA PRIMEIRA OCORRÊNCIA
    # =========================
    
    if not df_hist.empty:
        df_primeira = (
            df_hist.groupby('chave_match')['data_execucao']
            .min()
            .reset_index()
            .rename(columns={'data_execucao': 'data_primeira_ocorrencia'})
        )

        df_log = df_log.merge(
            df_primeira,
            on='chave_match',
            how='left'
        )
    else:
        df_log['data_primeira_ocorrencia'] = pd.NaT

    # =========================
    # DEFINE PRIMEIRA OCORRÊNCIA
    # =========================
    df_log['data_primeira_ocorrencia'] = df_log['data_primeira_ocorrencia'].fillna(df_log['data_execucao'])


    # =========================
    # CALCULA AGING
    # =========================
    df_log['dias_em_aberto'] = (
        df_log['data_execucao'] - df_log['data_primeira_ocorrencia']
    ).dt.days

    # =========================
    # SALVA HISTÓRICO (APPEND)
    # =========================
    df_final = pd.concat([df_hist, df_log], ignore_index=True)

    df_final.to_excel(path, index=False)
