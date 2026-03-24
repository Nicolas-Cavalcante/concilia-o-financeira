from datetime import datetime

def definir_destinatarios(dias_para_corte, df_base_email):

    df_base_email['E-mail Célula'] = df_base_email['E-mail Célula'].astype(str).str.lower().str.strip()

    # separa grupos
    operacao = (
    df_base_email['E-mail Célula']
    .dropna()
    .astype(str)
    .str.lower()
    .str.strip()
)

    operacao = operacao[operacao != "nan"].tolist()
    #gestao = df_base_email[df_base_email['tipo'] == 'gestao']['email'].dropna().tolist()
    #diretoria = df_base_email[df_base_email['tipo'] == 'diretoria']['email'].dropna().tolist()

        #Busca dia e semana atual do processamento
    hoje = datetime.today()
    dia_semana = hoje.weekday() # 0=segunda, 6=domingo

    if dias_para_corte == -4 and dia_semana >= 5:
    
        print("⚠️ Hoje é fim de semana e deveria ter sido enviado na sexta")

        # Aqui você decide:
        # opção 1 → NÃO envia
        return []
    
            # opção 2 → força envio
        # return list(set(operacao + gestao + diretoria))

            # regras normais
    if dias_para_corte <= 28 and dias_para_corte >= 10:
        return list(set(operacao))
    else:
        return operacao