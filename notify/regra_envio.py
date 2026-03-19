from datetime import datetime

def definir_destinatarios(dias_para_corte, config):

    if dias_para_corte <= config.DIAS_CRITICO:
        return config.EMAIL_OPERACAO + config.EMAIL_GESTAO + config.EMAIL_DIRETORIA

    elif dias_para_corte <= config.DIAS_ALERTA:
        return config.EMAIL_OPERACAO + config.EMAIL_GESTAO

    else:
        return config.EMAIL_OPERACAO