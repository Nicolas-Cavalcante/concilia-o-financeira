
#==============================================
# ⚙️ IMPORTAÇÃO DAS BASES
#==============================================

from src.extract.database import carregar_sql
from src.extract.pendencias import carregar_planilha
from src.extract.base_email import carregar_base_email
from src.transform.tratamento import tratar_dados
from src.matching.conciliacao import executar_matching
from src.export.salvar import salvar
from src.notify.analises_email import (
    compara_movimento,
    montar_corpo_email
)
from src.log.logger import registrar_execucao
from src.notify.regra_envio import definir_destinatarios
from src.notify.email import enviar_email

#==============================================
# ⚙️ IMPORTAÇÃO DAS BIBLIOTECAS
#==============================================

from src import config
from datetime import datetime
from uuid import uuid4
from src import config
from dotenv import load_dotenv
import pandas as pd
import os
import argparse
from pathlib import Path
import time



def main(input_path, input_path2, enviar_email_flag, atualizar_status=None):

    load_dotenv()
    nome_arquivo = Path(input_path).stem # nome do arquivo sem extensão
    id_execucao = nome_arquivo[-6:]
    data_execucao = datetime.now()
    status_execucao = "Sucesso"
    try:
        # Extração
        if atualizar_status:
            atualizar_status("Carregando base de pendências...", 10)
            time.sleep(1.7)
        df_planilha = carregar_planilha(input_path)

        if atualizar_status:
            atualizar_status("Carregando base de clientes...", 20)
        df_base_email = carregar_base_email(input_path2)

        if atualizar_status:
            atualizar_status("Conectando ao banco...", 35)
        df_sql = carregar_sql()

        atualizar_status("Base carregada. Iniciando processamento...", 55)

        if df_planilha.empty:
            raise ValueError("Planilha vazia")

        if df_sql.empty:
            raise ValueError("Base SQL vazia")

        if atualizar_status:
            atualizar_status("Trabalhando nas bases...", 65)
            time.sleep(2.5)
        df_planilha = tratar_dados(df_planilha)
        dias_para_corte = df_planilha['Aging Corte'].astype(int).min()

        atualizar_status("Executando conciliação...", 75)
        time.sleep(1.5)
        df_final, df_nao_localizados = executar_matching(df_planilha, df_sql)

        qtde_ok = (df_planilha['status'] == 'OK').sum()
        qtde_erro = (df_planilha['status'] == 'NAO_LOCALIZADO').sum()

        if atualizar_status:
            atualizar_status(f"{qtde_ok} Conciliados | {qtde_erro} não localizados", 85)
            time.sleep(1.0)


        # Saída
        salvar(
            df_final=df_final,
            df_nao_localizados=df_nao_localizados,
            df_sql=df_sql,
            path=config.OUTPUT_BASE,
            path_corretos=config.OUTPUT_CORRETOS,
            path_incorretos=config.OUTPUT_INCORRETOS
        )

        #==============================================
        # 📊 analytics
        #==============================================

        # 🔴 provisório (até você ter df_ontem)
        status_movimento = {
            "Novos": 0,
            "Resolvidos": 0,
            "Pioraram": 0,
            "Melhoraram": 0
        }

        corpo_email = montar_corpo_email(status_movimento)

        #==============================================
        # 📩 Chamada para E-mail
        #==============================================

        existem_urgentes = (df_nao_localizados['Aging Corte'] < 0).any() # Verifica casos urgentes

        cc = [] # Cria cópia no email vazia

        if existem_urgentes:
            cc = os.getenv("Email_Diretoria").split(";")

        dias_para_corte = df_planilha['Aging Corte'].astype(int).min()

        destinatarios = definir_destinatarios(dias_para_corte, df_base_email)

        if destinatarios and enviar_email_flag:
            if atualizar_status:
                atualizar_status("Encaminhando e-mail para operação 📩", 90)

            enviar_email(
                email_origem=os.getenv("Email_User"),
                destinatarios=destinatarios,
                cc=cc,
                assunto="Casos não identificados - EBTA",
                corpo=corpo_email,
                anexos=[
                    os.path.join(config.OUTPUT_INCORRETOS, "Pendências_EBTA.xlsx")
                ]
            )
            
        atualizar_status("Finalizando...", 95)
        time.sleep(1.5)
    

        atualizar_status("Finalizado", 100)
    #==============================================
    # 🛠️ Exceção de erros
    #==============================================
    except Exception as e:
        print(f"Erro na execução: {e}")
        status_execucao = "Erro"

        df_final = None
        df_nao_localizados = None

        raise e #Não permite que a informação apresentada no erro quebre
    
    #==============================================
    # 📌 Carrega LOG de Excução (executa sempre)
    #==============================================
    dados_log = {
        "id_execucao": id_execucao,
        "data_execucao": data_execucao,

        "qtd_total": len(df_planilha) if 'df_planilha' in locals() else 0,
        "qtd_corretos": len(df_final[df_final['status'] == 'OK']) if isinstance(df_final, pd.DataFrame) else 0,
        "qtd_nao_localizados": ( 
            len(df_nao_localizados[df_nao_localizados['status'] == 'NAO_LOCALIZADO'])
            if isinstance(df_nao_localizados, pd.DataFrame)
            else 0
        ),

        "status_execucao": status_execucao,
        "email_enviado": "Sim" if status_execucao == "Sucesso" else "Não",
    }

    registrar_execucao(config.LOG_PATH, dados_log)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)

    args = parser.parse_args()

    INPUT_PATH = Path(args.input1)
    INPUT_PATH2 = Path(args.input2)

    main(INPUT_PATH, INPUT_PATH2, True)