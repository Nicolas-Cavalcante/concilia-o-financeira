"""
generate_mock_data.py
=====================
Gera dados sintéticos para demonstração do SmartCheck no portfólio.

- Cria o banco SQLite (substitui SQL Server em ambiente demo)
- Gera os arquivos Excel de entrada (pendências, base de e-mails, de-para)
- Cobre os três status de saída: Ok, Não Localizado, Ausência de Dados
- Distribui os casos em proporções realistas (~70% Ok, ~20% NL, ~10% AD)

Execute:
    python generate_mock_data.py

Saída:
    demo.db                          ← banco SQLite com tabela de transações
    inputs/pendencias_demo.xlsx      ← arquivo de pendências (entrada principal)
    inputs/Base_emails.xlsx          ← base de e-mails dos responsáveis
    inputs/De_Para_demo.xlsx         ← regras de mapeamento por cliente

Nota: todos os dados são sintéticos. Nomes, valores e referências
não correspondem a nenhuma operação real.
"""

import sqlite3
import random
import string
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# ── Configuração ────────────────────────────────────────────────────────────

random.seed(42)

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "inputs"
INPUT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "demo.db"

# Proporção dos status nos dados gerados
TOTAL_RECORDS = 120
PCT_OK = 0.70          # 84 registros → match completo
PCT_NAO_LOC = 0.20     # 24 registros → sem match em nenhuma chave
PCT_AUSENCIA = 0.10    # 12 registros → match encontrado, mas campo vazio no banco

N_OK = int(TOTAL_RECORDS * PCT_OK)
N_NAO_LOC = int(TOTAL_RECORDS * PCT_NAO_LOC)
N_AUSENCIA = TOTAL_RECORDS - N_OK - N_NAO_LOC

# Empresas fictícias (simulam clientes)
EMPRESAS = ["AEROTECH", "SKYLINES", "VIAJAX", "TRANSCORP", "ROTALINK"]

# gerado uma única vez — compartilhado entre pendências e base de e-mails
COMP_POR_EMPRESA = {emp: str(random.randint(10000, 99999)) for emp in EMPRESAS}

# Localizadores de cia aérea (6 chars alfanuméricos)
def rand_loc():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Número de autorização (8 dígitos)
def rand_aut():
    return str(random.randint(10000000, 99999999))

# Últimos 3 dígitos do cartão
def rand_card_suffix():
    return str(random.randint(100, 999))

# Data aleatória dentro da janela de 3 meses
def rand_date():
    today = date.today()
    delta = random.randint(0, 89)
    return (today - timedelta(days=delta)).strftime("%Y-%m-%d")

# Valor monetário (R$)
def rand_valor():
    return round(random.uniform(50.0, 8000.0), 2)

# Ausência de dado (conforme regra implícita do sistema)
AUSENCIA_MARKER = "**********"


# ── 1. Geração dos registros base ───────────────────────────────────────────

def gerar_registro(idx: int, tipo: str) -> dict:
    """Gera um registro com campos consistentes para matching."""
    empresa = random.choice(EMPRESAS)
    data = rand_date()
    valor = rand_valor()
    aut = rand_aut()
    nr_aut = rand_aut()
    loc = rand_loc()
    cartao = rand_card_suffix()

    return {
        "idx": idx,
        "tipo": tipo,           # ok | nao_loc | ausencia
        "empresa": empresa,
        "data": data,
        "valor": valor,
        "aut": aut,
        "nr_aut": nr_aut,
        "loc_cia": loc,
        "cartao": cartao,
        "comp": COMP_POR_EMPRESA[empresa],
        # Chaves compostas (espelham a lógica de matching do SmartCheck)
        "k1": f"{aut}_{data}_{valor:.2f}",
        "k2": f"{nr_aut}_{data}_{valor:.2f}",
        "k3": f"{loc}_{data}_{valor:.2f}",
        "k4": f"{cartao}_{data}_{valor:.2f}_{loc}",
        "k5": f"{cartao}_{valor:.2f}_{loc}",
    }

registros_ok       = [gerar_registro(i, "ok")       for i in range(N_OK)]
registros_nao_loc  = [gerar_registro(i + N_OK, "nao_loc") for i in range(N_NAO_LOC)]
registros_ausencia = [gerar_registro(i + N_OK + N_NAO_LOC, "ausencia") for i in range(N_AUSENCIA)]

