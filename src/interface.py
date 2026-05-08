import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import customtkinter as ctk
import threading
import traceback
import os
import subprocess
import sys
import src.main
from pathlib import Path
from PIL import Image, ImageOps, ImageTk

# ==============================
# ROOT (uma única instância)
# ==============================

root = ctk.CTk()
#root.configure(fg_color="black")

#==============================================
#🔧 1. SELEÇÃO DE ARQUIVOS
#==============================================

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

BASE_PATH = get_base_path()

#foto = tk.PhotoImage(file=str(BASE_PATH / "logo_fly_azul.png"))
#root.iconphoto(True, foto)

    #==============================================
    # BUSCA ARQUIVO EMAILS AUTOMÁTICAMENTE E ALOCA NA FUNÇÃO
    #==============================================

def busca_arquivo_emails():
    pasta = Path.cwd() / "inputs"

    if not pasta.exists():
        return None
    
    arquivos = list(pasta.glob("Base_emails.xlsx"))

    if not arquivos:
        return None

    if len(arquivos) > 1:
        messagebox.showwarning(
            "Atenção",
            "Mais de um arquivo de base de clientes encontrado. Selecione manualmente."
        )
        return None
    
    return arquivos[0]

    #==============================================
    # BUSCA ARQUIVO PENDENCIAS AUTOMÁTICAMENTE E ALOCA NA FUNÇÃO
    #==============================================

def busca_arquivo_pendencias():
    pasta = Path.cwd() / "inputs"

    if not pasta.exists():
        return None
    
    arquivos = list(pasta.glob("pendencias*.xlsx"))

    if not arquivos:
        return None

    if len(arquivos) > 1:
        messagebox.showwarning(
            "Atenção",
            "Mais de um arquivo de base de clientes encontrado. Selecione manualmente."
        )
        return None
    
    return arquivos[0]

    #==============================================
    # FAZ SELEÇÃO DE ARQUIVOS
    #==============================================

def selecionar_arquivo(titulo):
    return filedialog.askopenfilename(
        title=titulo,
        filetypes=[("Excel", "*.xlsx")]
    )

def iniciar_processo():
    input1 = selecionar_arquivo("Selecione o arquivo de pendências")

    input2 = busca_arquivo_emails()
    
    if not input2:
        input2 = selecionar_arquivo("Selecione a base de clientes")

    if not input1 or not input2:
        messagebox.showerror("Erro", "Selecione ambos os arquivos")
        return
    
    controle = {"cancelar": False}
    enviar_email = perguntar_envio_email()
    tela_processamento(
        lambda atualiza_status: src.main.main(input1, input2, enviar_email, atualiza_status, controle)
        )

#==============================================
#🔧 2. CONFIRMAÇÃO DE ENVIO DO E-MAIL
#==============================================

def perguntar_envio_email():
    return messagebox.askyesno(
        "Envio de Email",
        "Deseja enviar o email ao final do processamento?"
    )

#==============================================
#🔧 3. FUNÇÃO PARA ABRIR ARQUIVO PELA INTERFACE
#==============================================

def abrir_arquivo():
    caminho = Path.cwd() / "outputs" / "Corretos" / "Conciliados.xlsx"

    try:
        os.startfile(caminho)
    except:
        subprocess.call(["open", caminho])

def abrir_arquivo_nl():
    caminho_nl = Path.cwd() / "outputs" / "Incorretos" / "Pendências_EBTA.xlsx"

    try:
        os.startfile(caminho_nl)
    except:
        subprocess.call(["open", caminho_nl])

#==============================================
#🔧 3. POPUP DE PROCESSAMENTO DO CÓDIGO
#==============================================

BACKGROUND_IMG = None

def carregar_background():
    global BACKGROUND_IMG

    caminho_background = BASE_PATH / "fundo_fly.png"

    if not caminho_background.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_background}")

    img = Image.open(caminho_background).convert("RGBA")

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 120))
    img = Image.alpha_composite(img, overlay)

    BACKGROUND_IMG = img

carregar_background()

logo_img = None

def carregar_logo():
    global logo_img

    img = Image.open(BASE_PATH / "logo_fly_branca.png")

    logo_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=(140, 70)
    )

carregar_logo()

    #==============================================
    # Configurações da janela de processamento
    #==============================================

