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


APP_NAME = "SmartCheck"
WINDOW_TITLE = "SmartCheck - Conciliação EBTA"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()


def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_exec_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


BASE_PATH = get_base_path()
EXEC_DIR = get_exec_dir()
INPUTS_DIR = EXEC_DIR / "inputs"

arquivos_selecionados = {
    "pendencias": None,
    "emails": None,
}


def carregar_background():
    caminho_background = BASE_PATH / "fundo_fly.png"

    if not caminho_background.exists():
        img = Image.new("RGBA", (1600, 900), "#0E1322")
    else:
        img = Image.open(caminho_background).convert("RGBA")

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 145))
    return Image.alpha_composite(img, overlay)


def carregar_logo():
    caminho_logo = BASE_PATH / "logo_fly_branca.png"

    if not caminho_logo.exists():
        return None

    img = Image.open(caminho_logo)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(150, 74))


BACKGROUND_IMG = carregar_background()
LOGO_IMG = carregar_logo()


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
        altura = int(root.winfo_screenheight() * 0.88)
        x = (root.winfo_screenwidth() - largura) // 2
        y = (root.winfo_screenheight() - altura) // 2
        root.geometry(f"{largura}x{altura}+{x}+{y}")


def criar_background():
    canvas = tk.Canvas(root, highlightthickness=0, bd=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def redesenhar(event=None):
        largura = max(canvas.winfo_width(), 1)
        altura = max(canvas.winfo_height(), 1)
        img = ImageOps.fit(BACKGROUND_IMG, (largura, altura), Image.LANCZOS)
        bg_tk = ImageTk.PhotoImage(img)
        canvas.bg_tk = bg_tk
        canvas.delete("background")
        canvas.create_image(0, 0, anchor="nw", image=bg_tk, tags="background")

    canvas.bind("<Configure>", redesenhar)
    root.after(0, redesenhar)
    return canvas


def buscar_arquivo_emails():
    if not INPUTS_DIR.exists():
        return None

    arquivos = [
        arquivo
        for arquivo in INPUTS_DIR.rglob("*.xlsx")
        if arquivo.name.lower() == "base_emails.xlsx"
    ]

    return arquivos[0] if len(arquivos) == 1 else None


def buscar_arquivo_pendencias():
    if not INPUTS_DIR.exists():
        return None

    arquivos = [
        arquivo
        for arquivo in INPUTS_DIR.rglob("*.xlsx")
        if arquivo.name.lower().startswith("pendencias")
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
    return f"{caminho.name}  |  {caminho.parent.name}"


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


def mostrar_menu():
    limpar_tela()
    configurar_janela_ampla()
    criar_background()

    if arquivos_selecionados["pendencias"] is None:
        arquivos_selecionados["pendencias"] = buscar_arquivo_pendencias()

    if arquivos_selecionados["emails"] is None:
        arquivos_selecionados["emails"] = buscar_arquivo_emails()

    painel = ctk.CTkFrame(root, width=900, height=520, corner_radius=8, fg_color="#101827")
    painel.place(relx=0.5, rely=0.5, anchor="center")
    painel.grid_propagate(False)
    painel.grid_columnconfigure(0, weight=1)

    if LOGO_IMG:
        logo_label = ctk.CTkLabel(painel, image=LOGO_IMG, text="")
    else:
        logo_label = ctk.CTkLabel(
            painel,
            text=APP_NAME,
            font=("Segoe UI", 26, "bold"),
            text_color="#FFFFFF",
        )
    logo_label.grid(row=0, column=0, pady=(28, 4))

    titulo = ctk.CTkLabel(
        painel,
        text=APP_NAME,
        font=("Segoe UI", 30, "bold"),
        text_color="#FFFFFF",
    )
    titulo.grid(row=1, column=0)

    subtitulo = ctk.CTkLabel(
        painel,
        text="Conciliação EBTA",
        font=("Segoe UI", 15),
        text_color="#D1D5DB",
    )
    subtitulo.grid(row=2, column=0, pady=(0, 22))

    arquivos_frame = ctk.CTkFrame(painel, fg_color="transparent")
    arquivos_frame.grid(row=3, column=0, sticky="ew", padx=46)
    arquivos_frame.grid_columnconfigure(0, weight=1)

    labels_caminho = {}

    def criar_linha_arquivo(row, titulo_linha, chave, texto_botao, comando):
        linha = ctk.CTkFrame(arquivos_frame, height=86, corner_radius=6, fg_color="#182235")
        linha.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        linha.grid_propagate(False)
        linha.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            linha,
            text=titulo_linha,
            font=("Segoe UI", 15, "bold"),
            text_color="#FFFFFF",
        ).grid(row=0, column=0, sticky="w", padx=(22, 16), pady=(16, 0))

        caminho_label = ctk.CTkLabel(
            linha,
            text="",
            font=("Segoe UI", 12),
            text_color="#B7C0D0",
            anchor="w",
        )
        caminho_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=22, pady=(4, 0))

        ctk.CTkButton(
            linha,
            text=texto_botao,
            width=150,
            height=36,
            corner_radius=5,
            fg_color="#2E7D54",
            hover_color="#256A47",
            command=comando,
        ).grid(row=0, column=2, rowspan=2, padx=(16, 22), pady=20)

        labels_caminho[chave] = caminho_label

    enviar_email_var = tk.BooleanVar(value=False)
    status_label = ctk.CTkLabel(
        painel,
        text="",
        font=("Segoe UI", 12, "bold"),
        text_color="#B7C0D0",
    )

    btn_executar = ctk.CTkButton(
        painel,
        text="Executar conciliação",
        width=260,
        height=46,
        corner_radius=5,
        fg_color="#19AA55",
        hover_color="#148844",
        text_color="#FFFFFF",
        font=("Segoe UI", 15, "bold"),
    )

    def atualizar_estado():
        for chave, label in labels_caminho.items():
            caminho = arquivos_selecionados[chave]
            if caminho:
                label.configure(text=caminho_curto(caminho), text_color="#D7DEE9")
            else:
                label.configure(text="Nenhum arquivo selecionado", text_color="#9CA3AF")

        pronto = bool(arquivos_selecionados["pendencias"] and arquivos_selecionados["emails"])
        btn_executar.configure(state="normal" if pronto else "disabled")
        status_label.configure(
            text="Pronto para iniciar" if pronto else "Selecione os arquivos para continuar",
            text_color="#9BE0B5" if pronto else "#B7C0D0",
        )

    def selecionar_pendencias():
        arquivo = selecionar_arquivo(
            "Selecione o arquivo de pendências",
            primeira_pasta_inputs("casos"),
        )

        if arquivo:
            arquivos_selecionados["pendencias"] = Path(arquivo)
            atualizar_estado()

    def selecionar_emails():
        arquivo = selecionar_arquivo(
            "Selecione a base de e-mails",
            primeira_pasta_inputs("base"),
        )

        if arquivo:
            arquivos_selecionados["emails"] = Path(arquivo)
            atualizar_estado()

    def executar_conciliacao():
        input_pendencias = arquivos_selecionados["pendencias"]
        input_emails = arquivos_selecionados["emails"]

        if not input_pendencias or not input_emails:
            messagebox.showerror("Erro", "Selecione os dois arquivos antes de executar.", parent=root)
            return

        controle = {"cancelar": False}
        enviar_email = enviar_email_var.get()
        tela_processamento(
            lambda atualiza_status: src.main.main(
                input_pendencias,
                input_emails,
                enviar_email,
                atualiza_status,
                controle,
            )
        )

    btn_executar.configure(command=executar_conciliacao)

    criar_linha_arquivo(
        0,
        "Arquivo de pendências",
        "pendencias",
        "Selecionar",
        selecionar_pendencias,
    )
    criar_linha_arquivo(
        1,
        "Base de e-mails",
        "emails",
        "Selecionar",
        selecionar_emails,
    )

    opcoes_frame = ctk.CTkFrame(painel, fg_color="transparent")
    opcoes_frame.grid(row=4, column=0, sticky="ew", padx=46, pady=(0, 8))
    opcoes_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkSwitch(
        opcoes_frame,
        text="Enviar e-mail ao final",
        variable=enviar_email_var,
        onvalue=True,
        offvalue=False,
        progress_color="#19AA55",
        button_color="#FFFFFF",
        button_hover_color="#E5E7EB",
        text_color="#D1D5DB",
        font=("Segoe UI", 13),
    ).grid(row=0, column=0, sticky="w")

    status_label.grid(row=5, column=0, pady=(6, 8))
    btn_executar.grid(row=6, column=0, pady=(0, 28))

    atualizar_estado()


