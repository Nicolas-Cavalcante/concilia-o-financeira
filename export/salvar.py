import os

def salvar(df_final, df_nao_localizados, base_path):

    os.makedirs(f"{base_path}/corretos", exist_ok=True)
    os.makedirs(f"{base_path}/incorretos", exist_ok=True)

    df_final.to_excel(f"{base_path}/corretos/preenchidos.xlsx", index=False)
    df_nao_localizados.to_excel(f"{base_path}/incorretos/nao_localizados.xlsx", index=False)