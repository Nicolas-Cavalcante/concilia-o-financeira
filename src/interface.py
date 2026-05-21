import os
import subprocess
import sys
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageOps, ImageTk

import src.main
from src import config
from src.tela_processamento import tela_processamento


APP_NAME = "SmartCheck"
WINDOW_TITLE = ""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
enviar_email_var = tk.BooleanVar(value=False)


def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_exec_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


BASE_PATH = get_base_path()
EXEC_DIR  = get_exec_dir()
INPUTS_DIR = EXEC_DIR / "inputs"

arquivos_selecionados = {
    "pendencias": None,
    "emails":     None,
}


# ─────────────────────────────────────────────
#  RECURSOS VISUAIS
# ─────────────────────────────────────────────

def carregar_background():
    caminho = BASE_PATH / "fundo_fly.png"
    if not caminho.exists():
        img = Image.new("RGBA", (1600, 900), "#0E1322")
    else:
        img = Image.open(caminho).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 145))
    return Image.alpha_composite(img, overlay)


def carregar_logo():
    caminho = BASE_PATH / "logo_fly_branca.png"
    if not caminho.exists():
        return None
    img = Image.open(caminho)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(150, 74))


BACKGROUND_IMG = carregar_background()
LOGO_IMG       = carregar_logo()


# ─────────────────────────────────────────────
#  UTILITÁRIOS DE JANELA
# ─────────────────────────────────────────────

def limpar_tela():
    for widget in root.winfo_children():
        widget.destroy()


def configurar_janela_ampla():
    root.title(WINDOW_TITLE)
    root.configure(fg_color="#0E1322")
    root.resizable(True, True)
    root.minsize(900, 580)
    root.deiconify()
    try:
        root.state("zoomed")
    except tk.TclError:
        largura = int(root.winfo_screenwidth() * 0.9)
        altura  = int(root.winfo_screenheight() * 0.88)
        x = (root.winfo_screenwidth()  - largura) // 2
        y = (root.winfo_screenheight() - altura)  // 2
        root.geometry(f"{largura}x{altura}+{x}+{y}")


