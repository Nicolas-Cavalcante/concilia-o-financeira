import pandas as pd
from src.erros import SmartCheckError


def carregar_base_email(path):
    abas = pd.read_excel(path, sheet_name=None)

    colunas_esperadas = {"SQUADS", "Nº Cliente/COMP"}
    abas_analisadas = []

    for nome_aba, df in abas.items():
        abas_analisadas.append(nome_aba)
        
        if colunas_esperadas.issubset(df.columns):
            return _normalizar_base_email(df)
        
    raise SmartCheckError(
        "Arquivo de emails fora do padrão esperado: nenhuma aba contém as colunas obrigatórias "
        f"{colunas_esperadas}. Abas encontradas: {abas_analisadas}"
    )


def _normalizar_base_email(df):
    df = df.copy()
    comp = df["Nº Cliente/COMP"].astype(str).str.strip()

    if comp.str.startswith("{").all() and "SQUADS" in df.columns:
        df["Nº Cliente/COMP"] = df["SQUADS"].astype(str).str.strip()
    else:
        df["Nº Cliente/COMP"] = comp

    return df
