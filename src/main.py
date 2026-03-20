from src.extract.database import carregar_sql
from src.extract.pendencias import carregar_planilha
from src.transform.tratamento import tratar_dados
from src.matching.conciliacao import executar_matching
from src.export.salvar import salvar
from src import config
from datetime import datetime
from uuid import uuid4
from src.log.logger import registrar_execucao
from src import config
from src.notify.regra_envio import definir_destinatarios
from src.notify.email import enviar_email

def main():

    id_execucao = str(uuid4())
    data_execucao = datetime.now()

    try:
        # Extração
        df_planilha = carregar_planilha(config.INPUT_PATH)
        df_sql = carregar_sql()

        if df_planilha.empty:
            raise ValueError("Planilha vazia")

        if df_sql.empty:
            raise ValueError("Base SQL vazia")

        # Transformação
        df_planilha = tratar_dados(df_planilha)

        dias_para_corte = df_planilha['Aging Corte'].min()

        # Matching
        df_final, df_nao_localizados = executar_matching(df_planilha, df_sql)

        # Saída
        salvar(
            df_final=df_final,
            df_nao_localizados=df_nao_localizados,
            base_path=config.OUTPUT_PATH
        )

        # 👉 AQUI começa email

        dias_para_corte = df_planilha['Aging Corte'].astype(int).min()

        destinatarios = definir_destinatarios(dias_para_corte, config)

        if destinatarios:
            enviar_email(
                destinatarios=destinatarios,
                assunto="Resultado da conciliação",
                corpo="Processamento concluído",
                anexos=[
                    f"{config.OUTPUT_PATH}/corretos/preenchidos.xlsx",
                    f"{config.OUTPUT_PATH}/incorretos/nao_localizados.xlsx"
                ]
    )

    except Exception as e:
        print(f"Erro na execução: {e}")

        df_final = []
        df_nao_localizados = []
        status_execucao = "ERRO"

    # LOG (executa sempre)
    dados_log = {
        "id_execucao": id_execucao,
        "data_execucao": data_execucao,
        #"arquivo": str(config.INPUT_PATH),

        "qtd_total": len(df_planilha) if 'df_planilha' in locals() else 0,
        "qtd_corretos": len(df_final[df_final['status'] == 'OK']),
        "qtd_nao_localizados": len(df_nao_localizados[df_nao_localizados['status'] == 'NAO_LOCALIZADO']),

        "status_execucao": status_execucao,
        "email_enviado": "Não",
        "tipo_envio": "",
        "dias_para_corte": ""
    }

    registrar_execucao(config.LOG_PATH, dados_log)

if __name__ == "__main__":
    main()