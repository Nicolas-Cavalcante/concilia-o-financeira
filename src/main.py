from extract.database import carregar_sql
from extract.sharepoint import carregar_planilha
from transform.tratamento import tratar_dados
from matching.conciliacao import executar_matching
from export.salvar import salvar

def main():

    arquivo = r"C:\...\Pendencias.xlsx"

    df_planilha = carregar_planilha(arquivo)
    df_sql = carregar_sql()

    df_planilha = tratar_dados(df_planilha)

    df_final, df_nao_localizados, df_duplicados = executar_matching(df_planilha, df_sql)

    salvar(df_final, df_nao_localizados, "outputs")

    print("Processamento concluído.")

if __name__ == "__main__":
    main()