todos = registros_ok + registros_nao_loc + registros_ausencia
random.shuffle(todos)


# ── 2. Banco SQLite ─────────────────────────────────────────────────────────

def criar_banco(registros: list[dict]) -> None:
    """
    Cria demo.db com a tabela 'transacoes', espelhando o schema do SQL Server.

    Registros 'nao_loc' NÃO são inseridos no banco → matching vai falhar.
    Registros 'ausencia' são inseridos com campo 'passageiro' vazio → match
    ocorre, mas o campo crítico retorna vazio (simula Ausência de Dados).
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS transacoes")
    cur.execute("""
        CREATE TABLE transacoes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa     TEXT,
            data        TEXT,
            valor       REAL,
            aut         TEXT,
            nr_aut      TEXT,
            loc_cia     TEXT,
            cartao      TEXT,
            passageiro  TEXT,
            bilhete     TEXT,
            trecho      TEXT,
            k1          TEXT,
            k2          TEXT,
            k3          TEXT,
            k4          TEXT,
            k5          TEXT
        )
    """)

    for r in registros:
        if r["tipo"] == "nao_loc":
            # Não insere → garante "Não Localizado" ao fazer o match
            continue

        passageiro = AUSENCIA_MARKER if r["tipo"] == "ausencia" else _rand_name()
        bilhete    = AUSENCIA_MARKER if r["tipo"] == "ausencia" else str(random.randint(1000000000, 9999999999))
        trecho     = _rand_trecho()

        cur.execute("""
            INSERT INTO transacoes
                (empresa, data, valor, aut, nr_aut, loc_cia, cartao,
                 passageiro, bilhete, trecho, k1, k2, k3, k4, k5)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["empresa"], r["data"], r["valor"],
            r["aut"], r["nr_aut"], r["loc_cia"], r["cartao"],
            passageiro, bilhete, trecho,
            r["k1"], r["k2"], r["k3"], r["k4"], r["k5"],
        ))

    conn.commit()
    conn.close()
    print(f"[OK] Banco criado: {DB_PATH}")
    print(f"     Registros no banco: {N_OK + N_AUSENCIA} "
          f"({N_OK} Ok + {N_AUSENCIA} Ausência de Dados)")
    print(f"     Não inseridos (→ Não Localizado): {N_NAO_LOC}")


def _rand_name() -> str:
    primeiros = ["CARLOS", "ANA", "LUCAS", "MARIANA", "PEDRO",
                 "BEATRIZ", "RAFAEL", "CAMILA", "THIAGO", "JULIA"]
    sobrenomes = ["SILVA", "SOUZA", "COSTA", "LIMA", "PEREIRA",
                  "ALVES", "SANTOS", "ROCHA", "MARTINS", "FERREIRA"]
    return f"{random.choice(primeiros)} {random.choice(sobrenomes)}"


def _rand_trecho() -> str:
    aeroportos = ["GRU", "CGH", "BSB", "GIG", "SSA",
                  "FOR", "REC", "CWB", "POA", "BEL"]
    origem, destino = random.sample(aeroportos, 2)
    return f"{origem}-{destino}"


# ── 3. Planilha de pendências (entrada principal) ────────────────────────────

def gerar_pendencias(registros: list[dict]) -> None:
    """Gera inputs/pendencias_demo.xlsx — arquivo de entrada do SmartCheck."""
    linhas = []
    for r in registros:
        linhas.append({
            "Empresa":      r["empresa"],
            "Data":         r["data"],
            "Valor":        r["valor"],
            "Aut":          r["aut"],
            "nr_aut":       r["nr_aut"],
            "Loc Cia":      r["loc_cia"],
            "Cartao":       r["cartao"],
            # Campos que serão preenchidos pelo SmartCheck após o match
            "Passageiro":   "",
            "Bilhete":      "",
            "Trecho":       "",
            "Status":       "",
            "Chave Usada":  "",
        })

    df = pd.DataFrame(linhas)
    path = INPUT_DIR / "pendencias_demo.xlsx"

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Pendências")
        ws = writer.sheets["Pendências"]
        _estilizar_cabecalho(ws, len(df.columns))

    print(f"[OK] Pendências geradas: {path}  ({len(linhas)} registros)")


# ── 4. Base de e-mails ───────────────────────────────────────────────────────

