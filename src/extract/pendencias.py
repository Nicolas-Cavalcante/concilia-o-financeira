import pandas as pd

def carregar_planilha(path):
    return pd.read_excel(path, header=3)