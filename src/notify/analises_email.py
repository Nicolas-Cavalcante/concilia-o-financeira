
#==============================================
# Este arquivo processa o conteudo que ira compor
# o corpo do e-mail. Nele teremos as funções sendo chamadas no main:
#   classificar_aging;
#   compara_movimento;
#   monta_corpo_email.
#==============================================

from src.extract.pendencias import carregar_planilha

#==============================================
# 📩 1. CLASSIFICA AGING POR CRITICIDADE
#==============================================

def classifica_agin(df):
    contagem = df['Status do Processo'].value_counts().to_dict()
    
    return {
        "Urgente": contagem.get("🔴 Urgente", 0),
        "Critico": contagem.get("⚠️ Critico", 0),
        "Alta": contagem.get("🟠 Alta", 0),
        "Média": contagem.get("🟡 Média", 0),
        "Baixa": contagem.get("🟢 Baixa", 0),
    }
  

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

def montar_corpo_email(stats_atual, stats_movimento):

    return f"""
    <p style="font-family: Calibri; font-size:11pt; color: #333333;">
    <p>Olá,</p>

    <p>Identificamos pendências em registros do seu atendimento.</p>

    <p><b>Pontos importantes:</b><br>
    </p>É necessário verficar se a venda foi lançada, revisar e corrigir os campos sinalizados com asterisco (*) mencionados no arquivo e validar dentro do benner, pois essas informações não foram localizadas no sistema.

    </p>Caso os dados não sejam ajustados, os campos permanecerão sem informação na fatura do cliente.</p>

    </p>Após a correção, as transações serão atualizadas em até 24 horas.</p>

    </p>Solicitamos a regularização o quanto antes para evitar impactos para o cliente.</p>

    <p><b>Detalhamento dos casos:</b></p>

    <p>🔴 URGENTE: {stats_atual['Urgente']}<br>
    ⚠️ CRÍTICA: {stats_atual['Critico']}<br>
    🟠 ALTA: {stats_atual['Alta']}<br>
    🟡 MÉDIA: {stats_atual['Média']}<br>
    🟢 BAIXA: {stats_atual['Baixa']}</p>

    <p><b>Resumo de evolução (vs ontem):</b></p>

    <p>🔺 +{stats_movimento['Novos']} novos casos<br>
    🔻 {stats_movimento['Resolvidos']} resolvidos<br>
    ⚠️ {stats_movimento['Pioraram']} se aproximaram do fechamento<br>
    ✅ {stats_movimento['Melhoraram']} ganharam prazo</p>
    """