def tela_processamento(funcao_processamento):
    limpar_tela()
    configurar_janela_ampla()
    criar_background()

    erro_ocorrido = False
    animacao_ativa = True

    painel = ctk.CTkFrame(root, width=720, height=430, corner_radius=8, fg_color="#101827")
    painel.place(relx=0.5, rely=0.5, anchor="center")
    painel.grid_propagate(False)
    painel.grid_columnconfigure(0, weight=1)

    if LOGO_IMG:
        ctk.CTkLabel(painel, image=LOGO_IMG, text="").grid(row=0, column=0, pady=(30, 4))

    title = ctk.CTkLabel(
        painel,
        text=APP_NAME,
        font=("Segoe UI", 24, "bold"),
        text_color="#FFFFFF",
    )
    title.grid(row=1, column=0)

    texto_frame = ctk.CTkFrame(painel, fg_color="transparent")
    texto_frame.grid(row=2, column=0, pady=(18, 6))

    label = ctk.CTkLabel(
        texto_frame,
        text="Iniciando processo",
        font=("Segoe UI", 15, "bold"),
        text_color="#D1D5DB",
        fg_color="transparent",
    )
    label.pack(side="left", padx=(0, 4))

    label_pontos = ctk.CTkLabel(
        texto_frame,
        text="",
        font=("Segoe UI", 15, "bold"),
        text_color="#51B772",
        fg_color="transparent",
    )
    label_pontos.pack(side="left", padx=(4, 0))

    progress = ctk.CTkProgressBar(
        painel,
        width=500,
        height=14,
        corner_radius=4,
        progress_color="#2ECC71",
        fg_color="#2A2A2A",
    )
    progress.set(0)
    progress.grid(row=3, column=0, pady=(18, 6))
    progress.configure(mode="indeterminate")
    progress.start()

    percent_label = ctk.CTkLabel(
        painel,
        text="0%",
        font=("Segoe UI", 13, "bold"),
        text_color="#EEEFF1",
        fg_color="transparent",
    )
    percent_label.grid(row=4, column=0, pady=(0, 18))

    resultado_label = ctk.CTkLabel(
        painel,
        text="",
        font=("Segoe UI", 13),
        text_color="#FFFFFF",
    )
    resultado_label.grid(row=5, column=0, pady=(0, 12))

    buttons_frame = ctk.CTkFrame(painel, fg_color="transparent")
    erro_frame = ctk.CTkFrame(painel, fg_color="transparent")

    ctk.CTkButton(
        buttons_frame,
        text="Abrir Conciliados",
        width=165,
        height=36,
        corner_radius=5,
        fg_color="#BDC3C7",
        hover_color="#A6ACAF",
        text_color="black",
        command=lambda: abrir_resultado(config.OUTPUT_CORRETOS / "Conciliados.xlsx"),
    ).pack(side="left", padx=7)

    ctk.CTkButton(
        buttons_frame,
        text="Abrir Pendentes",
        width=165,
        height=36,
        corner_radius=5,
        fg_color="#BDC3C7",
        hover_color="#A6ACAF",
        text_color="black",
        command=lambda: abrir_resultado(config.OUTPUT_INCORRETOS / "Pendências_EBTA.xlsx"),
    ).pack(side="left", padx=7)

    ctk.CTkButton(
        buttons_frame,
        text="Nova conciliação",
        width=165,
        height=36,
        corner_radius=5,
        fg_color="#2E7D54",
        hover_color="#256A47",
        text_color="#FFFFFF",
        command=mostrar_menu,
    ).pack(side="left", padx=7)

    ctk.CTkButton(
        erro_frame,
        text="Voltar ao menu",
        width=180,
        height=36,
        corner_radius=5,
        fg_color="#2E7D54",
        hover_color="#256A47",
        text_color="#FFFFFF",
        command=mostrar_menu,
    ).pack(side="left", padx=7)

    current_progress = 0
    target_progress = 0

    def animar_pontos():
        frames = [".  ", ".. ", "...", " .."]
        idx = 0

        def loop():
            nonlocal idx

            if not animacao_ativa:
                label_pontos.configure(text="")
                return

            try:
                label_pontos.configure(text=frames[idx])
            except tk.TclError:
                return

            idx = (idx + 1) % len(frames)
            root.after(250, loop)

        loop()

    def animar_progresso():
        nonlocal current_progress, target_progress

        diff = target_progress - current_progress

        if abs(diff) > 0.001:
            current_progress += diff * 0.07
            progress.set(current_progress)
            root.after(16, animar_progresso)
        else:
            current_progress = target_progress
            progress.set(current_progress)

    def exibir_erro(mensagem):
        nonlocal erro_ocorrido, animacao_ativa
        erro_ocorrido = True
        animacao_ativa = False

        try:
            progress.stop()
        except tk.TclError:
            pass

        label.configure(text="Erro no processamento", text_color="#EF4444")
        percent_label.configure(text="Erro")
        resultado_label.configure(text="Verifique os arquivos e tente novamente.", text_color="#FFFFFF")
        erro_frame.grid(row=6, column=0, pady=(4, 28))

        messagebox.showerror("Erro", mensagem, parent=root)

    def atualiza_status(texto, progresso=None):
        def update():
            nonlocal target_progress

            if erro_ocorrido:
                return

            try:
                texto_limpo = (texto or "").rstrip(".")
                if texto_limpo:
                    label.configure(text=texto_limpo, text_color="#D1D5DB")

                if progresso is not None:
                    progress.stop()
                    progress.configure(mode="determinate")
                    target_progress = progresso / 100
                    animar_progresso()
                    percent_label.configure(text=f"{progresso}%")

                root.update_idletasks()

            except tk.TclError as e:
                exibir_erro(str(e))

        root.after(0, update)

    def rodar():
        try:
            resultado = funcao_processamento(atualiza_status)

            if not resultado:
                raise RuntimeError("Processamento encerrado sem resultado.")

            percentual_ok, percentual_pendente = resultado

            def mostrar_sucesso():
                nonlocal target_progress, animacao_ativa

                animacao_ativa = False
                target_progress = 1
                animar_progresso()
                percent_label.configure(text="100%")

                label.configure(
                    text="Processamento concluído",
                    text_color="#19AA55",
                    font=("Segoe UI", 15, "bold"),
                )

                resultado_label.configure(
                    text=f"{percentual_ok}% Conciliados | {percentual_pendente}% Pendentes",
                    text_color="#FFFFFF",
                )

                buttons_frame.grid(row=6, column=0, pady=(4, 28))

            root.after(0, mostrar_sucesso)

        except PermissionError:
            root.after(
                0,
                lambda: exibir_erro("O arquivo está aberto. Feche o Excel e rode novamente."),
            )

        except Exception as e:
            print(traceback.format_exc())
            root.after(0, lambda: exibir_erro(str(e)))

    animar_pontos()
    root.after(50, lambda: threading.Thread(target=rodar, daemon=True).start())


def iniciar_processo():
    mostrar_menu()


if __name__ == "__main__":
    root.after(0, iniciar_processo)
    root.mainloop()
