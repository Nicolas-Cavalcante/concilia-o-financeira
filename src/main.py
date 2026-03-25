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
import argparse
from pathlib import Path

def main(input_path, input_path2, enviar_email_flag):

    load_dotenv()
    id_execucao = str(uuid4())
    data_execucao = datetime.now()
    status_execucao = "Sucesso"
    try:
        # Extração
        df_planilha = carregar_planilha(input_path)
        df_base_email = carregar_base_email(input_path2)
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
            path_corretos=config.OUTPUT_CORRETOS,
            path_incorretos=config.OUTPUT_INCORRETOS
        )

        # 👉 AQUI começa email

        dias_para_corte = df_planilha['Aging Corte'].astype(int).min()

        destinatarios = definir_destinatarios(dias_para_corte, df_base_email)

        if destinatarios and enviar_email_flag:
            enviar_email(
                email_origem=os.getenv("Email_User"),
                destinatarios=destinatarios,
                assunto="Casos não identificados - EBTA",
                corpo="""<p>Olá,

                    <p>Identificamos pendências em registros do seu atendimento.<p>

                    <p>É necessário verficar se a venda foi lançada, revisar e corrigir os campos sinalizados com asterisco (*) mencionados no arquivo e validar dentro do benner, pois essas informações não foram localizadas no sistema.<p>

                    <p>Caso os dados não sejam ajustados, os campos permanecerão sem informação na fatura do cliente.<p>

                    <p>Após a correção, as transações serão atualizadas em até 24 horas.<p>

                    <p>Solicitamos a regularização o quanto antes para evitar impactos para o cliente.<p>

                    <p>Atenciosamente,
                """,
                anexos=[
                    os.path.join(config.OUTPUT_PATH, "Incorretos", "Pendências_EBTA.xlsx")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)

    args = parser.parse_args()

    INPUT_PATH = Path(args.input1)
    INPUT_PATH2 = Path(args.input2)

    main(INPUT_PATH, INPUT_PATH2, True)  # ou False padrão