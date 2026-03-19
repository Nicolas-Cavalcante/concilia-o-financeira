import pandas as pd

def executar_matching(df_planilha, df_sql):

    # =========================
    # IDENTIFICAR DUPLICADOS
    # =========================

    dup_sql_k1 = df_sql[df_sql['Chave Cartão'].duplicated(keep=False)]
    dup_plan_k1 = df_planilha[df_planilha['Chave Cartão'].duplicated(keep=False)]

    dup_sql_k2 = df_sql[df_sql['Chave Cartão + LOC CIA'].duplicated(keep=False)]
    dup_plan_k2 = df_planilha[df_planilha['Chave Cartão + LOC CIA'].duplicated(keep=False)]

    dup_sql_k3 = df_sql[df_sql['Chave Cartão Sem data'].duplicated(keep=False)]
    dup_plan_k3 = df_planilha[df_planilha['Chave Cartão Sem data'].duplicated(keep=False)]

    df_duplicados = pd.concat([
        dup_sql_k1.assign(origem='sql_k1'),
        dup_plan_k1.assign(origem='plan_k1'),
        dup_sql_k2.assign(origem='sql_k2'),
        dup_plan_k2.assign(origem='plan_k2'),
        dup_sql_k3.assign(origem='sql_k3'),
        dup_plan_k3.assign(origem='plan_k3'),
    ], ignore_index=True)

    # =========================
    # CHAVES VÁLIDAS
    # =========================

    unicos_sql_k1 = df_sql['Chave Cartão'][~df_sql['Chave Cartão'].duplicated(keep=False)]
    unicos_plan_k1 = df_planilha['Chave Cartão'][~df_planilha['Chave Cartão'].duplicated(keep=False)]
    chaves_validas_k1 = set(unicos_sql_k1).intersection(set(unicos_plan_k1))

    unicos_sql_k2 = df_sql['Chave Cartão + LOC CIA'][~df_sql['Chave Cartão + LOC CIA'].duplicated(keep=False)]
    unicos_plan_k2 = df_planilha['Chave Cartão + LOC CIA'][~df_planilha['Chave Cartão + LOC CIA'].duplicated(keep=False)]
    chaves_validas_k2 = set(unicos_sql_k2).intersection(set(unicos_plan_k2))

    unicos_sql_k3 = df_sql['Chave Cartão Sem data'][~df_sql['Chave Cartão Sem data'].duplicated(keep=False)]
    unicos_plan_k3 = df_planilha['Chave Cartão Sem data'][~df_planilha['Chave Cartão Sem data'].duplicated(keep=False)]
    chaves_validas_k3 = set(unicos_sql_k3).intersection(set(unicos_plan_k3))

    # =========================
    # MAPAS
    # =========================

    map_k1 = df_sql[df_sql['Chave Cartão'].isin(chaves_validas_k1)].set_index('Chave Cartão')
    map_k2 = df_sql[df_sql['Chave Cartão + LOC CIA'].isin(chaves_validas_k2)].set_index('Chave Cartão + LOC CIA')
    map_k3 = df_sql[df_sql['Chave Cartão Sem data'].isin(chaves_validas_k3)].set_index('Chave Cartão Sem data')

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
        valores = df_planilha.loc[mask, 'Chave Cartão'].map(map_k1[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Cartão']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k1)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

        # k2
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Cartão + LOC CIA'].map(map_k2[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Cartão + LOC CIA']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k2)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

        # k3
        mask = df_planilha[col_dest] == '**********'
        valores = df_planilha.loc[mask, 'Chave Cartão Sem data'].map(map_k3[col_origem])
        chaves = df_planilha.loc[mask, 'Chave Cartão Sem data']

        idx = df_planilha.loc[mask].index
        idx_match = idx[chaves.isin(chaves_validas_k3)]

        df_planilha.loc[idx_match, 'match_encontrado'] = True
        df_planilha.loc[idx_match, col_dest] = valores.loc[idx_match]

        df_planilha.loc[idx_match[valores.loc[idx_match].isna()], col_dest] = 'NT'

    # =========================
    # NÃO LOCALIZADOS
    # =========================

    df_nao_localizados = df_planilha[df_planilha['match_encontrado'] == False].copy()

    # =========================
    # STATUS
    # =========================

    df_planilha['status'] = 'OK'

    df_planilha.loc[df_planilha['match_encontrado'] == False, 'status'] = 'NAO_LOCALIZADO'

    df_planilha.loc[
        (df_planilha['status'] == 'OK') &
        (df_planilha[list(regras.keys())] == 'NT').any(axis=1),
        'status'
    ] = 'NT'

    # =========================
    # LIMPEZA
    # =========================

    df_planilha.drop(columns=['match_encontrado'], inplace=True)

    # =========================
    # DATAFRAME FINAL
    # =========================

    df_preenchido = df_planilha.copy()