import pandas as pd

# O Bloco abaixo permite executar esse módulo filho sem usar o main
#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def carregar_base_email(path):
    abas = pd.read_excel(path, sheet_name=None)

    colunas_esperadas = {"Cliente Conciliadora", "SQUADS"}
    abas_analisadas = []

    for nome_aba, df in abas.items():
        abas_analisadas.append(nome_aba)
        
        if colunas_esperadas.issubset(df.columns):
            return df
        
    raise ValueError(
        "Arquivo fora do padrão esperado: nenhuma aba contém as colunas obrigatórias "
        f"{colunas_esperadas}. Abas encontradas: {abas_analisadas}"
    )