def criar_background():
    canvas = tk.Canvas(root, highlightthickness=0, bd=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def redesenhar(event=None):
        largura = max(canvas.winfo_width(), 1)
        altura  = max(canvas.winfo_height(), 1)
        img     = ImageOps.fit(BACKGROUND_IMG, (largura, altura), Image.LANCZOS)
        bg_tk   = ImageTk.PhotoImage(img)
        canvas.bg_tk = bg_tk
        canvas.delete("background")
        canvas.create_image(0, 0, anchor="nw", image=bg_tk, tags="background")

    canvas.bind("<Configure>", redesenhar)
    root.after(0, redesenhar)
    return canvas


# ─────────────────────────────────────────────
#  UTILITÁRIOS DE ARQUIVO
# ─────────────────────────────────────────────

def buscar_arquivo_emails():
    if not INPUTS_DIR.exists():
        return None
    arquivos = [
        f for f in INPUTS_DIR.rglob("*.xlsx")
        if f.name.lower() == "base_emails.xlsx"
    ]
    return arquivos[0] if len(arquivos) == 1 else None


def buscar_arquivo_pendencias():
    if not INPUTS_DIR.exists():
        return None
    arquivos = [
        f for f in INPUTS_DIR.rglob("*.xlsx")
        if f.name.lower().startswith("pendencias")
    ]
    return arquivos[0] if len(arquivos) == 1 else None


def primeira_pasta_inputs(prefixo):
    if not INPUTS_DIR.exists():
        return EXEC_DIR
    for pasta in INPUTS_DIR.iterdir():
        if pasta.is_dir() and pasta.name.lower().startswith(prefixo.lower()):
            return pasta
    return INPUTS_DIR


def selecionar_arquivo(titulo, pasta_inicial):
    return filedialog.askopenfilename(
        parent=root,
        title=titulo,
        initialdir=str(pasta_inicial),
        filetypes=[("Arquivos Excel", "*.xlsx")],
    )


def caminho_curto(caminho):
    if not caminho:
        return "Nenhum arquivo selecionado"
    caminho = Path(caminho)
    return f"{caminho.name}  ·  {caminho.parent.name}"


def abrir_resultado(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        messagebox.showwarning(
            "Arquivo não encontrado",
            f"O arquivo ainda não foi gerado:\n{caminho}",
            parent=root,
        )
        return
    try:
        os.startfile(str(caminho))
    except AttributeError:
        subprocess.call(["open", str(caminho)])


# ─────────────────────────────────────────────
#  HELPERS DE LAYOUT COMPARTILHADOS
# ─────────────────────────────────────────────

def _criar_painel_central(width=860, height=540):
    painel = ctk.CTkFrame(
        root,
        width=width,
        height=height,
        corner_radius=10,
        fg_color="#101827",
        border_width=1,
        border_color="#1F2937",
    )
    painel.place(relx=0.5, rely=0.5, anchor="center")
    painel.grid_propagate(False)
    painel.grid_columnconfigure(0, weight=1)
    return painel


def _criar_header(painel, row=0):
    header = ctk.CTkFrame(painel, fg_color="transparent")
    header.grid(row=row, column=0, sticky="ew", padx=36, pady=(26, 0))
    header.grid_columnconfigure(1, weight=1)

    icon_frame = ctk.CTkFrame(
        header, width=38, height=38, corner_radius=8, fg_color="#0B1955"
    )
    icon_frame.grid(row=0, column=0, rowspan=2)
    icon_frame.grid_propagate(False)
    ctk.CTkLabel(
        icon_frame, text="✦", font=("Segoe UI", 16, "bold"), text_color="#FFFFFF"
    ).place(relx=0.5, rely=0.5, anchor="center")

    nome_frame = ctk.CTkFrame(header, fg_color="transparent")
    nome_frame.grid(row=0, column=1, sticky="w", padx=(12, 0))
    ctk.CTkLabel(
        nome_frame, text=APP_NAME, font=("Segoe UI", 15, "bold"), text_color="#F9FAFB"
    ).pack(side="left")
    #ctk.CTkLabel(
    #    nome_frame, text="  Conciliação EBTA", font=("Segoe UI", 11), text_color="#ffffff"
    #).pack(side="left")

    ctk.CTkLabel(
        header,
        text="v1.0",
        font=("Segoe UI", 10),
        text_color="#ffffff",
        fg_color="#1E293B",
        corner_radius=20,
        padx=10,
        pady=3,
    ).grid(row=0, column=2)

    ctk.CTkFrame(painel, height=1, fg_color="#1F2937").grid(
        row=row + 1, column=0, sticky="ew", padx=0, pady=(14, 0)
    )
    return row + 2


def _criar_indicador_passos(painel, passo_atual, row):
    frame = ctk.CTkFrame(painel, fg_color="transparent")
    frame.grid(row=row, column=0, sticky="w", padx=36, pady=(18, 4))

    cor_ativo   = "#5DCAA5" # #5DCAA5
    cor_feito   = "#1D9E75"
    cor_inativo = "#374151"

    def _passo(parent, numero, texto, estado):
        f = ctk.CTkFrame(parent, fg_color="transparent")

        if estado == "feito":
            cor_num = "#FFFFFF"
            bg_num  = cor_feito
            cor_txt = cor_feito
        elif estado == "ativo":
            cor_num = cor_ativo
            bg_num  = "transparent"
            cor_txt = cor_ativo
        else:
            cor_num = cor_inativo
            bg_num  = "transparent"
            cor_txt = cor_inativo

        circulo = ctk.CTkFrame(
            f,
            width=22,
            height=22,
            corner_radius=11,
            fg_color=bg_num,
            border_width=1,
            border_color=cor_num if estado != "feito" else cor_feito,
        )
        circulo.pack(side="left")
        circulo.pack_propagate(False)
        ctk.CTkLabel(
            circulo,
            text="✓" if estado == "feito" else str(numero),
            font=("Segoe UI", 10, "bold"),
            text_color=cor_num,
        ).pack(expand=True, anchor="center")

        ctk.CTkLabel(
            f, text=f"  {texto}", font=("Segoe UI", 12), text_color=cor_txt
        ).pack(side="left")

        return f

    estado1 = "feito" if passo_atual == 2 else "ativo"
    estado2 = "ativo" if passo_atual == 2 else "inativo"

    _passo(frame, 1, "Arquivos", estado1).pack(side="left")
    ctk.CTkFrame(frame, width=40, height=1, fg_color="#1F2937").pack(side="left", padx=10)
    _passo(frame, 2, "Confirmar", estado2).pack(side="left")

    return row + 1


# ─────────────────────────────────────────────
#  PASSO 1 — SELEÇÃO DE ARQUIVOS
# ─────────────────────────────────────────────

def mostrar_menu():
    limpar_tela()
    configurar_janela_ampla()
    criar_background()

    if arquivos_selecionados["pendencias"] is None:
        arquivos_selecionados["pendencias"] = buscar_arquivo_pendencias()
    if arquivos_selecionados["emails"] is None:
        arquivos_selecionados["emails"] = buscar_arquivo_emails()

    painel = _criar_painel_central(width=860, height=560)
    row    = _criar_header(painel, row=0)
    row    = _criar_indicador_passos(painel, passo_atual=1, row=row)

    ctk.CTkLabel(
        painel,
        text="SELECIONAR ARQUIVOS",
        font=("Courier New", 10),
        text_color="#4B5563",
    ).grid(row=row, column=0, sticky="w", padx=36, pady=(16, 8))
    row += 1

    area = ctk.CTkFrame(painel, fg_color="transparent")
    area.grid(row=row, column=0, sticky="ew", padx=36)
    area.grid_columnconfigure(0, weight=1)
    row += 1
 
    labels_caminho = {}

    def _criar_linha_arquivo(parent, r, titulo_linha, chave, comando):
        linha = ctk.CTkFrame(
            parent,
            height=76,
            corner_radius=8,
            fg_color="#111827",
            border_width=1,
            border_color="#1F2937",
        )
        linha.grid(row=r, column=0, sticky="ew", pady=(0, 10))
        linha.grid_propagate(False)
        linha.grid_columnconfigure(1, weight=1)

        icone = ctk.CTkFrame(
            linha, width=42, height=42, corner_radius=7, fg_color="#1E293B"
        )
        icone.grid(row=0, column=0, rowspan=2, padx=(18, 12), pady=15)

        ctk.CTkLabel(
            icone,
            text="📋" if chave == "pendencias" else "📩",
            font=("Segoe UI", 20),
            #text_color="#5DCAA5",
            height=42,
            width=42
        ).pack()

        ctk.CTkLabel(
            linha,
            text=titulo_linha,
            font=("Segoe UI", 13, "bold"),
            text_color="#E5E7EB",
            anchor="w",
        ).grid(row=0, column=1, sticky="sw", pady=(14, 0))

        lbl_caminho = ctk.CTkLabel(
            linha, text="", font=("Segoe UI", 11), text_color="#4B5563", anchor="w"
        )
        lbl_caminho.grid(row=1, column=1, sticky="nw", pady=(0, 14))
        labels_caminho[chave] = lbl_caminho

        # botões de seleção do arquivo
        ctk.CTkButton(
            linha,
            text="Selecionar",
            width=110,
            height=32,
            corner_radius=6,
            fg_color="#1E293B",         # Fundo normal
            hover_color="#2D3F55",      # Fundo ao passar o mouse
            border_width=1,               
            border_color="#334155",     # borda
            text_color="#94A3B8",       # texto
            font=("Segoe UI", 12),
            command=comando,
        ).grid(row=0, column=2, rowspan=2, padx=(12, 18))

    status_frame = ctk.CTkFrame(painel, fg_color="transparent")
    status_frame.grid(row=row + 1, column=0, pady=(6, 4))
    status_dot = ctk.CTkLabel(
        status_frame, text="●", font=("Segoe UI", 9), text_color="#374151"
    )
    status_dot.pack(side="left", padx=(0, 6))
    status_label = ctk.CTkLabel(
        status_frame, text="", font=("Segoe UI", 11), text_color="#4B5563" # altera texto -> Pronto para continuar que fica ao iniciar o menu
    )
    status_label.pack(side="left")

    btn_continuar = ctk.CTkButton(
        painel,
        text="Continuar  →",
        width=260,
        height=46,
        corner_radius=8,
        fg_color="#1D9E75",
        hover_color="#178A65",
        text_color="#FFFFFF",
        font=("Segoe UI", 14, "bold"),
    )

    def atualizar_estado():
        for chave, lbl in labels_caminho.items():
            caminho = arquivos_selecionados[chave]
            if caminho:
                lbl.configure(text=caminho_curto(caminho), text_color="#F9F9F9")
                lbl.master.configure(border_color="#64748B") # #2E7D54
            else:
                lbl.configure(text="nenhum arquivo selecionado", text_color="#4B5563")
                lbl.master.configure(border_color="#1F2937")

        pronto = bool(arquivos_selecionados["pendencias"] and arquivos_selecionados["emails"])
        btn_continuar.configure(state="normal" if pronto else "disabled")
        if pronto:
            status_dot.configure(text_color="#9CA3AF")
            status_label.configure(text="pronto para continuar", text_color="#9CA3AF")
        else:
            status_dot.configure(text_color="#374151")
            status_label.configure(
                text="selecione os dois arquivos para continuar", text_color="#4B5563"
            )

    def selecionar_pendencias():
        arquivo = selecionar_arquivo(
            "Selecione o arquivo de pendências", primeira_pasta_inputs("casos")
        )
        if arquivo:
            arquivos_selecionados["pendencias"] = Path(arquivo)
            atualizar_estado()

    _criar_linha_arquivo(area, 0, "Arquivo de pendências", "pendencias", selecionar_pendencias)
  
    ctk.CTkFrame(painel, height=1, fg_color="#1F2937").grid(
        row=row, column=0, sticky="ew", padx=0, pady=(4, 0)
    )
    row += 1
    row += 2  # pula status_frame já posicionado em row+1

    toggle_frame = ctk.CTkFrame(painel, fg_color="transparent")
    toggle_frame.grid(row=row, column=0, sticky="w", padx=36, pady=(0, 4))
    row += 1

    ctk.CTkSwitch(
        toggle_frame,
        text="Enviar e-mail ao final",
        variable=enviar_email_var,
        onvalue=True,
        offvalue=False,
        progress_color="#1D9E75",
        button_color="#FFFFFF",
        button_hover_color="#E5E7EB",
        text_color="#9CA3AF",
        font=("Segoe UI", 13),
    ).pack(side="left")

    def ir_para_confirmacao():
        mostrar_confirmacao(enviar_email_var.get())

    btn_continuar.configure(command=ir_para_confirmacao)
    btn_continuar.grid(row=row, column=0, pady=(10, 28))

    atualizar_estado()


# ─────────────────────────────────────────────
#  PASSO 2 — CONFIRMAÇÃO
# ─────────────────────────────────────────────

def mostrar_confirmacao(enviar_email: bool):
    limpar_tela()
    configurar_janela_ampla()
    criar_background()

    painel = _criar_painel_central(width=860, height=520)
    row    = _criar_header(painel, row=0)
    row    = _criar_indicador_passos(painel, passo_atual=2, row=row)

    ctk.CTkLabel(
        painel,
        text="Confirmar execução",
        font=("Segoe UI", 20, "bold"),
        text_color="#F9FAFB",
    ).grid(row=row, column=0, sticky="w", padx=36, pady=(20, 2))
    row += 1

    ctk.CTkLabel(
        painel,
        text="Revise os arquivos antes de iniciar a conciliação.",
        font=("Segoe UI", 12),
        text_color="#6B7280",
    ).grid(row=row, column=0, sticky="w", padx=36, pady=(0, 16))
    row += 1

    cards_frame = ctk.CTkFrame(painel, fg_color="transparent")
    cards_frame.grid(row=row, column=0, sticky="ew", padx=36)
    cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
    row += 1

    def _card_resumo(parent, col, label, valor, cor_valor="#D1D5DB"):
        card = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color="#111827",
            border_width=1,
            border_color="#1F2937",
        )
        card.grid(row=0, column=col, sticky="ew", padx=(0, 10) if col < 2 else 0)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=label, font=("Courier New", 10), text_color="#4B5563"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            card,
            text=valor,
            font=("Segoe UI", 12),
            text_color=cor_valor,
            wraplength=200,
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))

    pend_path  = arquivos_selecionados["pendencias"]
    email_path = arquivos_selecionados["emails"]

    _card_resumo(cards_frame, 0, "PENDÊNCIAS",  Path(pend_path).name  if pend_path  else "—", "#D1D5DB")
    _card_resumo(cards_frame, 1, "BASE E-MAILS", Path(email_path).name if email_path else "—", "#D1D5DB")
    _card_resumo(
        cards_frame, 2, "ENVIO E-MAIL",
        "ativado" if enviar_email else "desativado",
        "#5DCAA5" if enviar_email else "#4B5563",
    )

    if enviar_email:
        aviso = ctk.CTkFrame(
            painel, corner_radius=7, fg_color="#0F2A1E", border_width=1, border_color="#2E7D54"
        )
        aviso.grid(row=row, column=0, sticky="ew", padx=36, pady=(14, 0))
        aviso.grid_columnconfigure(1, weight=1)
        row += 1
        ctk.CTkLabel(aviso, text="✉", font=("Segoe UI", 14), text_color="#5DCAA5").grid(
            row=0, column=0, padx=(14, 8), pady=10
        )
        ctk.CTkLabel(
            aviso,
            text="E-mail será enviado para operação ao término do processamento. Casos urgentes com o fechamento abaixo ou igual a 1 dia também notificam a diretoria.",
            font=("Segoe UI", 11),
            text_color="#5DCAA5",
            wraplength=640,
            justify="left",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=10, padx=(0, 14))
    else:
        row += 1

    btns = ctk.CTkFrame(painel, fg_color="transparent")
    btns.grid(row=row, column=0, pady=(20, 28))

    def executar_conciliacao():
        input_pendencias = arquivos_selecionados["pendencias"]
        input_emails     = arquivos_selecionados["emails"]

        if not input_pendencias or not input_emails:
            messagebox.showerror(
                "Erro", "Selecione os dois arquivos antes de executar.", parent=root
            )
            return

        controle = {"cancelar": False}

        # ── Popup de confirmação de e-mail ──────────────────────────────
        popup = ctk.CTkToplevel(root)
        popup.title("Confirmar envio de e-mail")
        popup.resizable(False, False)
        popup.grab_set()

        largura, altura = 420, 210
        popup.update_idletasks()
        x = root.winfo_x() + (root.winfo_width()  - largura) // 2
        y = root.winfo_y() + (root.winfo_height() - altura)  // 2
        popup.geometry(f"{largura}x{altura}+{x}+{y}")
        popup.configure(fg_color="#101827")

        estado_email = {"confirmado": None}  # None = popup fechado sem decisão

        if enviar_email:
            icone_txt = "✉"
            titulo_txt = "Enviar e-mail ao final?"
            descricao_txt = "O envio de e-mail está ativado.\nDeseja confirmar o envio ao término da conciliação?"
            texto_sim = "Sim, enviar  ✉"
            texto_nao = "Não enviar"
        else:
            icone_txt = "🔕"
            titulo_txt = "E-mail desativado"
            descricao_txt = "O envio de e-mail está desativado.\nDeseja ativar o envio ao término da conciliação?"
            texto_sim = "Não, continuar sem enviar"
            texto_nao = "Ativar e enviar  ✉"

        ctk.CTkLabel(
            popup, text=icone_txt, font=("Segoe UI", 28)
        ).pack(pady=(22, 4))

        ctk.CTkLabel(
            popup, text=titulo_txt, font=("Segoe UI", 14, "bold"), text_color="#F9FAFB"
        ).pack()

        ctk.CTkLabel(
            popup, text=descricao_txt, font=("Segoe UI", 11),
            text_color="#6B7280", justify="center"
        ).pack(pady=(4, 16))

        btns_popup = ctk.CTkFrame(popup, fg_color="transparent")
        btns_popup.pack()

        def ao_confirmar():
            # mantém a intenção original
            estado_email["confirmado"] = enviar_email
            enviar_email_var.set(enviar_email)
            popup.destroy()

        def ao_inverter():
            # inverte a decisão
            novo = not enviar_email
            estado_email["confirmado"] = novo
            enviar_email_var.set(novo)
            popup.destroy()

        # Botão secundário (Não enviar) — vem primeiro no pack = fica à esquerda
        ctk.CTkButton(
            btns_popup, text=texto_nao, width=160, height=36, corner_radius=7,
            fg_color="transparent",
            hover_color="#1F2937",
            border_width=1,
            border_color="#334155",
            text_color="#9CA3AF",
            font=("Segoe UI", 12), command=ao_inverter,
        ).pack(side="left", padx=(0, 10))

        # Botão principal (Sim, enviar) — vem depois no pack = fica à direita, agora verde
        ctk.CTkButton(
            btns_popup, text=texto_sim, width=160, height=36, corner_radius=7,
            fg_color="#1D9E75",
            hover_color="#178A65",
            text_color="#FFFFFF",
            font=("Segoe UI", 12, "bold"), command=ao_confirmar,
        ).pack(side="left")

        popup.wait_window()

        # Se o popup foi fechado sem escolha (X), aborta execução
        if estado_email["confirmado"] is None:
            return

        enviar_definitivo = estado_email["confirmado"]
        # ────────────────────────────────────────────────────────────────

        controle = {"cancelar": False}

        tela_processamento(
            root=root,
            funcao_processamento=lambda atualiza_status: src.main.main(
                input_pendencias,
                input_emails,
                enviar_email,
                atualiza_status,
                controle,
            ),
            mostrar_menu_fn=mostrar_menu,
            abrir_resultado_fn=abrir_resultado,
            config=config,
            base_path=BASE_PATH,
        )

    ctk.CTkButton(
        btns,
        text="← Voltar",
        width=130,
        height=46,
        corner_radius=8,
        fg_color="transparent",
        hover_color="#1F2937",
        border_width=1,
        border_color="#2E4A3A",
        text_color="#6B7280",
        font=("Segoe UI", 13),
        command=mostrar_menu,
    ).pack(side="left", padx=(0, 12))

    ctk.CTkButton(
        btns,
        text="Executar conciliação  ▶",
        width=240,
        height=46,
        corner_radius=8,
        fg_color="#1D9E75",
        hover_color="#178A65",
        text_color="#FFFFFF",
        font=("Segoe UI", 14, "bold"),
        command=executar_conciliacao,
    ).pack(side="left")


# ─────────────────────────────────────────────
#  ENTRADA
# ─────────────────────────────────────────────

def iniciar_processo():
    mostrar_menu()


if __name__ == "__main__":
    root.after(0, iniciar_processo)
    root.mainloop()