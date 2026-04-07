import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, Color
from openpyxl.utils import get_column_letter

def executar_matching(df_planilha, df_sql):

    # =========================
    # CHAVES VÁLIDAS
    # =========================
    
    # Chave K1
    unicos_sql_k1 = df_sql['Chave Aut + Data + Valor'][~df_sql['Chave Aut + Data + Valor'].duplicated(keep=False)]
    unicos_plan_k1 = df_planilha['Chave Aut + Data + Valor'][~df_planilha['Chave Aut + Data + Valor'].duplicated(keep=False)]
    chaves_validas_k1 = set(unicos_sql_k1).intersection(set(unicos_plan_k1))

    # Chave K2
    unicos_sql_k2 = df_sql['Chave Aut + Cartão + Data + Valor'][~df_sql['Chave Aut + Cartão + Data + Valor'].duplicated(keep=False)]
    unicos_plan_k2 = df_planilha['Chave Aut + Cartão + Data + Valor'][~df_planilha['Chave Aut + Cartão + Data + Valor'].duplicated(keep=False)]
    chaves_validas_k2 = set(unicos_sql_k2).intersection(set(unicos_plan_k2))

    # Chave K3
    unicos_sql_k3 = df_sql['Chave Loc Cia + Data + Valor'][~df_sql['Chave Loc Cia + Data + Valor'].duplicated(keep=False)]
    unicos_plan_k3 = df_planilha['Chave Loc Cia + Data + Valor'][~df_planilha['Chave Loc Cia + Data + Valor'].duplicated(keep=False)]
    chaves_validas_k3 = set(unicos_sql_k3).intersection(set(unicos_plan_k3))

    # Chave K4
    unicos_sql_k4 = df_sql['Chave Cartão + Data + Valor'][~df_sql['Chave Cartão + Data + Valor'].duplicated(keep=False)]
    unicos_plan_k4 = df_planilha['Chave Cartão + Data + Valor'][~df_planilha['Chave Cartão + Data + Valor'].duplicated(keep=False)]
    chaves_validas_k4 = set(unicos_sql_k4).intersection(set(unicos_plan_k4))

    # Chave K5
    unicos_sql_k5 = df_sql['Chave Cartão + Data + Valor + Loc Cia'][~df_sql['Chave Cartão + Data + Valor + Loc Cia'].duplicated(keep=False)]
    unicos_plan_k5 = df_planilha['Chave Cartão + Data + Valor + Loc Cia'][~df_planilha['Chave Cartão + Data + Valor + Loc Cia'].duplicated(keep=False)]
    chaves_validas_k5 = set(unicos_sql_k5).intersection(set(unicos_plan_k5))

    # Chave K6
    unicos_sql_k6 = df_sql['Chave Cartão + Valor + Loc Cia'][~df_sql['Chave Cartão + Valor + Loc Cia'].duplicated(keep=False)]
    unicos_plan_k6 = df_planilha['Chave Cartão + Valor + Loc Cia'][~df_planilha['Chave Cartão + Valor + Loc Cia'].duplicated(keep=False)]
    chaves_validas_k6 = set(unicos_sql_k6).intersection(set(unicos_plan_k6))

    # =========================
    # MAPAS
    # =========================

    map_k1 = df_sql[df_sql['Chave Aut + Data + Valor'].isin(chaves_validas_k1)].set_index('Chave Aut + Data + Valor')
    map_k2 = df_sql[df_sql['Chave Aut + Cartão + Data + Valor'].isin(chaves_validas_k2)].set_index('Chave Aut + Cartão + Data + Valor')
    map_k3 = df_sql[df_sql['Chave Loc Cia + Data + Valor'].isin(chaves_validas_k3)].set_index('Chave Loc Cia + Data + Valor')
    map_k4 = df_sql[df_sql['Chave Cartão + Data + Valor'].isin(chaves_validas_k4)].set_index('Chave Cartão + Data + Valor')
    map_k5 = df_sql[df_sql['Chave Cartão + Data + Valor + Loc Cia'].isin(chaves_validas_k5)].set_index('Chave Cartão + Data + Valor + Loc Cia')
    map_k6 = df_sql[df_sql['Chave Cartão + Valor + Loc Cia'].isin(chaves_validas_k6)].set_index('Chave Cartão + Valor + Loc Cia')
    
    # =========================
    # REGRAS
    # =========================

    regras = {
        'Ticket': 'Bilhete',
        'Passageiro': 'Nome do Passageiro',
        'Trecho Voado': 'Trecho',
        'Centro de Custo': 'Centro de Custo',
        'Departamento': 'Departamento',
        'Matricula': 'Matricula',
        'Requisição': 'OS',
        'Solicitante': 'Nome do Solicitante',
        'Aprovador': 'Aprovador',
        'Localizador': 'Localizador'
    }

    # =========================
    # NORMALIZAÇÃO
    # =========================

    colunas_validacao = list(regras.keys())

    df_planilha[colunas_validacao] = (
        df_planilha[colunas_validacao]
        .replace('**********', '')
        .replace(r'^\s+$', '', regex=True)
        .fillna('')
    )

    chaves = [
        ('Chave Aut + Data + Valor', map_k1, chaves_validas_k1),
        ('Chave Aut + Cartão + Data + Valor', map_k2, chaves_validas_k2),
        ('Chave Loc Cia + Data + Valor', map_k3, chaves_validas_k3),
        ('Chave Cartão + Data + Valor', map_k4, chaves_validas_k4),
        ('Chave Cartão + Data + Valor + Loc Cia', map_k5, chaves_validas_k5),
        ('Chave Cartão + Valor + Loc Cia', map_k6, chaves_validas_k6),
    ]

    # =========================
    # MATCH
    # =========================

    df_planilha['teve_match'] = False

    for nome_chave, mapa, chaves_validas in chaves:

        # só tenta quem ainda não encontrou nada
        mask = df_planilha['teve_match'] == False

        idx = df_planilha.loc[mask].index
        chaves_linha = df_planilha.loc[mask, nome_chave]

        idx_match = idx[chaves_linha.isin(chaves_validas)]

        if len(idx_match) == 0:
            continue

        # marca que essa linha encontrou sua chave definitiva
        df_planilha.loc[idx_match, 'teve_match'] = True

        # agora preenche TODAS as colunas de uma vez
        for col_dest, col_origem in regras.items():

            valores = df_planilha.loc[idx_match, nome_chave].map(mapa[col_origem])

            idx_valido = idx_match[valores.notna()]

            df_planilha.loc[idx_valido, col_dest] = valores.loc[idx_valido]


    # =========================
    # CRIA STATUS PARA VALIDAR CASOS TRATADOS
    # =========================

    colunas_validacao = list(regras.keys())

    df_planilha[colunas_validacao] = df_planilha[colunas_validacao].replace('**********', '').fillna('')

    tem_vazio = (df_planilha[colunas_validacao] == '').any(axis=1)
    tudo_vazio = (df_planilha[colunas_validacao] == '').all(axis=1)

    df_planilha['status'] = 'Ok'

    # 1.Não encontrou nenhuma chave
    df_planilha.loc[df_planilha['teve_match'] == False, 'status'] = 'Não Localizado'

    # 2.Encontrou a chave, mas ficou com coluna incompleta
    df_planilha.loc[
        (df_planilha['teve_match'] == True) & tem_vazio,
        'status'
    ] = 'Colunas com ausência de dados'

    df_planilha[colunas_validacao] = df_planilha[colunas_validacao].replace('', '**********')
    # =========================
    # EXCLUI COLUNAS INDESEJADAS DAS PLANILHAS FINAIS
    # =========================

    df_planilha.drop(columns=[
        #'match_encontrado',
        #'RLOC_CIA_TRATADO',
        #'RLOC_CIA_CORRETO',
        #'Chave Aut + Data + Valor',
        #'Chave Aut + Cartão + Data + Valor',
        #'Chave Loc Cia + Data + Valor',
        #'Chave Cartão + Data + Valor + Loc Cia',
        #'Chave Cartão + Valor + Loc Cia',
        #'status'
        ], inplace=True)

    # =========================
    # CRIA DF NÃO LOCALIZADOS PARA ENCAMINHAR PARA OPERAÇÃO
    # =========================

    df_nao_localizados = df_planilha[df_planilha['status'].isin(['Não Localizado', 'Colunas com ausência de dados'])].copy()

    # =========================
    # RETORNA DATAFRAME FINAL
    # =========================

    df_preenchido = df_planilha[df_planilha['status'] == 'Ok'].copy()

    return df_preenchido, df_nao_localizados