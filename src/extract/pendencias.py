import pandas as pd
from pathlib import Path
from src.erros import SmartCheckError

#==============================================
# 📑 CARREGA BASE DE PENDêNCIAS
#==============================================

def carregar_planilha(path):
    abas = pd.read_excel(path, header=3, sheet_name=None)

    colunas_esperadas = {"Nome da Empresa", "Autorização"}
    abas_analisadas_pendencia = []

    for nome_aba, df in abas.items():
        abas_analisadas_pendencia.append(nome_aba)

        if colunas_esperadas.issubset(df.columns):
            return df
        
    raise SmartCheckError(
        "Arquivo de pendências fora do padrão esperado: nenhuma aba contém as colunas obrigatórias "
        f"{colunas_esperadas}. Abas encontradas {abas_analisadas_pendencia}"
    )


#==============================================
# 📑 CARREGA DE_PARA DE CAMPOS GERÊNCIAIS
#==============================================

input_path = None

if not input_path:
    pasta = Path("inputs")
    arquivos = list(pasta.glob("*De_Para_campos_gerenciais_EBTA*.xlsx"))

    if not arquivos:
        raise SmartCheckError("Nenhum arquivo .xslx encontrado na pasta inputs")

    input_path = max(arquivos, key=lambda f: f.stat().st_mtime)

df_depara = pd.read_excel(input_path)




## adicionar posteriormente para evitar quebra silenciosa

#colunas_esperadas = {'Cliente', 'Campo Arquivo do Cliente', 'Nome do Campo'}

#faltando = colunas_esperadas - set(df_depara.columns)

#if faltando:
#    raise ValueError(f"De-para inválido. Faltando: {faltando}")