def gerar_base_emails() -> None:
    dados = []
    dominios = ["empresa.com.br", "corp.net", "gestao.io"]
    
    for emp in EMPRESAS:
        nome_responsavel = _rand_name().title()
        nome_supervisor  = _rand_name().title()
        nome_coordenador = _rand_name().title()
        nome_gerente     = _rand_name().title()
        
        squad_email = f"{nome_responsavel.split()[0].lower()}@{random.choice(dominios)}"
        
        dados.append({
            "Nº Cliente/COMP":  COMP_POR_EMPRESA,           # obrigatório — chave de join com pendências
            "SQUADS":           emp,             # obrigatório — validação do carregar_base_email
            "E-MAIL SQUADS":    squad_email,
            "SUPERVISOR":       f"{nome_supervisor.split()[0].lower()}@{random.choice(dominios)}",
            "COORDENADOR":      f"{nome_coordenador.split()[0].lower()}@{random.choice(dominios)}",
            "GERENTE":          f"{nome_gerente.split()[0].lower()}@{random.choice(dominios)}",
        })

    df = pd.DataFrame(dados)
    path = INPUT_DIR / "Base_emails.xlsx"

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Emails")
        ws = writer.sheets["Emails"]
        _estilizar_cabecalho(ws, len(df.columns))

    print(f"[OK] Base de e-mails gerada: {path}")


# ── 5. De-Para ───────────────────────────────────────────────────────────────

def gerar_depara() -> None:
    """
    Gera inputs/De_Para_demo.xlsx — regras de mapeamento por cliente.
    Inclui uma entrada DEFAULT e overrides por empresa.
    """
    dados = [
        # Regra padrão (aplicada a todos que não têm regra específica)
        {"Cliente": "DEFAULT", "Campo": "Trecho",     "De": "",    "Para": "N/A"},
        {"Cliente": "DEFAULT", "Campo": "Passageiro", "De": "",    "Para": "NÃO INFORMADO"},
        # Overrides por empresa
        {"Cliente": "AEROTECH", "Campo": "Trecho",    "De": "",    "Para": "AEROTECH-DEFAULT"},
        {"Cliente": "SKYLINES",  "Campo": "Bilhete",  "De": "",    "Para": "SKY-000"},
    ]

    df = pd.DataFrame(dados)
    path = INPUT_DIR / "De_Para_demo.xlsx"

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="De-Para")
        ws = writer.sheets["De-Para"]
        _estilizar_cabecalho(ws, len(df.columns))

    print(f"[OK] De-Para gerado: {path}")


# ── Utilitário de estilo ─────────────────────────────────────────────────────

def _estilizar_cabecalho(ws, n_cols: int) -> None:
    """Aplica estilo ao cabeçalho da planilha."""
    fill   = PatternFill("solid", fgColor="1F3864")
    fonte  = Font(bold=True, color="FFFFFF", size=11)
    borda  = Border(
        bottom=Side(style="medium", color="2F5496"),
    )
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill  = fill
        cell.font  = fonte
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = borda

    # Ajuste automático de largura
    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    ws.row_dimensions[1].height = 20
    ws.freeze_panes = "A2"


# ── Resumo final ─────────────────────────────────────────────────────────────

def imprimir_resumo() -> None:
    print()
    print("=" * 55)
    print("  SmartCheck — Mock Data gerado com sucesso")
    print("=" * 55)
    print(f"  Total de registros : {TOTAL_RECORDS}")
    print(f"  Ok (match completo): {N_OK}  ({PCT_OK:.0%})")
    print(f"  Não Localizado     : {N_NAO_LOC}  ({PCT_NAO_LOC:.0%})")
    print(f"  Ausência de Dados  : {N_AUSENCIA}   ({PCT_AUSENCIA:.0%})")
    print()
    print("  Arquivos gerados:")
    print(f"    demo.db")
    print(f"    inputs/pendencias_demo.xlsx")
    print(f"    inputs/Base_emails.xlsx")
    print(f"    inputs/De_Para_demo.xlsx")
    print()
    print("  Conexão SQLite (substitui SQL Server em demo):")
    print('    conn = sqlite3.connect("demo.db")')
    print("=" * 55)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    criar_banco(todos)
    gerar_pendencias(todos)
    gerar_base_emails()
    gerar_depara()
    imprimir_resumo()
