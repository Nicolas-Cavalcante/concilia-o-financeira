
#==============================================
# ⚙️ IMPORTAÇÃO DAS BASES
#==============================================

from src.extract.database import carregar_sql
from src.extract.pendencias import carregar_planilha
from src.extract.pendencias import df_depara
from src.extract.base_email import carregar_base_email
from src.transform.tratamento import tratar_dados
from src.matching.conciliacao import executar_matching
from src.export.salvar import salvar
from src.notify.analises_email import (
    montar_corpo_diretoria,
    montar_corpo_email
)
from src.log.logger import (
    registrar_execucao_chaves,
    registra_execucao_detalhada
)
from src.notify.regra_envio import definir_destinatarios
from src.notify.email import enviar_email
from src.outputs_configs.layout import (
    montar_layout_conciliados,
    montar_layout_nao_localizados
)

#==============================================
# ⚙️ IMPORTAÇÃO DAS BIBLIOTECAS
#==============================================

from src.config import EXEC_DIR
from datetime import datetime
from src import config
import pandas as pd
import os
import argparse
from pathlib import Path
import time



def main(input_path, input_path2, enviar_email_flag, atualizar_status, controle):

    nome_arquivo = Path(input_path).stem # nome do arquivo sem extensão
    id_execucao = nome_arquivo[-6:]
    data_execucao = datetime.now()
    status_execucao = "Sucesso"
    try:
        # Extração
        if atualizar_status:
            atualizar_status("Iniciando processo", 10)
        df_planilha = carregar_planilha(input_path)

        if controle["cancelar"]:
            return

        if atualizar_status:
            atualizar_status("Carregando base de clientes", 20)
        df_base_email = carregar_base_email(input_path2)

        if controle["cancelar"]:
            return

        if atualizar_status:
            atualizar_status("Carregando base interna", 35)
        df_sql = carregar_sql()

        if controle["cancelar"]:
            return

        atualizar_status("Bases carregadas. Iniciando processamento", 55)
        time.sleep(2.5)

        if df_planilha.empty:
            raise ValueError("Planilha vazia")

        if df_sql.empty:
            raise ValueError("Base SQL vazia")

        if atualizar_status:
            atualizar_status("Iniciando processo de conciliação", 65)
            time.sleep(2.5)
        df_planilha = tratar_dados(df_planilha)

        if controle["cancelar"]:
            return

        atualizar_status("Executando conciliação", 75)
        time.sleep(1.5)
        df_conciliados_preenchido, df_nao_localizados, df_log_chaves = executar_matching(df_planilha, df_sql, df_depara)
        dias_para_corte = df_nao_localizados['Dias Restantes'].min()

        df_conciliados = montar_layout_conciliados(df_conciliados_preenchido)
        df_nao_conciliado = montar_layout_nao_localizados(df_nao_localizados)

        if controle["cancelar"]:
            return

        qtde_ok = (df_planilha['status'] == 'Ok').sum()
        qtde_erro = (df_planilha['status'] == 'Não Localizado').sum()
        qtde_ausente_de_dados = (df_planilha['status'] == 'Colunas com ausência de dados').sum()
        
        qtde_total = (
            qtde_ok +
            qtde_erro +
            qtde_ausente_de_dados
        )
        if qtde_total > 0:

            percentual_ok = round((qtde_ok / qtde_total) * 100, 2)

        percentual_pendente = round(((
            qtde_erro +
            qtde_ausente_de_dados
        ) / qtde_total) * 100, 2)
        if controle["cancelar"]:
            return

        atualizar_status("Salvando arquivos nas pastas", 90)
        # Saída
        salvar(
            df_final=df_conciliados,
            df_nao_localizados=df_nao_conciliado,
            df_sql=df_sql,
            df_planilha=df_planilha,
            path=config.OUTPUT_BASE,
            path_corretos=config.OUTPUT_CORRETOS,
            path_incorretos=config.OUTPUT_INCORRETOS
        )

        # =========================
        # CRIA TABELA PARA ENCAMINHAR NO CORPO DO EMAIL
        # =========================

        html_tabela = "<p>Sem pendências no momento.</p>"
        if not df_nao_localizados.empty:
            tabela_clientes = (
                df_nao_localizados
                .groupby('Nome da Empresa')
                .size()
                .reset_index(name='Qtde Pendente')
                .sort_values(by='Qtde Pendente', ascending=False)
                .head(10)
            )

            tabela_clientes.index.name=None

            html_tabela = tabela_clientes.to_html(
                index=False,
                border=0,
                justify='center'
                ).replace(
                '<table',
                '<table style="border-collapse:collapse;font-family:Calibri;font-size:11pt;"'
                ).replace(
                    '<th',
                    '<th style="border:1px solid #ccc;padding:5px;background-color:#f2f2f2;"'
                ).replace(
                    '<td',
                    '<td style="border:1px solid #ccc;padding:5px;text-align:center;"'
                )
            corpo_email = montar_corpo_email(html_tabela)

        #==============================================
        # 📩 Chamada para E-mail
        #==============================================

        existem_urgentes = (df_nao_localizados['Dias Restantes'] < 5).any() # Verifica casos urgentes

        operacao = definir_destinatarios(dias_para_corte, df_base_email)
        diretoria = os.getenv("Email_Diretoria").split(";")

        #  1. ENVIO OPERAÇÃO
        if enviar_email_flag:
            if atualizar_status:
                atualizar_status("Encaminhando e-mail para operação 📩", 93)

            enviar_email(
                email_origem=os.getenv("Email_User"),
                destinatarios=operacao,
                assunto="Casos não identificados - EBTA",
                corpo=corpo_email,
                anexos=[
                    os.path.join(config.OUTPUT_INCORRETOS, "Pendências_EBTA.xlsx")
                ]
            )
            
            #  2. ENVIO DIRETORIA
            if existem_urgentes:

                qtde_casos = (df_nao_localizados["Dias Restantes"] <= 5).sum()
                dias_min = df_nao_localizados['Dias Restantes'].min()
                corpo_diretoria = montar_corpo_diretoria(qtde_casos, dias_min)

                enviar_email(
                    email_origem=os.getenv("Email_User"),
                    destinatarios=diretoria,
                    assunto="⚠️ Pendências próximas ao fechamento",
                    corpo=corpo_diretoria,
                    anexos=None
                )

            atualizar_status("Finalizando", 95)
            time.sleep(1.5)
        

            atualizar_status("", 100)
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
    # 📌 Carrega LOG de Excução detalhado com chave unica
    #==============================================
    df_log = df_planilha.copy()
    
    df_log = (
        df_planilha
        .groupby('Nome da Empresa')['status']
        .value_counts()
        .unstack(fill_value=0)
    )

    # Garante todas as colunas
    for col in ['Ok', 'Não Localizado', 'Colunas com ausência de dados']:
        if col not in df_log.columns:
            df_log[col] = 0

    # Agora sim renomeia
    df_log = df_log.rename(columns={
        'Ok': 'corretos',
        'Não Localizado': 'incorretos',
        'Colunas com ausência de dados': 'ausencia_de_dados'
    }).reset_index()
    
    df_log['data_execucao'] = data_execucao
    df_log['celula'] = df_log['Nome da Empresa']
    df_log['status_email'] = "Sim" if status_execucao == "Sucesso" else "Não"
    
    df_log = df_log [
        [
            "data_execucao",
            "celula",
            "Nome da Empresa",
            "incorretos",
            "corretos",
            "ausencia_de_dados",
            "status_email"
        ]
    ]

    #==============================================
    # 📌 Carrega log de execução
    #==============================================
    
    # 1. Agrupando para saber a assertividade por chave
    # Supondo que 'chave_utilizada' seja o nome da regra (ex: 'Match por CNPJ')
    # e 'status' seja 'Ok' ou 'Não Localizado'

    df_log_chaves = (
        df_log_chaves
        .groupby(['chave', 'resultado'])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for col in ['Ok', 'nao_encontrado', 'incompleto']:
        if col not in df_log_chaves:
            df_log_chaves[col] = 0
    df_log_chaves['data_execucao'] = data_execucao

    df_log_chaves = df_log_chaves.rename(columns={
        'incompleto': 'ausencia_de_dados',
        'Ok': 'qtd_encontrada',
        'nao_encontrado': 'qtd_nao_encontrada'
    })

    registra_execucao_detalhada(config.LOG_DETALHE_PATH, df_log)

    registrar_execucao_chaves(config.LOG_PATH, df_log_chaves)
    
    return percentual_ok, percentual_pendente

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)

    args = parser.parse_args()

    INPUT_PATH = Path(args.input1)
    INPUT_PATH2 = Path(args.input2)

    main(INPUT_PATH, INPUT_PATH2, True, None, {"cancelar": False})