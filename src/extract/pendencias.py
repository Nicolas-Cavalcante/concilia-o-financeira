import pandas as pd
from pathlib import Path
from src.erros import SmartCheckError


#==============================================
# 📑 CARREGA BASE DE PENDêNCIAS
#==============================================

def carregar_planilha(path):
    tentativas = [
        (3, {"Nome da Empresa", "Autorização"}),
        (0, {"Nome da Empresa", "Autorização"}),
        (0, {"Empresa", "Aut"}),
    ]
    abas_analisadas_pendencia = []

    for header, colunas_esperadas in tentativas:
        abas = pd.read_excel(path, header=header, sheet_name=None)

        for nome_aba, df in abas.items():
            abas_analisadas_pendencia.append(f"{nome_aba} (header={header})")

            if colunas_esperadas.issubset(df.columns):
                return df
        
    raise SmartCheckError(
        "Arquivo de pendências fora do padrão esperado: nenhuma aba contém as colunas obrigatórias "
        "{'Nome da Empresa', 'Autorização'} ou {'Empresa', 'Aut'}. "
        f"Abas analisadas: {abas_analisadas_pendencia}"
    )


#==============================================
# 📑 CARREGA DE_PARA DE CAMPOS GERÊNCIAIS
#==============================================

def _normalizar_depara(df):
    renomear = {
        "Campo Arquivo do Cliente": "Campo Arquivo do cliente",
        "Campo arquivo do cliente": "Campo Arquivo do cliente",
    }
    df = df.rename(columns=renomear)

    colunas_esperadas = {"Cliente", "Campo Arquivo do cliente", "Nome do Campo"}
    if colunas_esperadas.issubset(df.columns):
        return df

    if {"Cliente", "Campo", "De", "Para"}.issubset(df.columns):
        return pd.DataFrame(columns=list(colunas_esperadas))

    faltando = colunas_esperadas - set(df.columns)
    raise SmartCheckError(f"De-para inválido. Faltando: {faltando}")


input_path = None

if not input_path:
    pasta = Path("inputs")
    arquivos = list(pasta.glob("*De_Para_campos_gerenciais_EBTA*.xlsx"))

    if not arquivos:
        raise SmartCheckError("Nenhum arquivo .xlsx encontrado na pasta inputs")

    input_path = max(arquivos, key=lambda f: f.stat().st_mtime)

df_depara = _normalizar_depara(pd.read_excel(input_path))
