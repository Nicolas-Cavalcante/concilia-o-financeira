import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, Color


# ==================================================
# 📝 ESTE ARQUIVO É RESPONSÁVEL POR APLICAR TODA LÓGICA DE MATCHING ENTRE AS BASES, CRIAÇÃO DE STATUS E CRIAÇÃO
# DOS ARQUIVOS FINAIS.
# ==================================================


def executar_matching(df_planilha, df_sql, df_depara):

    # =========================
    # ⚙️ CRIA CHAVES VÁLIDAS REMOVENDO DUPLICADOS
    # =========================
    
    # Chave KEY 1 🗝️
    unicos_sql_k1 = df_sql['Chave Aut + Data + Valor'][~df_sql['Chave Aut + Data + Valor'].duplicated(keep=False)]
    unicos_plan_k1 = df_planilha['Chave Aut + Data + Valor'][~df_planilha['Chave Aut + Data + Valor'].duplicated(keep=False)]
    chaves_validas_k1 = set(unicos_sql_k1).intersection(set(unicos_plan_k1))

    # Chave KEY 2 🗝️
    unicos_sql_k2 = df_sql['Chave nr_aut + Data + Valor'][~df_sql['Chave nr_aut + Data + Valor'].duplicated(keep=False)]
    unicos_plan_k2 = df_planilha['Chave Aut + Data + Valor'][~df_planilha['Chave Aut + Data + Valor'].duplicated(keep=False)]
    chaves_validas_k2 = set(unicos_sql_k2).intersection(set(unicos_plan_k2))

    # Chave KEY 3 🗝️
    unicos_sql_k3 = df_sql['Chave Loc Cia + Data + Valor'][~df_sql['Chave Loc Cia + Data + Valor'].duplicated(keep=False)]
    unicos_plan_k3 = df_planilha['Chave Loc Cia + Data + Valor'][~df_planilha['Chave Loc Cia + Data + Valor'].duplicated(keep=False)]
    chaves_validas_k3 = set(unicos_sql_k3).intersection(set(unicos_plan_k3))

    # Chave KEY 4 🗝️
    #unicos_sql_k3 = df_sql['Chave Cartão + Data + Valor'][~df_sql['Chave Cartão + Data + Valor'].duplicated(keep=False)]
    #unicos_plan_k3 = df_planilha['Chave Cartão + Data + Valor'][~df_planilha['Chave Cartão + Data + Valor'].duplicated(keep=False)]
    #chaves_validas_k3 = set(unicos_sql_k3).intersection(set(unicos_plan_k3))

    # Chave KEY 4 🗝️
    unicos_sql_k4 = df_sql['Chave Cartão + Data + Valor + Loc Cia'][~df_sql['Chave Cartão + Data + Valor + Loc Cia'].duplicated(keep=False)]
    unicos_plan_k4 = df_planilha['Chave Cartão + Data + Valor + Loc Cia'][~df_planilha['Chave Cartão + Data + Valor + Loc Cia'].duplicated(keep=False)]
    chaves_validas_k4 = set(unicos_sql_k4).intersection(set(unicos_plan_k4))

    # Chave KEY 5 🗝️
    unicos_sql_k5 = df_sql['Chave Cartão + Valor + Loc Cia'][~df_sql['Chave Cartão + Valor + Loc Cia'].duplicated(keep=False)]
    unicos_plan_k5 = df_planilha['Chave Cartão + Valor + Loc Cia'][~df_planilha['Chave Cartão + Valor + Loc Cia'].duplicated(keep=False)]
    chaves_validas_k5 = set(unicos_sql_k5).intersection(set(unicos_plan_k5))

    # Chave KEY 7 🗝️
    #unicos_sql_k7 = df_sql['Chave Cartão + Valor'][~df_sql['Chave Cartão + Valor'].duplicated(keep=False)]
    #unicos_plan_k7 = df_planilha['Chave Cartão + Valor'][~df_planilha['Chave Cartão + Valor'].duplicated(keep=False)]
    #chaves_validas_k7 = set(unicos_sql_k7).intersection(set(unicos_plan_k7))

    # =========================
    # 📍CRIA MAPAS ARMAZENANDO AS CHAVES VALIDAS
    # =========================

    map_k1 = df_sql[df_sql['Chave Aut + Data + Valor'].isin(chaves_validas_k1)].set_index('Chave Aut + Data + Valor')
    map_k2 = df_sql[df_sql['Chave nr_aut + Data + Valor'].isin(chaves_validas_k2)].set_index('Chave nr_aut + Data + Valor')
    map_k3 = df_sql[df_sql['Chave Loc Cia + Data + Valor'].isin(chaves_validas_k3)].set_index('Chave Loc Cia + Data + Valor')
    map_k4 = df_sql[df_sql['Chave Cartão + Data + Valor + Loc Cia'].isin(chaves_validas_k4)].set_index('Chave Cartão + Data + Valor + Loc Cia')
    map_k5 = df_sql[df_sql['Chave Cartão + Valor + Loc Cia'].isin(chaves_validas_k5)].set_index('Chave Cartão + Valor + Loc Cia')
    #map_k7 = df_sql[df_sql['Chave Cartão + Valor'].isin(chaves_validas_k7)].set_index('Chave Cartão + Valor')

    # =========================
    # 📝 REGRAS, AS COLUNAS SERÃO O PARAMETRO DE PREENHCIMENTO, COLUNAS A ESQUERDA SÃO AS COLUNAS QUE VEM DE df_planilha,
    # após os dois pontos são os dados que serão buscados no df_sql
    # =========================

    regras_padrao = {
        'Ticket': 'Bilhete',
        'Passageiro': 'Nome do Passageiro',
        'Trecho Voado': 'Trecho',
        'Centro de Custo': 'cod_centro_custo',
        'Departamento': 'Departamento',
        'Matricula': 'Matricula',
        'Requisição': 'OS',
        'Solicitante': 'Nome do Solicitante',
        'Aprovador': 'Aprovador',
        'Localizador': 'Localizador',
        'Emissor': 'Emissor',
        'Classe': 'sgl_classe',
        'Data Ida': 'Data Ida',
        'Taxa de Embarque': 'vl_taxa_embarque'
    }


    regras_clientes = (
        df_depara
        .groupby('Cliente')
        .apply(lambda x: dict(zip(
            x['Campo Arquivo do cliente'], # Campo destino depara
            x['Nome do Campo']             # Campo origem depara
            )))          
        .to_dict()
    )

    
    def regras_finais(cliente, regras_padrao, regras_clientes):

        regras_finais = regras_padrao.copy()

        if 'DEFAULT' in regras_clientes:
            regras_finais.update(regras_clientes['DEFAULT'])

        if cliente in regras_clientes:
            regras_finais.update(regras_clientes[cliente])

        return regras_finais

    # =========================
    # NORMALIZAÇÃO EM COLUNAS COM ASTERISCO
    # PARA INICIAR O MATCH EVITANDO POSSÍVEIS INTERFERENCIAS
    # =========================

    colunas_validacao = list(regras_padrao.keys())

    mask_original_columns = df_planilha[colunas_validacao] == '**********'

    df_planilha[colunas_validacao] = (
        df_planilha[colunas_validacao]
        .replace('**********', '')
        .replace(r'^\s+$', '', regex=True)
        .fillna('')
    )

    chaves = [
        ('Chave Aut + Data + Valor', map_k1, chaves_validas_k1),
        ('Chave nr_aut + Data + Valor', map_k2, chaves_validas_k2),
        ('Chave Loc Cia + Data + Valor', map_k3, chaves_validas_k3),
        ('Chave Cartão + Data + Valor + Loc Cia', map_k4, chaves_validas_k4),
        ('Chave Cartão + Valor + Loc Cia', map_k5, chaves_validas_k5),
        #('Chave Cartão + Valor', map_k7, chaves_validas_k7),
    ]

    log_chaves = []

    # =========================
    # MATCH - FAZ LOOPING VALIDANDO ONDE HOUVE MATCH COM OS MAPAS E PREENCHE AS COLUNAS
    # =========================

    print(df_planilha.dtypes)
    df_planilha['teve_match'] = False
    df_planilha['chave_match'] = None

    for nome_chave, mapa, chaves_validas in chaves:

        # só tenta quem ainda não encontrou nada
        mask = df_planilha['teve_match'] == False
        idx = df_planilha.loc[mask].index

        for idx_linha in idx:

            mask_original_linha = mask_original_columns.loc[idx_linha]
            
            chave_valor = df_planilha.at[idx_linha, nome_chave]

            encontrou = chave_valor in chaves_validas

            if not encontrou:
                log_chaves.append({
                    'idx': idx_linha,
                    'chave': nome_chave,
                    'resultado': 'nao_encontrado'
                    })
                continue

            cliente = df_planilha.at[idx_linha, 'Nome da Empresa']
            regra_final = regras_finais(cliente, regras_padrao, regras_clientes)
            
            linha_temp = df_planilha.loc[idx_linha].copy()

            for col_dest, col_origem in regra_final.items():
                if col_origem in mapa.columns:
                    try:
                        linha_temp[col_dest] = mapa.at[chave_valor, col_origem]
                    except KeyError:
                        continue

            for col in regra_final.keys():
                if linha_temp[col] == '' and mask_original_linha[col]:
                    linha_temp[col] = '**********'

            tem_ausencia = any(
                linha_temp[col] == '**********'
                for col in regra_final.keys()
            )

            resultado = 'incompleto' if tem_ausencia else 'Ok'

            log_chaves.append({
                'idx': idx_linha,
                'chave': nome_chave,
                'resultado': resultado 
            })

        chaves_linha = df_planilha.loc[mask, nome_chave]

        idx_match = idx[chaves_linha.isin(chaves_validas)]

        # marca que essa linha encontrou sua chave definitiva
        df_planilha.loc[idx_match, 'teve_match'] = True
        df_planilha.loc[idx_match, 'chave_match'] = nome_chave

        # agora preenche TODAS as colunas de uma vez

        for idx_linha in idx_match:

            cliente = df_planilha.at[idx_linha, 'Nome da Empresa']

            regra_final = regras_finais(cliente, regras_padrao, regras_clientes)

            chave_valor = df_planilha.at[idx_linha, nome_chave]

            if chave_valor not in mapa.index:
                continue
            
            for col_dest, col_origem in regra_final.items():
            
                if col_origem not in mapa.columns:
                    continue
                
                df_planilha.at[idx_linha, col_dest] = mapa.at[chave_valor, col_origem]

    # =========================
    # CRIA STATUS PARA VALIDAR CASOS TRATADOS
    # =========================

    df_planilha['chave_match'] = df_planilha['chave_match'].fillna('não_match')

    colunas_validacao = list(regras_padrao.keys())

    df_planilha[colunas_validacao] = (df_planilha[colunas_validacao].replace(r'^\s+$', '', regex=True).fillna(''))
    
    df_planilha['status'] = 'Ok'

    # 1.Não encontrou nenhuma chave
    df_planilha.loc[df_planilha['teve_match'] == False, 'status'] = 'Não Localizado'

    # 3.Preenche com asterisco onde já existia
    df_planilha[colunas_validacao] = df_planilha[colunas_validacao].mask(
        (df_planilha[colunas_validacao] == '') & mask_original_columns,
        '**********'
    )

    mask_asterisco = (df_planilha[colunas_validacao] == '**********')
    tem_asterisco = mask_asterisco.any(axis=1)
    df_planilha.loc[
    (df_planilha['teve_match'] == True) & tem_asterisco,
    'status'
] = 'Colunas com ausência de dados'
    
    #df_planilha.loc[df_planilha['Nome da Cia Aérea'] == 'FLYTOUR CALL CENT', 'status'] = 'Ok'

    # =========================
    # CRIA DF NÃO LOCALIZADOS PARA ENCAMINHAR PARA OPERAÇÃO
    # =========================

    df_nao_localizados = df_planilha[df_planilha['status'].isin(['Não Localizado', 'Colunas com ausência de dados'])].copy()
    
    # =========================
    # RETORNA DATAFRAME FINAL PARA SUBIR NO SITE DO BRADESCO
    # =========================

    df_preenchido = df_planilha[df_planilha['status'] == 'Ok'].copy()
    
    return df_preenchido, df_nao_localizados, pd.DataFrame(log_chaves)