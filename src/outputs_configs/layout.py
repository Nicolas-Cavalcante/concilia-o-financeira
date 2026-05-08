
# =========================
# 📝 ESTE ARQUIVO É RESPONSÁVEL POR APLICAR O MODELO DE COLUNAS PARA O ARQUIVO FINAL QUE SOBE AO BANCO,
# E O ARQUIVO QUE É ENCAMINHADO PARA OPERAÇÃO.
#
# - O LAYOUT APLICADO PELA FUNÇÃO É CHAMADO NO MAIN ANTES DO BLOCO QUE CHAMA A FUNÇÃO SALVAR.
# =========================


    # =========================
    # ⚙️ AJUSTA MODELO FINAL APENAS COM CASOS CORRETOS
    # =========================

def formatar_valor_brasileiro(df, colunas):
    df = df.copy()

    for coluna in colunas:
        if coluna in df.columns:
            df[coluna] = df[coluna].apply(
                lambda x: str(x).replace('.', ',') if x != '' and x is not None else x
            )

    return df




def montar_layout_conciliados(df):
    colunas = [
       "MatchID",
        "Aging Venda",
        "Aging Corte",
        "Nº Cliente/COMP",
        "Cartão",
        "Agência",
        "Nome da Empresa",
        "Autorização",
        "Data de Emissão",
        "Valor Total",
        "Valor Bilhete (Travel)",
        "Cia Aérea",
        "Nome da Cia Aérea",
        "Ticket",
        "Débito/Fee",
        "Desconto/Rebate",
        "Centro de Custo",
        "Data Ida",
        "Data Volta",
        "Passageiro",
        "Trecho Voado",
        "Classe",
        "Departamento",
        "Matricula",
        "Requisição",
        "Solicitante",
        "Aprovador",
        "Localizador",
        "Livre 1",
        "Livre 2",
        "Livre 3",
        "Empresa Empregado",
        "Taxa de Embarque",
        "Taxa de Repasse",
        "Tipo"
    ]
    for col in colunas:
        if col not in df.columns:
            df[col] = ''

    df_final = df[colunas].copy()
    df_final = formatar_valor_brasileiro(df_final, ['Valor Total'])

    return df_final

    # =========================
    # ⚙️ AJUSTA MODELO NÃO LOCALIZADO COM CASOS NÃO ENCONTRADOS E COLUNAS COM AUSÊNCIA DE DADOS
    # =========================

def montar_layout_nao_localizados(df):
    colunas = [
        "MatchID",
        "Aging Venda",
        "Aging Corte",
        "Nº Cliente/COMP",
        "Cartão",
        "Agência",
        "Nome da Empresa",
        "Autorização",
        "Data de Emissão",
        "Valor Total",
        "Valor Bilhete (Travel)",
        "Cia Aérea",
        "Nome da Cia Aérea",
        "Ticket",
        "Débito/Fee",
        "Desconto/Rebate",
        "Centro de Custo",
        "Data Ida",
        "Data Volta",
        "Passageiro",
        "Trecho Voado",
        "Classe",
        "Departamento",
        "Matricula",
        "Requisição",
        "Solicitante",
        "Aprovador",
        "Localizador",
        "Livre 1",
        "Livre 2",
        "Livre 3",
        "Empresa Empregado",
        "Taxa de Embarque",
        "Taxa de Repasse",
        "Tipo",
        "Data Fechamento Cartão",
        "Dias Restantes",
        "status"
    ]
    for col in colunas:
        if col not in df.columns:
            df[col] = ''
    
    df_final = df[colunas].copy()
    df_final = formatar_valor_brasileiro(df_final, ['Valor Total'])

    return df_final
