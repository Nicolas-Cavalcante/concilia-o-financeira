import pandas as pd
import os


#==============================================
# 📌 LOG DE CHAVES
#==============================================

def registrar_execucao_chaves(path, df_log_chaves):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        try:
            df_hist = pd.read_excel(path)
            df_hist['data_execucao'] = pd.to_datetime(df_hist['data_execucao']).dt.normalize()

            # Remove linhas onde a chave composta já existe no novo log
            chave_nova = set(
                zip(
                    df_log_chaves['data_execucao'],
                    df_log_chaves['chave']
                )
            )
            mask = ~df_hist.apply(
                lambda r: (r['data_execucao'], r['chave']) in chave_nova, axis=1
            )
            df_hist_filtrado = df_hist[mask]

            df_final = pd.concat([df_hist_filtrado, df_log_chaves], ignore_index=True)

        except PermissionError:
            raise ValueError("O arquivo de log de chaves está aberto. Feche-o e execute novamente.")
        except Exception as e:
            print(f"[AVISO] Erro ao ler log de chaves: {e}")
            df_final = df_log_chaves
    else:
        df_final = df_log_chaves

    df_final.to_excel(path, index=False)


#==============================================
# 📌 LOG DETALHADO
#==============================================

def registra_execucao_detalhada(path, df_log):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        try:
            df_hist = pd.read_excel(path)
            df_hist['data_execucao'] = pd.to_datetime(df_hist['data_execucao']).dt.normalize()

            # Separa dias anteriores — nunca tocados
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
                # Reprocessamento — upsert por celula
                # corretos → soma | incorretos e ausencia_de_dados → substitui
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

                df_merged['incorretos'] = df_merged['incorretos_novo'].combine_first(
                    df_merged['incorretos_hist']
                )
                df_merged['ausencia_de_dados'] = df_merged['ausencia_de_dados_novo'].combine_first(
                    df_merged['ausencia_de_dados_hist']
                )

                df_merged = df_merged.drop(columns=[
                    'corretos_hist', 'corretos_novo',
                    'incorretos_hist', 'incorretos_novo',
                    'ausencia_de_dados_hist', 'ausencia_de_dados_novo',
                ])

                # Preenche colunas fixas para células novas (outer join)
                for col in ['data_execucao', 'status_email', 'usuario']:
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