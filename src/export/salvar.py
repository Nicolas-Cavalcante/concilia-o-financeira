import os

def salvar(df_final, df_nao_localizados, base_path):

    os.makedirs(f"{base_path}/Corretos", exist_ok=True)
    os.makedirs(f"{base_path}/Incorretos", exist_ok=True)

    df_final.to_excel(f"{base_path}/Corretos/preenchidos.xlsx", index=False)
    df_nao_localizados.to_excel(f"{base_path}/Incorretos/Pendências_EBTA.xlsx", index=False)