from src.extract.database import carregar_sql
from src.extract.pendencias import carregar_planilha
from src.extract.base_email import carregar_base_email
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
from dotenv import load_dotenv
import pandas as pd
import os

def main():

    load_dotenv()
    id_execucao = str(uuid4())
    data_execucao = datetime.now()
    status_execucao = "Sucesso"
    try:
        # Extração
        df_planilha = carregar_planilha(config.INPUT_PATH)
        df_base_email = carregar_base_email(config.INPUT_PATH2)
        df_sql = carregar_sql()

        if df_planilha.empty:
            raise ValueError("Planilha vazia")

        if df_sql.empty:
            raise ValueError("Base SQL vazia")

        # Transformação
        df_planilha = tratar_dados(df_planilha)

        dias_para_corte = df_planilha['Aging Corte'].astype(int).min()

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

        destinatarios = definir_destinatarios(dias_para_corte, df_base_email)

        if destinatarios:
            enviar_email(
                email_origem=os.getenv("Email_User"),
                destinatarios=destinatarios,
                assunto="Casos incorretos Conciliação",
                corpo="""Bom dia, 
                
                Seguem casos incorretos

                Atenciosamente,
                """,
                anexos=[
                    os.path.join(config.OUTPUT_PATH, "Incorretos", "nao_localizados.xlsx")
                ]
    )

    except Exception as e:
        print(f"Erro na execução: {e}")
        status_execucao = "Erro"

        df_final = None
        df_nao_localizados = None

    # LOG (executa sempre)
    dados_log = {
        "id_execucao": id_execucao,
        "data_execucao": data_execucao,
        #"arquivo": str(config.INPUT_PATH),

        "qtd_total": len(df_planilha) if 'df_planilha' in locals() else 0,
        "qtd_corretos": len(df_final[df_final['status'] == 'OK']) if isinstance(df_final, pd.DataFrame) else 0,
        "qtd_nao_localizados": len(df_nao_localizados[df_nao_localizados['status'] == 'NAO_LOCALIZADO']),

        "status_execucao": status_execucao,
        "email_enviado": "Sim" if status_execucao == "Sucesso" else "Não",
        "tipo_envio": "",
        "dias_para_corte": dias_para_corte if 'Dias para corte' in locals() else 0
    }

    registrar_execucao(config.LOG_PATH, dados_log)

if __name__ == "__main__":
    main()