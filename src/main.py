
#==============================================
# ⚙️ IMPORTAÇÃO DAS BASES
#==============================================

from src.extract.database import carregar_sql
from src.extract.pendencias import carregar_planilha
from src.extract.pendencias import df_depara
from src.extract.base_email import carregar_base_email
from src.transform.tratamento import tratar_dados
from src.matching.conciliacao import executar_matching
from src.export.salvar import (salvar, aplicar_estilo_visual)
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
    montar_layout_nao_localizados,
    montar_layout_gestor
)
from src.erros import SmartCheckError, classificar_erro
import traceback

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
    data_execucao = pd.Timestamp.today().normalize()
    status_execucao = "Sucesso"
    usuario_execucao = os.getenv("USERNAME")
    arquivo_pendencias_email = None
    try:
        # Extração
        if atualizar_status:
            atualizar_status(
                "Iniciando processo",
                10,
                etapa=0,
                log=("K1", "Arquivo de pendências carregado")
                )
        df_planilha = carregar_planilha(input_path)
        time.sleep(2.5)
        # Valida se é o arquivo correto
        colunas_esperadas_pendencias = ['Autorização', 'Valor Total', 'Nome da Empresa', 'Cartão']
        colunas_faltando = [c for c in colunas_esperadas_pendencias if c not in df_planilha.columns]
        if colunas_faltando:
            raise SmartCheckError(
                mensagem_usuario=f"Arquivo de pendências inválido. Verifique se selecionou o arquivo correto.\nColunas não encontradas: {', '.join(colunas_faltando)}",
                tipo="usuario",
            )

        total_registros = len(df_planilha)
      

        if atualizar_status:
            atualizar_status(
               "Pendências carregadas",
                15,
                etapa=0,
                registros=total_registros,
                log=("K1", f"{total_registros} registros lidos")
            )
     
        if controle["cancelar"]:
            return

        if atualizar_status:
            atualizar_status(
                "Carregando base de clientes",
                20,
                etapa=1,
                registros=total_registros,
                log=("K2", "Base de e-mails carregada")
            )

        df_base_email = carregar_base_email(input_path2)
        time.sleep(2.5)

        # Valida base de e-mails
        colunas_esperadas_email = ['SQUADS']
        colunas_faltando = [c for c in colunas_esperadas_email if c not in df_base_email.columns]
        if colunas_faltando:
            raise SmartCheckError(
                mensagem_usuario="Arquivo de e-mails inválido. Verifique se selecionou o arquivo correto.",
                tipo="usuario",
            )

        if controle["cancelar"]:
            return

        if atualizar_status:
            atualizar_status(
                "Carregando base interna",
                35,
                etapa=2,
                registros=total_registros,
                log=("K3", "Consulta SQL concluída")
            )
            
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
            atualizar_status(
                "Iniciando processo de conciliação",
                65,
                etapa=3,
                registros=total_registros,
                log=("K4", "Tratando dados")
            )

        df_planilha = tratar_dados(df_planilha, df_base_email)

        if controle["cancelar"]:
            return

        # Matching
        if atualizar_status:
            atualizar_status(
                "Executando conciliação",
                75,
                etapa=3,
                registros=total_registros,
                log=("K4", "Executando regras de matching")
            )

        df_conciliados_preenchido, df_nao_localizados, df_log_chaves = executar_matching(
            df_planilha,
            df_sql,
            df_depara
        )

        # Cria não localizados email respeitando os dias que devem entrar para operação
        df_nao_localizados_email = df_nao_localizados[
             df_nao_localizados['Dias Restantes'] <= 15
             ].copy()

        # cria variavel dias_para_corte para considerar na próximas aplicações
        dias_para_corte = df_nao_localizados_email['Dias Restantes'].min() \
            if not df_nao_localizados_email.empty else None
        
        df_conciliados = montar_layout_conciliados(df_conciliados_preenchido)
        df_nao_conciliado = montar_layout_nao_localizados(df_nao_localizados)
        df_nao_conciliado_email = montar_layout_nao_localizados(df_nao_localizados_email)

        if controle["cancelar"]:
            return
        
        # Cálculo dinâmico
        qtde_ok = (df_planilha['status'] == 'Ok').sum()
        qtde_erro = (df_planilha['status'] == 'Não Localizado').sum()
        qtde_ausente_de_dados = (
            df_planilha['status'] == 'Colunas com ausência de dados'
        ).sum()

        qtde_total = qtde_ok + qtde_erro + qtde_ausente_de_dados

        if qtde_total > 0:
            percentual_ok = round((qtde_ok / qtde_total) * 100, 2)
            percentual_pendente = round(
                ((qtde_erro + qtde_ausente_de_dados) / qtde_total) * 100,
                2
            )
        else:
            percentual_ok = 0
            percentual_pendente = 0
        
        # Atualiza cards com valores reais
        if atualizar_status:
            atualizar_status(
                "Conciliação concluída",
                85,
                etapa=3,
                registros=qtde_total,
                ok=qtde_ok,
                pendentes=qtde_erro + qtde_ausente_de_dados,
                log=("K4", f"{qtde_ok} conciliados e {qtde_erro + qtde_ausente_de_dados} pendentes")
            )

        # Exportação
        if atualizar_status:
            atualizar_status(
                "Salvando arquivos nas pastas",
                90,
                etapa=4,
                registros=qtde_total,
                ok=qtde_ok,
                pendentes=qtde_erro + qtde_ausente_de_dados,
                log=("K5", "Arquivos exportados com sucesso")
            )
            
        # Saída
        arquivo_pendencias_email = config.OUTPUT_INCORRETOS / "Pendências_email.xlsx"

        salvar(
            df_final=df_conciliados,
            df_nao_localizados=df_nao_conciliado,
            df_sql=df_sql,
            df_planilha=df_planilha,
            df_nao_localizados_email=df_nao_conciliado_email,
            path=config.OUTPUT_BASE,
            path_corretos=config.OUTPUT_CORRETOS,
            path_incorretos=config.OUTPUT_INCORRETOS
        )

        # =========================
        # ENVIO POR SQUAD (OPERAÇÃO)
        # =========================

        existem_urgentes = (df_nao_localizados_email['Dias Restantes'] <= -2).any()
        nao_urgente = (df_nao_localizados_email['Dias Restantes'] >= 0).any()
        gerente_rm = os.getenv("Email_Gerente_RM", "")
        diretoria = os.getenv("Email_Diretoria").split(";")
 
        if enviar_email_flag and not df_nao_localizados_email.empty:
 
            squads_sem_email = 0
            comps_do_dia = df_nao_localizados_email['Nº Cliente/COMP'].unique()
            base_do_dia = df_base_email[df_base_email['Nº Cliente/COMP'].isin(comps_do_dia)]
 
            for squads_email in base_do_dia['EMAIL_CELULA_TESTE'].dropna().unique():
 
                if str(squads_email).strip().lower() in ("nan", "none", ""):
                    squads_sem_email += 1
                    continue
 
                comps_squads = base_do_dia[
                    base_do_dia['EMAIL_CELULA_TESTE'] == squads_email
                ]['Nº Cliente/COMP'].unique()
 
                df_squad = df_nao_localizados_email[
                    df_nao_localizados_email['Nº Cliente/COMP'].isin(comps_squads)
                ]
 
                if df_squad.empty:
                    continue
 
                registro_base = base_do_dia[
                    base_do_dia['EMAIL_CELULA_TESTE'] == squads_email
                ].iloc[0]
 
                to_email = [str(squads_email).strip()]
 
                cc_emails = [
                    registro_base.get('SUPERVISOR_TESTE'),
                    registro_base.get('COORDENADOR_TESTE'),
                    registro_base.get('GERENTE_TESTE'),
                ]
                cc_emails = [
                    str(e).strip() for e in cc_emails
                    if pd.notna(e) and str(e).strip().lower() not in ("nan", "none", "")
                ]
 
                tabela_comp = (
                    df_squad
                    .groupby('Nome da Empresa')
                    .agg(
                        Qtde_Pendente=('Nome da Empresa', 'size'),
                        Data_fechamento=('Data Fechamento Cartão', 'first'),
                    )
                    .reset_index()
                    .sort_values(by='Qtde_Pendente', ascending=False)
                    .rename(columns={
                        'Qtde_Pendente':   'Qtde Pendente',
                        'Data_fechamento': 'Data de Fechamento',
                    })
                )
                tabela_comp.index.name = None
 
                html_tabela = tabela_comp.to_html(
                    index=False, border=0, justify='center'
                ).replace(
                    '<table', '<table style="border-collapse:collapse;font-family:Calibri;font-size:11pt;"'
                ).replace(
                    '<th', '<th style="border:1px solid #ccc;padding:5px;background-color:#f2f2f2;"'
                ).replace(
                    '<td', '<td style="border:1px solid #ccc;padding:5px;text-align:center;"'
                )
 
                corpo_email = montar_corpo_email(html_tabela)
                squad_id = str(squads_email).split("@")[0]
                df_anexo = montar_layout_nao_localizados(df_squad)
                arquivo_comp = config.OUTPUT_INCORRETOS / f"Pendencias_{squad_id}.xlsx"
                df_anexo.to_excel(arquivo_comp, index=False)
                aplicar_estilo_visual([arquivo_comp]) # Aplica estilo no arquivo anexado no email

                try:
                    enviar_email(
                        email_origem=os.getenv("Email_User"),
                        destinatarios=to_email,
                        cc=cc_emails if cc_emails else None,
                        assunto=f"Casos não identificados EBTA - {registro_base.get('SQUADS', '')}",
                        corpo=corpo_email,
                        anexos=[str(arquivo_comp)],
                    )
                finally:
                    try:
                        arquivo_comp.unlink()
                    except OSError:
                        pass
            
            if squads_sem_email > 0:
                print(f"[AVISO] {squads_sem_email} squad(s) ignoradas por ausência de e-mail na base.")

        # =========================
        # ENVIO GESTÃO
        # =========================
 
        if enviar_email_flag and not df_nao_localizados_email.empty:
 
            gestores_sem_email = 0
            comps_do_dia = df_nao_localizados_email['Nº Cliente/COMP'].unique()
            base_do_dia = df_base_email[df_base_email['Nº Cliente/COMP'].isin(comps_do_dia)]
 
            for gestor_email in base_do_dia['GERENTE_TESTE'].dropna().unique():
 
                if str(gestor_email).strip().lower() in ("nan", "none", ""):
                    gestores_sem_email += 1
                    continue
 
                comps_gestor = base_do_dia[
                    base_do_dia['GERENTE_TESTE'] == gestor_email
                ]['Nº Cliente/COMP'].unique()
 
                df_gestor = df_nao_localizados_email[
                    df_nao_localizados_email['Nº Cliente/COMP'].isin(comps_gestor)
                ]
 
                if df_gestor.empty:
                    continue
 
                registro_gestor = base_do_dia[base_do_dia['GERENTE_TESTE'] == gestor_email]
                cc_gestor = []
                for _, row in registro_gestor.iterrows():
                    for campo in ['SUPERVISOR_TESTE', 'COORDENADOR_TESTE']:
                        val = row.get(campo)
                        if pd.notna(val) and str(val).strip().lower() not in ("nan", "none", ""):
                            cc_gestor.append(str(val).strip())
                cc_gestor = list(set(cc_gestor))
 
                tabela_gestor = (
                    df_gestor
                    .groupby('SQUADS')
                    .agg(
                        Qtde_Pendente=('Nome da Empresa', 'size')
                    )
                    .reset_index()
                    .sort_values(by='Qtde_Pendente', ascending=False)
                    .rename(columns={
                        'Qtde_Pendente':   'Qtde Pendente',
                    })
                )
                tabela_gestor.index.name = None
 
                html_tabela = tabela_gestor.to_html(
                    index=False, border=0, justify='center'
                ).replace(
                    '<table', '<table style="border-collapse:collapse;font-family:Calibri;font-size:11pt;"'
                ).replace(
                    '<th', '<th style="border:1px solid #ccc;padding:5px;background-color:#f2f2f2;"'
                ).replace(
                    '<td', '<td style="border:1px solid #ccc;padding:5px;text-align:center;"'
                )
 
                corpo_email = montar_corpo_email(html_tabela)
                gestor_id = str(gestor_email).split("@")[0]
                arquivo_gestor = config.OUTPUT_INCORRETOS / f"Pendencias_Gestor_{gestor_id}.xlsx"
                df_anexo_gestor = montar_layout_gestor(df_gestor)
                df_anexo_gestor.to_excel(arquivo_gestor, index=False)
                aplicar_estilo_visual([arquivo_gestor]) # Aplica estilo no arquivo anexado no email
 
                try:
                    enviar_email(
                        email_origem=os.getenv("Email_User"),
                        destinatarios=[str(gestor_email).strip()],
                        cc=cc_gestor if cc_gestor else None,
                        assunto="Casos não identificados EBTA gestor",
                        corpo=corpo_email,
                        anexos=[str(arquivo_gestor)],
                    )
                finally:
                    try:
                        arquivo_gestor.unlink()
                    except OSError:
                        pass
 
            if gestores_sem_email > 0:
                print(f"[AVISO] {gestores_sem_email} gestor(es) ignorados por ausência de e-mail na base.")

        # ENVIO DIRETORIA
        if enviar_email_flag and existem_urgentes:

            qtde_casos = (df_nao_localizados['Dias Restantes'] <= -3).sum()
            dias_min = df_nao_localizados['Dias Restantes'].min()
            corpo_diretoria = montar_corpo_diretoria(qtde_casos, dias_min)

            destinatarios_diretoria = diretoria.copy()
            if gerente_rm:
                destinatarios_diretoria.append(gerente_rm)

            enviar_email(
                email_origem=os.getenv("Email_User"),
                destinatarios=destinatarios_diretoria,
                assunto="⚠️ Pendências próximas ao fechamento",
                corpo=corpo_diretoria,
                anexos=None
            )
        
            # Finalização
        if atualizar_status:
            atualizar_status(
                "Finalizando",
                100,
                etapa=4,
                registros=qtde_total,
                ok=qtde_ok,
                pendentes=qtde_erro + qtde_ausente_de_dados,
                log=("K5", "Processamento concluído")
            )
    #==============================================
    # 🛠️ Exceção de erros
    #==============================================
    #==============================================
    # 🛠️ Exceção de erros
    # Classifica o erro e relança como SmartCheckError
    # para que a interface exiba a mensagem correta.
    #==============================================
    except SmartCheckError:
        # Já classificado — apenas relança
        status_execucao = "Erro"
        raise

    except Exception as e:
        status_execucao = "Erro"

        info = classificar_erro(e)

        # Log técnico no terminal
        print(f"\n{'='*60}")
        print(f"[{info['tipo'].upper()}] {info['detalhe']}")
        print(traceback.format_exc())
        print(f"{'='*60}\n")

        # Relança como SmartCheckError com mensagem amigável
        raise SmartCheckError(
            mensagem_usuario=info["mensagem"],
            tipo=info["tipo"],
            detalhe=info["detalhe"],
        ) from e

    finally:
        if arquivo_pendencias_email and arquivo_pendencias_email.exists():
            try:
                arquivo_pendencias_email.unlink()
            except OSError as e:
                print(f"Não foi possível excluir o arquivo temporário do e-mail: {e}")
    
    #==============================================
    # 📌 Carrega LOG de Excução detalhado com chave unica
    #==============================================
    df_log = df_planilha.copy()
    
    df_log = (
        df_planilha
        .groupby('SQUADS')['status']
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
    df_log['celula'] = df_log['SQUADS']
    df_log['Nome da Empresa'] = df_planilha['Nome da Empresa']
    df_log['status_email'] = "Sim" if status_execucao == "Sucesso" else "Não"
    df_log['usuario'] = usuario_execucao
    
    df_log = df_log [
        [
            "data_execucao",
            "celula",
            "Nome da Empresa",
            "incorretos",
            "corretos",
            "ausencia_de_dados",
            "status_email",
            "usuario"
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
