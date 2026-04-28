import tkinter as tk
import customtkinter as ctk
import threading
import traceback
import os
import subprocess
import sys
from tkinter import messagebox
from tkinter import filedialog
import src.main
from pathlib import Path
from PIL import Image

# ==============================
# ROOT (uma única instância)
# ==============================
root = tk.Tk()
root.withdraw()


#==============================================
#🔧 1. SELEÇÃO DE ARQUIVOS
#==============================================

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

BASE_PATH = get_base_path()


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
    caminho = BASE_PATH / "outputs" / "Corretos" / "Conciliados.xlsx"

    try:
        os.startfile(caminho)
    except:
        subprocess.call(["open", caminho])

#==============================================
#🔧 3. POPUP DE PROCESSAMENTO DO CÓDIGO
#==============================================

    #==============================================
    # Configurações da janela de processamento
    #==============================================

def tela_processamento(funcao_processamento):

    erro_ocorrido = False
    root.deiconify()
    root.title("")

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root.update_idletasks()  # garante medidas corretas
    root.resizable(False, False)
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
  

    root.attributes("-alpha", 0.0)

    def fade_in(opacity=0.0):
        opacity += 0.03
        if opacity <= 1:
            root.attributes("-alpha", opacity)
            root.after(2, fade_in, opacity)

    fade_in()
    
    # Inicia ajustes no container
    container = ctk.CTkFrame(
        root,
        fg_color=("#FFFFFF", "#121212"), # light, dark
        corner_radius=6
        )
    container.pack(expand=True, fill="both")

    # Busca logo da empresa
    caminho_logo_fly_light = BASE_PATH / "logo_fly_branca.png"
    caminho_logo_fly_dark = BASE_PATH / "logo_fly_branca.png"

    # Define parametros da imagem
    logo_img = ctk.CTkImage(
        light_image=Image.open(caminho_logo_fly_light),
        dark_image=Image.open(caminho_logo_fly_dark),
        size=(140, 70)
    )

    label_logo = ctk.CTkLabel(
        container,
        image=logo_img,
        text=""
    )
    label_logo.pack(pady=(25, 5))

    # Titulo do Processamento
    title = ctk.CTkLabel(
        container,
        text="SmartCheck",
        font=("Segoe UI", 16, "bold"),
        text_color="#FFFFFF"  # light, dark"
    )
    title.pack(pady=(5, 6))
    
    texto_frame = ctk.CTkFrame(container, fg_color="transparent")
    texto_frame.pack(pady=(5, 14))

    spinner_label = ctk.CTkLabel(container, text="")
    spinner_label.pack(pady=(5, 10))

    # Subtitulo do processamento
    label = ctk.CTkLabel(
        texto_frame,
        text="Preparando",
        font=("Segoe UI", 13, "bold"),
        text_color="#D1D5DB"
    )
    label.pack(side="left", padx=(0, 4))

    label_pontos = ctk.CTkLabel(
        texto_frame,
        text="",
        font=("Segoe UI", 13, "bold"),
        text_color="#D1D5DB",
        width=30
    )
    label_pontos.pack(side="left")

    # Barra de progresso
    progress = ctk.CTkProgressBar(
        container,
        width=300,
        height=12,
        corner_radius=4,
        progress_color="#2ECC71",
        fg_color="#2A2A2A" # fundo da barra
    )

    progress.set(0)
    progress.pack(pady=(8, 6))

    progress.configure(mode="indeterminate")
    progress.start()

    # Percentual de carregamento
    percent_label = ctk.CTkLabel(
        container,
        text="0%",
        font=("Segoe UI", 12, "bold"),
        text_color="#9CA3AF"
    )

    percent_label.pack(pady=(0, 15))

    #==============================================
    # CRIA BOTÃO PARA ABRIR O ARQUIVO NO FINAL DO PROCESSAMENTO
    #==============================================

    buttons_frame = ctk.CTkFrame(container, fg_color="transparent")

    btn_abrir = ctk.CTkButton(
        buttons_frame,
        text="Abrir arquivo",
        width=180,
        height=35,
        corner_radius=5,
        fg_color="#50C480",
        hover_color="#287C4B",  # 👈 hover automático
        text_color="white",
        command=lambda: abrir_arquivo()
    )

    #==============================================
    # CRIA BOTÃO PARA FECHAR O ARQUIVO NO FINAL DO PROCESSAMENTO
    #==============================================

    btn_fechar = ctk.CTkButton(
        buttons_frame,
        text="Fechar",
        width=180,
        height=35,
        corner_radius=5,
        fg_color="#BDC3C7",
        hover_color="#A6ACAF",
        text_color="black",
        command=root.destroy
    )

    btn_abrir.pack(side="left", padx=8)
    btn_fechar.pack(side="left", padx=8)

    #==============================================
    # CRIA LABEL PARA O FINAL DO PROCESSAMENTO
    #==============================================

    resultado_label = ctk.CTkLabel(
        container,
        text="",
        font=("Segoe UI", 12),
        text_color="#9CA3AF"
    )
    resultado_label.pack(pady=(0, 10))

#==============================================
# Configurações execução do processamento
#==============================================

    # Variaveis globais
    animar_id = 0

    #==============================================
    # CRIA ANIMAÇÃO NA EVOLUÇÃO DO PROCESSAMENTO
    #==============================================
    def animar_spinner():
        frames = ["⟳", "⟲"]  # alterna sentido
        idx = 0
        meu_id = animar_id

        def loop():
            nonlocal idx
            
            try:
                label_pontos.configure(text=frames[idx])
            except:
                return

            idx = (idx + 1) % len(frames)
            root.after(500, loop)

        loop()

    animar_spinner()

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
            
            nonlocal target_progress, animar_id

            if erro_ocorrido:
                return
            
            try:
                texto_limpo = texto.rstrip(".")
                label.configure(text=texto_limpo)

                animar_id += 1

                if progresso is not None:
                    progress.stop()
                    progress.configure(mode="determinate")

                    target_progress = progresso / 100
                    animar_progresso()
                    
                    percent_label.configure(text=f"{progresso}%")

                root.update_idletasks()

            except Exception as e:
                tratar_erro_ui(e)

        root.after(0,update)

    #==============================================
    # ✅ FUNÇÃO PARA RODAR O PROCESSO
    #==============================================

    def rodar():
        try:
            resultado = funcao_processamento(atualiza_status)
            qtde_ok, qtde_erro = resultado

            # Mostra sucesso 
            def mostrar_sucesso():
                nonlocal target_progress

                target_progress = 1
                animar_progresso()
                percent_label.configure(text="100%")

                label.configure(
                    text="✔ Processamento concluído",
                    text_color="#0C6832",
                    font=("Segoe UI", 14)
                )

                resultado_label.configure(
                    text=f"{qtde_ok} Conciliados | {qtde_erro} Não Localizados"
                )

                buttons_frame.pack(pady=(10,10))

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

    threading.Thread(target=rodar, daemon=True).start()
    root.mainloop()

# ==============================
# 4. EXECUÇÃO
# ==============================
if __name__ == "__main__":
    iniciar_processo()