def tela_processamento(funcao_processamento):
    
    erro_ocorrido = False
    root.title("")
    root.configure(fg_color="#0E1322")

    # tamanho da janela
    largura = 420
    altura = 260
    
    # tamanho da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # posição central da tela
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    # aplica na janela
    root.geometry(f"{largura}x{altura}+{x}+{y}")
    root.resizable(False, False
                   )
    # 2. cria canvas já no tamanho correto
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)

    root.update()  # 👈 ESSENCIAL

    largura_real = canvas.winfo_width()
    altura_real = canvas.winfo_height()

    img = ImageOps.fit(BACKGROUND_IMG, (largura_real, altura_real), Image.LANCZOS)

    # 3. cria imagem
    bg_tk = ImageTk.PhotoImage(img)
    canvas.bg_tk = bg_tk

    canvas.create_image(
        0, 0,
        anchor="nw",
        image=bg_tk
    )

    #def fade_in(opacity=0.0):
    #    opacity += 0.03
    #    if opacity <= 1:
    #        root.attributes("-alpha", opacity)
    #        root.after(10, fade_in, opacity)

    #fade_in()
    
#==============================================
# INICIA AJUSTES NO CONTAINER
#==============================================

    #==============================================
    # CRIA FUNDO
    #==============================================

    #backgorund_label = ctk.CTkLabel(
    #    root,
    #    image=BACKGROUND_IMG,
    #    text=""
    #
    #backgorund_label.place(x=0, y=0, relwidth=1, relheight=1)
    #backgorund_label.lower()
    #root.deiconify()

    #==============================================
    # TORNA CONTAINER TRANSPARENTE
    #==============================================

    #container = ctk.CTkFrame(
    #    root,
    #    fg_color="#1F2A44"
    #)
    #container.place(relwidth=1, relheight=1)

    #==============================================
    # CONFIGURA PARAMETROS DA LOGO
    #==============================================

    label_logo = ctk.CTkLabel(
        root,
        image=logo_img,
        text="",
        fg_color="transparent"
    )
    label_logo.place(relx=0.5, rely=0.15, anchor="center")

    #==============================================
    # CONFIGURA TITULO DO CONTAINER
    #==============================================

    title = ctk.CTkLabel(
        root,
        text="SmartCheck",
        font=("Segoe UI", 16, "bold"),
        text_color="#FFFFFF",  # light, dark"
        fg_color="transparent"
    )
    title.place(relx=0.5, rely=0.35, anchor="center")
    
    texto_frame = ctk.CTkFrame(root, fg_color="transparent")
    texto_frame.place(relx=0.5, rely=0.45, anchor="center")

    #==============================================
    # CONFIGURA SUBTITULO DO CONTAINER
    #==============================================

    label = ctk.CTkLabel(
        texto_frame,
        text="Preparando",
        font=("Segoe UI", 13, "bold"),
        text_color="#D1D5DB",
        fg_color="transparent"
    )
    label.pack(side="left", padx=(0, 4))

    #==============================================
    # CONFIGURA PONTOS DINAMICOS
    #==============================================

    label_pontos = ctk.CTkLabel(
        texto_frame,
        text="",
        font=("Segoe UI", 16, "bold"),
        text_color="#51B772",  # verde igual barra
        fg_color="transparent"    
    )
    label_pontos.pack(side="left", padx=(6, 0))

    #==============================================
    # CONFIGURA BARRA DE PROGRESSO
    #==============================================

    progress = ctk.CTkProgressBar(
        root,
        width=300,
        height=12,
        corner_radius=4,
        progress_color="#2ECC71",
        fg_color="#2A2A2A" # fundo da barra
    )

    progress.set(0)
    progress.place(relx=0.5, rely=0.6, anchor="center")

    progress.configure(mode="indeterminate")
    progress.start()

    #==============================================
    # CONFIGURA PERCENTUAL DE CARREGAMENTO
    #==============================================

    percent_label = ctk.CTkLabel(
        root,
        text="0%",
        font=("Segoe UI", 12, "bold"),
        text_color="#EEEFF1",
        fg_color="transparent"
    )

    percent_label.place(relx=0.5, rely=0.68, anchor="center")

    #==============================================
    # CRIA BOTÃO PARA ABRIR O ARQUIVO NO FINAL DO PROCESSAMENTO
    #==============================================

    buttons_frame = ctk.CTkFrame(root, fg_color="transparent")

    btn_abrir = ctk.CTkButton(
        buttons_frame,
        text="Abrir Conciliados",
        width=180,
        height=35,
        corner_radius=5,
        fg_color="#BDC3C7",
        hover_color="#A6ACAF",  # 👈 hover automático
        text_color="black",
        command=lambda: abrir_arquivo()
    )

    #==============================================
    # CRIA BOTÃO PARA ABRIR O ARQUIVO PENDENCIAS NO FINAL DO PROCESSAMENTO
    #==============================================

    btn_abrir_nl = ctk.CTkButton(
        buttons_frame,
        text="Abrir Pendentes",
        width=180,
        height=35,
        corner_radius=5,
        fg_color="#BDC3C7",
        hover_color="#A6ACAF",
        text_color="black",
        command=lambda: abrir_arquivo_nl()
    )

    btn_abrir.pack(side="left", padx=8)
    btn_abrir_nl.pack(side="left", padx=8)

    #==============================================
    # CRIA LABEL PARA O FINAL DO PROCESSAMENTO
    #==============================================

    resultado_label = ctk.CTkLabel(
        root,
        text="",
        font=("Segoe UI", 12),
        text_color="#9CA3AF"
    )
    resultado_label.place(relx=0.5, rely=0.85, anchor="center")

