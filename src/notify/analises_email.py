
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

    <p>Este é o último alerta referente ao fechamento dos clientes abaixo.</p>

    <p>Caso os dados não sejam regularizados, os campos permanecerão sem preenchimento na fatura do cliente, podendo gerar impactos financeiros para a Flytour, além de ruídos comerciais junto aos clientes.</p>

    </p>Solicitamos a regularização ou inclusão ainda hoje, diretamente no Benner (não iremos considerar retornos via e-mail ou teams), considerando os campos obrigatórios do cliente (sinalizados com asterisco no arquivo).
    
    </p>Importante: todas as emissões da Flytour devem estar integradas no mesmo dia da emissão ou, em casos excepcionais de ajustes pontuais, em até 48 horas.</p>

    </p>O recebimento deste e-mail pela Squad indica que já estamos atuando de forma contingencial. Caso a regularização não ocorra dentro do prazo, contaremos com o apoio da Diretoria na gestão e divisão dos possíveis impactos.</p>

    <p><b>Resumo por Squad:</b><br>
    {html_tabela}
    
    """

def montar_corpo_diretoria(qtde_casos, dias_min):

    return f"""
    <p>Prezados,</p>

    <p>Identificamos <b>{qtde_casos} pendências</b> com proximidade de fechamento.</p>

    <p>O menor prazo atual é de <b>{dias_min} dias para o fechamento do cartão</b>.</p>

    <p>Os casos foram encaminhados para operação e caso não forem ajustados irão sem informação na fatura do cliente</p>

    <p>Atualizaremos em caso de evolução relevante.</p>
    """


