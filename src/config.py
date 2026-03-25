#==============================
#Config salva o local de caminho dos arquivos de entrada e saída
#==============================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_BASE = BASE_DIR / "outputs"
OUTPUT_CORRETOS = OUTPUT_BASE / "Corretos"
OUTPUT_INCORRETOS = OUTPUT_BASE / "Incorretos"
LOG_PATH = BASE_DIR / "logs" / "historico_execucao.xlsx"

# garante que as pastas existem
LOG_PATH.parent.mkdir(exist_ok=True)
OUTPUT_CORRETOS.mkdir(parents=True, exist_ok=True)
OUTPUT_INCORRETOS.mkdir(parents=True, exist_ok=True)

#Arquivo pendências
#INPUT_PATH = r"C:\Users\nicolas.cavalcante\OneDrive - BEFLY TRAVEL\Área de Trabalho\Teste_python\EBTA\PendenciasAereo_20260305-092004.xlsx"

#Arquivo base de clientes
#INPUT_PATH2 = r"C:\Users\nicolas.cavalcante\OneDrive - BEFLY TRAVEL\Área de Trabalho\Teste_python\EBTA\25FEB26_Contatos Squads_SAO e CPQ.xlsx"

#Pasta dos arquivos de saída
#OUTPUT_PATH = r"C:\Users\nicolas.cavalcante\OneDrive - BEFLY TRAVEL\Documentos\GitHub\projeto-conciliacao_ebta\outputs"
#LOG_PATH = "logs/historico_execucao.xlsx"

#teste
MAIOR_MARGEM = 28
MENOR_MARGEM = 10
DIAS_ALERTA = 5
DIAS_CRITICO = 2


