import pandas as pd
from pathlib import Path

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
        
    raise ValueError(
        "Arquivo fora do padrão esperado: nenhuma aba contém as colunas obrigatórias "
        f"{colunas_esperadas}. Abas encontradas {abas_analisadas_pendencia}"
    )


#==============================================
# 📑 CARREGA DE_PARA DE CAMPOS GERÊNCIAIS
#==============================================

input_path = None

if not input_path:
    pasta = Path(r"C:\Users\nicolas.cavalcante\OneDrive - BEFLY TRAVEL\Documentos\GitHub\projeto-conciliacao_ebta\inputs")
    arquivos = list(pasta.glob("*.xlsx"))

    if not arquivos:
        raise ValueError("Nenhum arquivo .xslx encontrado na pasta inputs")

    input_path = max(arquivos, key=lambda f: f.stat().st_mtime)