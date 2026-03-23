import pandas as pd

# O Bloco abaixo permite executar esse módulo filho sem usar o main
#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
#from src import config


def carregar_base_email(path):
    return pd.read_excel(path, sheet_name='Clientes_SAO CPQ',header=0)

#df = carregar_base_email(config.INPUT_PATH2)
#print(df['COLABORADOR'])