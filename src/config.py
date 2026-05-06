from pathlib import Path
import sys
from dotenv import load_dotenv

# ==============================
# 🔹 BASE DO SISTEMA (para recursos internos, ex: logo)
# ==============================
def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_path()

# ==============================
# 🔹 BASE DE EXECUÇÃO (onde roda o EXE)
# ==============================
EXEC_DIR = (
    Path(sys.executable).parent
    if getattr(sys, 'frozen', False)
    else Path.cwd()
)

load_dotenv(EXEC_DIR / ".env")

if not (EXEC_DIR / ".env").exists():
    raise FileNotFoundError(".env não encontrado")
# ==============================
# 📁 OUTPUTS (sempre fora do exe)
# ==============================
OUTPUT_BASE = EXEC_DIR / "outputs"
OUTPUT_CORRETOS = OUTPUT_BASE / "Corretos"
OUTPUT_INCORRETOS = OUTPUT_BASE / "Incorretos"

# ==============================
# 📁 LOGS (também fora do exe)
# ==============================
LOG_DIR = EXEC_DIR / "logs"
LOG_PATH = LOG_DIR / "historico_execucao.xlsx"
LOG_DETALHE_PATH = LOG_DIR / "historico_execucao_detalhado.xlsx"

# ==============================
# 📁 GARANTE QUE AS PASTAS EXISTEM
# ==============================
OUTPUT_CORRETOS.mkdir(parents=True, exist_ok=True)
OUTPUT_INCORRETOS.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)