
#==============================================
# Este arquivo processa o conteudo que ira compor
# o corpo do e-mail. Nele teremos as funções sendo chamadas no main:
#   classificar_aging;
#   compara_movimento;
#   monta_corpo_email.
#==============================================

from src.matching.conciliacao import executar_matching

#==============================================
# 🔄️ 2. COMPARA MOVIMENTO DAS PENDÊNCIAS
#==============================================

ID_Col = "MatchID"

def compara_movimento(df_hoje, df_ontem):
    hoje_ids = set(df_hoje[ID_Col])
    ontem_ids = set(df_ontem[ID_Col])
                    
    novos = hoje_ids - ontem_ids
    resolvidos = ontem_ids - hoje_ids

    df_merge = df_hoje.merge(df_ontem, on=ID_Col, suffixes=("_hoje", "_ontem"))

    pioraram = df_merge[df_merge["aging_hoje"] < df_merge["aging_ontem"]]
    melhoraram = df_merge[df_merge["aging_hoje"] > df_merge["aging_ontem"]]

    return {
        "Novos": len(novos),
        "Resolvidos": len(resolvidos),
        "Pioraram": len(pioraram),
        "Melhoraram": len(melhoraram),
    }


#==============================================
# 📝 3. MONTA O CORPO DO E-MAIL
#==============================================

def montar_corpo_email(html_tabela):

    return f"""
    <p style="font-family: Calibri; font-size:11pt; color: #333333;">
    <p>Olá,</p>

    <p>Identificamos pendências em registros do seu atendimento.</p>

    <p>Os casos apontados no arquivo não foram localizados no sistema ou estão com informações faltantes.

    </p>É necessário verficar se a venda foi lançada, revisar e corrigir os campos sinalizados com asterisco (*) mencionados no arquivo e validar dentro do benner, pois essas informações não foram localizadas no sistema.

    <p><b>Resumo por Squad:</b><br>
    {html_tabela}
    
    </p>Caso os dados não sejam ajustados, os campos permanecerão sem informação na fatura do cliente.</p>

    </p>Após a correção, as transações serão atualizadas em até 24 horas.</p>

    </p>Solicitamos a regularização o quanto antes para evitar impactos para o cliente.</p>

    <p><b>Resumo de evolução (vs ontem):</b></p>

    """

def montar_corpo_diretoria(qtde_casos, dias_min):

    return f"""
    <p>Prezados,</p>

    <p>Identificamos <b>{qtde_casos} pendências</b> com proximidade de fechamento.</p>

    <p>O menor prazo atual é de <b>{dias_min} dias para o fechamento do cartão</b>.</p>

    <p>Os casos foram encaminhados para operação e caso não forem ajustados irão sem informação na fatura do cliente</p>

    <p>Atualizaremos em caso de evolução relevante.</p>
    """


