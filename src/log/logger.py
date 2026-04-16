import pandas as pd
import os

## Define colunas que sairão no arquivo histórico_execucao na pasta logs
COLUNAS_LOG = [
    "id_execucao",
    "data_execucao",
    "qtd_total",
    "qtd_corretos",
    "qtd_nao_localizados",
    "status_execucao",
    "email_enviado"
    #"tipo_envio",
    #"dias_para_corte"
]

#==============================================
# 📌 Carrega LOG de Excução detalhado (executa sempre)
#==============================================

def registrar_execucao(path, dados):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        try:
            df = pd.read_excel(path)
        except:
            df = pd.DataFrame(columns=COLUNAS_LOG)
    else:
        df = pd.DataFrame(columns=COLUNAS_LOG)

    novo = pd.DataFrame([dados])

    df = pd.concat([df, novo], ignore_index=True)

    df.to_excel(path, index=False)

#==============================================
# 📌 Carrega LOG de Excução detalhado (executa sempre)
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
            df_hist = pd.DataFrame(columns=df_log.columns)
    else:
        df_hist = pd.DataFrame(columns=df_log.columns)

    # =========================
    # ENCONTRA PRIMEIRA OCORRÊNCIA
    # =========================
    if not df_hist.empty:
        df_primeira = (
            df_hist.groupby('chave_registro')['data_execucao']
            .min()
            .reset_index()
            .rename(columns={'data_execucao': 'data_primeira_ocorrencia'})
        )

        df_log = df_log.merge(
            df_primeira,
            on='chave_registro',
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



#==============================================
# 📌 Carrega LOG de Excução detalhado (executa sempre)
#==============================================


def registra_execucao_cliente(path, df_log_cliente):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        try:
            df_hist = pd.read_excel(path)
        except:
            df_hist = pd.DataFrame(columns=df_log_cliente.columns)
    else:
        df_hist = pd.DataFrame(columns=df_log_cliente.columns)

    df_final = pd.concat([df_hist, df_log_cliente], ignore_index=True)

    df_final.to_excel(path, index=False)