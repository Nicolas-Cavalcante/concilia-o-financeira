from datetime import datetime

def definir_destinatarios(dias_para_corte, config):

    #Busca dia e semana atual do processamento
    hoje = datetime.today()
    dia_semana = hoje.weekday() # 0=segunda, 6=domingo

    #Ajuste em casos de fim de semana
    if dias_para_corte == -4 and dia_semana >= 5:
        dias_para_corte = -4 # mas deveria ter sido tratado antes (sexta)

    # Regras
    if dias_para_corte <= 0:
        return config.EMAIL_OPERACAO + config.EMAIL_GESTAO + config.EMAIL_DIRETORIA

    elif dias_para_corte <= config.DIAS_ALERTA:
        return config.EMAIL_OPERACAO + config.EMAIL_GESTAO

    else:
        return config.EMAIL_OPERACAO