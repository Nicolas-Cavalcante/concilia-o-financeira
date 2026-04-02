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
    # MATCH
    # =========================

    df_planilha['match_encontrado'] = False

    for col_dest, col_origem in regras.items():

        # k1
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Aut + Data + Valor'].map(map_k1[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Aut + Data + Valor']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k1)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

        # k2
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Aut + Data + Cartão + Valor'].map(map_k2[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Aut + Data + Cartão + Valor']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k2)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

        # k3
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Loc Cia + Data + Valor'].map(map_k3[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Loc Cia + Data + Valor']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k3)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

        # k4
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Cartão + Data + Valor'].map(map_k4[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Cartão + Data + Valor']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k4)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

        # k5
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Cartão + Data + Valor + Loc Cia'].map(map_k5[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Cartão + Data + Valor + Loc Cia']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k5)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

        # k6
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Cartão + Valor + Loc Cia'].map(map_k6[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Cartão + Valor + Loc Cia']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k6)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'


    # =========================
    # CRIA STATUS PARA VALIDAR CASOS TRATADOS
    # =========================

    df_planilha['status'] = 'OK'

    df_planilha.loc[df_planilha['match_encontrado'] == False, 'status'] = 'NAO_LOCALIZADO'

    df_planilha.loc[
        (df_planilha['status'] == 'OK') &
        (df_planilha[list(regras.keys())] == 'NT').any(axis=1),
        'status'
    ] = 'NT'

    # =========================
    # CRIA DF NÃO LOCALIZADOS PARA ENCAMINHAR PARA OPERAÇÃO
    # =========================

    df_nao_localizados = df_planilha[df_planilha['status'] == 'NAO_LOCALIZADO'].copy()

    # ==============================================
    # 📊 REGRAS DE CLASSIFICAÇÃO DE ACORDO COM AGING CORTE
    # ==============================================

    def regras_status(aging):
        if aging < 0:
            return "Crítico"
        elif aging == 0:
            return "Urgente"
        elif aging <= 5:
            return "Alta"
        elif aging <= 10:
            return "Média"
        else:
            return "Baixa"

    df_nao_localizados['Status do Processo'] = df_nao_localizados['Aging Corte'].apply(regras_status)
    
    # =========================
    # EXCLUI COLUNAS INDESEJADAS DAS PLANILHAS FINAIS
    # =========================

    df_planilha.drop(columns=['match_encontrado'], inplace=True)
    df_nao_localizados.drop(columns=[
        'Chave Cartão', 
        'Chave Cartão + '
        'LOC CIA', 
        'Chave Cartão Sem data',
        'match_encontrado',
        'status'
        ])

    # =========================
    # RETORNA DATAFRAME FINAL
    # =========================

    df_preenchido = df_planilha.copy()

    return df_preenchido, df_nao_localizados