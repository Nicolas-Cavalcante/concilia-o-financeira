import os

def salvar(df_final, df_nao_localizados, path_corretos, path_incorretos):

    df_final.to_excel(path_corretos / "Corretos.xlsx", index=False)
    df_nao_localizados.to_excel(path_incorretos / "Incorretos.xlsx", index=False)