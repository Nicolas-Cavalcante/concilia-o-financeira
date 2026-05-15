import pandas as pd
import os

#==============================================
# 📌 Carrega LOG de Excução detalhado
#==============================================

def registrar_execucao_chaves(path, df_log_chaves):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        try:
            df_hist = pd.read_excel(path)
            df_final = pd.concat([df_hist, df_log_chaves], ignore_index=True)
        except PermissionError:
            df_final = df_log_chaves
            raise ValueError("O arquivo está aberto")
        except Exception as e:
            print(e)
    else:
        df_final = df_log_chaves

    df_final.to_excel(path, index=False)

#==============================================
# 📌 Carrega LOG de Excução detalha
#==============================================

def registra_execucao_detalhada(path, df_log):

    # Garante que a pasta exista
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # =========================
    # CARREGA HISTÓRICO
    # =========================
    if os.path.exists(path):
        try:
            df_hist = pd.read_excel(path)
            df_hist['data_execucao'] = pd.to_datetime(df_hist['data_execucao']).dt.normalize()

            # Separa histórico de dias anteriores — esses nunca são tocados
            df_dias_anteriores = df_hist[
                df_hist['data_execucao'] != df_log['data_execucao'].iloc[0]
            ]

            # Separa histórico do dia atual
            df_hoje_hist = df_hist[
                df_hist['data_execucao'] == df_log['data_execucao'].iloc[0]
            ]

            if df_hoje_hist.empty:
                # Primeira execução do dia — insere direto
                df_hoje_final = df_log
            else:
                df_merged = df_hoje_hist.merge(
                    df_log[['celula', 'corretos', 'incorretos', 'ausencia_de_dados']],
                    on='celula',
                    how='outer',
                    suffixes=('_hist', '_novo')
                )

                df_merged['corretos'] = (
                    df_merged['corretos_hist'].fillna(0) +
                    df_merged['corretos_novo'].fillna(0)
                )

                # incorretos e ausencia_de_dados → substitui pelo novo, mantém histórico se célula não apareceu
                df_merged['incorretos'] = df_merged['incorretos_novo'].combine_first(
                    df_merged['incorretos_hist']
                )
                df_merged['ausencia_de_dados'] = df_merged['ausencia_de_dados_novo'].combine_first(
                    df_merged['ausencia_de_dados_hist']
                )

                # Remove colunas auxiliares do merge
                df_merged = df_merged.drop(columns=[
                    'corretos_hist', 'corretos_novo',
                    'incorretos_hist', 'incorretos_novo',
                    'ausencia_de_dados_hist', 'ausencia_de_dados_novo',
                ])

                # Preenche colunas fixas que vieram nulas do outer (células novas)
                for col in ['data_execucao', 'Nome da Empresa', 'status_email', 'usuario']:
                    if col in df_log.columns:
                        df_merged[col] = df_merged[col].combine_first(
                            df_log.set_index('celula')[col].reindex(df_merged['celula'])
                        )

                df_hoje_final = df_merged

            df_final = pd.concat([df_dias_anteriores, df_hoje_final], ignore_index=True)

        except PermissionError:
            raise ValueError("O arquivo de log está aberto. Feche-o e execute novamente.")
        except Exception as e:
            print(f"[AVISO] Erro ao ler log detalhado: {e}")
            df_final = df_log
    else:
        df_final = df_log

    df_final.to_excel(path, index=False)
  