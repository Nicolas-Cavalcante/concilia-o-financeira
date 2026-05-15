from datetime import datetime

def definir_destinatarios(dias_para_corte, df_base_email):

    df_base_email['EMAIl_CELULA_TESTE'] = df_base_email['EMAIl_CELULA_TESTE'].astype(str).str.lower().str.strip()

    # separa grupos
    operacao = (
    df_base_email['EMAIl_CELULA_TESTE']
    .dropna()
    .astype(str)
    .str.lower()
    .str.strip()
)

    operacao = operacao[operacao != "nan"].tolist()

            # regras normais
    if dias_para_corte <= 28 and dias_para_corte >= 10:
        return list(set(operacao))
    else:
        return operacao