#==============================================
# Configurações execução do processamento
#==============================================

    # Variaveis globais
    animar_id = 0
    animacao_ativa = True
    #==============================================
    # CRIA ANIMAÇÃO NA EVOLUÇÃO DO PROCESSAMENTO
    #==============================================
    
    def animar_pontos():
        frames = [
            "•  ",
            " • ",
            "  •",
            " • "
        ]
        idx = 0
        
        def loop():
            nonlocal idx

            if not animacao_ativa:
                label_pontos.configure(text="")  # limpa
                return

            try:
                label_pontos.configure(text=frames[idx])
            except:
                return

            idx = (idx + 1) % len(frames)
            root.after(200, loop)

        loop()
        
    animar_pontos()

    #==============================================
    # CRIA ANIMAÇÃO NA EVOLUÇÃO DO PERCENTUAL
    #==============================================

    current_progress = 0
    target_progress = 0

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

    #==============================================
    # CRIA FUNÇÃO PARA TRATAR ERROS
    #==============================================

    def tratar_erro_ui(e):
        nonlocal erro_ocorrido
        erro_ocorrido=True

        try:
            progress.stop()
        except:
            pass

        # atualiza UI
        label.configure(
            text="❌ Erro no processamento",
            text_color="red"
        )

        percent_label.configure(text="Erro")

        # mostra popup
        messagebox.showerror("Erro", str(e))

        # opcional: fecha depois
        root.after(3000, root.destroy)

    #==============================================
    # ✅ FUNÇÃO DE ATUALIZAÇÃO
    #==============================================

    def atualiza_status(texto, progresso=None):
        def update():
            
            nonlocal target_progress

            if erro_ocorrido:
                return
            
            try:
                texto_limpo = texto.rstrip(".")
                label.configure(text=texto_limpo)

                if progresso is not None:
                    progress.stop()
                    progress.configure(mode="determinate")

                    target_progress = progresso / 100
                    animar_progresso()
                    
                    percent_label.configure(text=f"{progresso}%")

                root.update_idletasks()

            except Exception as e:
                tratar_erro_ui(e)

        root.after(0, update)

    #==============================================
    # ✅ FUNÇÃO PARA RODAR O PROCESSO
    #==============================================

    def rodar():
        try:
            resultado = funcao_processamento(atualiza_status)
            percentual_ok, percentual_pendente = resultado

            # Mostra sucesso 
            def mostrar_sucesso():
                nonlocal target_progress, animacao_ativa

                animacao_ativa = False # Define como false para não subir os pontos ao final do processamento
                target_progress = 1
                animar_progresso()
                percent_label.configure(text="100%")

                label.configure(
                    text="✔ Processamento concluído",
                    text_color="#19AA55",
                    font=("Segoe UI", 14)
                )

                resultado_label.configure(
                    text=f"{percentual_ok}¨% Conciliados | {percentual_pendente}% Pendentes",
                    text_color="#FFFFFF"
                )

                resultado_label.place(relx=0.5, rely=0.76, anchor="center")

                buttons_frame.place(relx=0.5, rely=0.9, anchor="center")

            root.after(0, mostrar_sucesso)
        
        # Exceção para mostrar erro em caso de arquivos abertos ao iniciar o processamento
        except PermissionError:
            root.after(0, lambda: messagebox.showerror(
                "⚠️ Arquivo em uso",
                "O arquivo está aberto. Feche o excel e rode novamente."
            ))
            root.after(3000, root.destroy)

        except Exception as e:
            erro = str(e)

            print(traceback.format_exc())
            root.after(0, lambda: messagebox.showerror("Erro", erro))

            root.after(10000, root.destroy)

    label.configure(text="Iniciando processo...")
    percent_label.configure(text="0%")

    root.after(50, lambda: threading.Thread(target=rodar, daemon=True).start())

# ==============================
# 4. EXECUÇÃO
# ==============================
if __name__ == "__main__":
    root.after(0, iniciar_processo)
    root.mainloop()