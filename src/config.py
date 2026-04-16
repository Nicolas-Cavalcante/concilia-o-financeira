#==============================
# Config salva o local de caminho dos arquivos de entrada e saída
#==============================

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

#==============================
# Caminho outputs
#==============================
OUTPUT_BASE = BASE_DIR / "outputs"
OUTPUT_CORRETOS = OUTPUT_BASE / "Corretos"
OUTPUT_INCORRETOS = OUTPUT_BASE / "Incorretos"

#==============================
# Caminho logs
#==============================
LOG_PATH = BASE_DIR / "logs" / "historico_execucao.xlsx"
LOG_DETALHE_PATH = BASE_DIR / "logs" / "historico_execucao_dt.xlsx"
LOG_CLIENTE_PATH = BASE_DIR / "logs" / "historico_cliente.xlsx"

#==============================
# garante que as pastas existem
#==============================
LOG_PATH.parent.mkdir(exist_ok=True)
OUTPUT_CORRETOS.mkdir(parents=True, exist_ok=True)
OUTPUT_INCORRETOS.mkdir(parents=True, exist_ok=True)


