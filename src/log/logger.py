import pandas as pd
import os
from datetime import datetime


## Define colunas que sairão no arquivo histórico_execucao na pasta logs
COLUNAS_LOG = [
    "id_execucao",
    "data_execucao",
    #"arquivo",
    "qtd_total",
    "qtd_corretos",
    "qtd_nao_localizados",
    "status_execucao",
    "email_enviado",
    "tipo_envio",
    "dias_para_corte"
]


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