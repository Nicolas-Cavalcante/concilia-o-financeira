
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

    <p>Seguem as pendências de lançamento de sua Squad no arquivo anexo.</p>

    <p>Solicitamos a regularização dos casos enviados diretamente no Benner, considerando que os campos obrigatórios do cliente (sinalizados com asterisco no arquivo), bem como as informações de Autorização e Data de Emissão, devem ser corrigidos diretamente em sistema. Não serão considerados retornos via e-mail ou Teams.</p>

    </p>Pedimos que todos os casos estejam ajustados no sistema em até 24 hora anteriores à data de fechamento, a fim de evitar possíveis impactos financeiros para a Flytour, mitigando riscos relacionados ao não pagamento da fatura pelo cliente.
    
    </p>Importante: todas as emissões da Flytour devem estar integradas no mesmo dia da emissão ou, em casos excepcionais de ajustes pontuais, em até 48 horas.</p>

    </p>O recebimento deste e-mail pela Squad indica que já estamos atuando de forma contingencial. Caso a regularização não ocorra dentro do prazo, contaremos com o apoio da Diretoria na gestão e divisão dos possíveis impactos.</p>

    <p><b>Resumo por cliente:</b><br>
    {html_tabela}
    
    """

def montar_corpo_email_gestor(html_tabela):

    return f"""
    <p style="font-family: Calibri; font-size:11pt; color: #333333;">
    <p>Olá, Gestor(a)!</p>

    <p>Seguem as pendências de lançamento de sua(s) Squad(s) no arquivo anexo.</p>

    <p>Solicitamos a regularização dos casos enviados diretamente no Benner, considerando que os campos obrigatórios do cliente (sinalizados com asterisco no arquivo), bem como as informações de Autorização e Data de Emissão, devem ser corrigidos diretamente em sistema. Não serão considerados retornos via e-mail ou Teams.</p>

    </p>Pedimos que todos os casos estejam lançados e/ou corrigidos em sistema em até 24 horas antes do prazo de fechamento, evitando impactos financeiros à Flytour.
    
    </p>Importante: todas as emissões da Flytour devem estar integradas no mesmo dia da emissão ou, em casos excepcionais de ajustes pontuais, em até 48 horas.</p>

    </p>O recebimento deste e-mail pela Gestão indica que já estamos atuando de forma contingencial. Caso a regularização não ocorra dentro do prazo, contaremos com o apoio da Diretoria na gestão e divisão dos possíveis impactos.</p>

    <p><b>Resumo por Squad:</b><br>
    {html_tabela}
    
    """

def montar_corpo_diretoria():

    return f"""
    <p>Olá,</p>

    <p>Este é o último alerta referente ao fechamento dos clientes abaixo.</p>

    <p>Caso os dados não sejam regularizados, os campos permanecerão sem preenchimento na fatura do cliente, podendo gerar impactos financeiros para a Flytour, além de ruídos comerciais junto aos clientes.</p>
    
    <p>Solicitamos a regularização ou inclusão ainda hoje, diretamente no Benner (não iremos considerar retornos via e-mail ou teams), considerando os campos obrigatórios do cliente (sinalizados com asterisco no arquivo).</p>
    
    <p>Importante: todas as emissões da Flytour devem estar integradas no mesmo dia da emissão ou, em casos excepcionais de ajustes pontuais, em até 48 horas.</p>
    
    <p>O recebimento deste e-mail pela Squad indica que já estamos atuando de forma contingencial. Caso a regularização não ocorra dentro do prazo, contaremos com o apoio da Diretoria na gestão e divisão dos possíveis impactos.</p>
 
    """


