import pandas as pd
import os
from datetime import datetime

def registrar_execucao(path, dados):

    if os.path.exists(path):
        df = pd.read_excel(path)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)

    df.to_excel(path, index=False)