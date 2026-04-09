import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import threading
from tkinter import messagebox
from tkinter import filedialog
from src.main import main
import traceback
import os
import subprocess

# ==============================
# ROOT (uma única instância)
# ==============================
root = tk.Tk()
root.withdraw()


#==============================================
#🔧 1. SELEÇÃO DE ARQUIVOS
#==============================================
def selecionar_arquivo(titulo):
    return filedialog.askopenfilename(
        title=titulo,
        filetypes=[("Excel", "*.xlsx")]
    )

def iniciar_processo():
    input1 = selecionar_arquivo("Selecione o arquivo de pendências")
    input2 = selecionar_arquivo("Selecione a base de clientes")

    if not input1 or not input2:
        messagebox.showerror("Erro", "Selecione ambos os arquivos")
        return

    enviar_email = perguntar_envio_email()
    tela_processamento(lambda atualiza_status: main(input1, input2, enviar_email, atualiza_status))

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
    caminho = os.path.join("outputs", "Corretos", "Conciliados.xlsx")

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
    root.deiconify()
    root.title("")

    ctk.set_appearance_mode("light")
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
    root.configure(bg="#F5F6FA")

    root.attributes("-alpha", 0.0)

    def fade_in(opacity=0.0):
        opacity += 0.03
        if opacity <= 1:
            root.attributes("-alpha", opacity)
            root.after(2, fade_in, opacity)

    fade_in()
    
    # Inicia ajustes no container
    container = ctk.CTkFrame(root, fg_color="#F5F6FA")
    container.pack(expand=True, fill="both")

    # Titulo do Processamento
    title = ctk.CTkLabel(
        container,
        text="Processamento EBTA",
        font=("Calibri", 16, "bold"),
        fg_color="#F5F6FA"
    )
    title.pack(pady=(20,10))
    
    # Subtitulo do processamento
    label = ctk.CTkLabel(
        container,
        text="Preparando...",
        font=("Calibri", 14, "bold")
    )
    label.pack(pady=10)

    # Barra de progresso
    progress = ctk.CTkProgressBar(
        container,
        width=300,
        height=12,
        corner_radius=4,
        progress_color="#2ECC71"
    )

    progress.set(0)
    progress.pack(pady=10)

    progress.configure(mode="indeterminate")
    progress.start()

    # Percentual de carregamento
    percent_label = ctk.CTkLabel(
        container,
        text="0%",
        font=("Calibri", 12, "bold")
    )

    percent_label.pack(pady=(0,10))

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
# CRIA CRIA ANIMAÇÃO NA EVOLUÇÃO DO PERCENTUAL
#==============================================

    current_progress = 0
    target_progress = 0

    def animar_progresso():
        nonlocal current_progress, target_progress

        diff = target_progress - current_progress

        if abs(diff) > 0.001:
            current_progress += diff * 0.1
            progress.set(current_progress)
            root.after(16, animar_progresso)
        else:
            current_progress = target_progress
            progress.set(current_progress)

#==============================================
# ✅ FUNÇÃO DE ATUALIZAÇÃO
#==============================================

    def atualiza_status(texto, progresso=None):
        def update():
            nonlocal target_progress

            label.configure(text=texto)

            if progresso is not None:
                progress.stop()
                progress.configure(mode="determinate")
                
                target_progress = progresso / 100
                animar_progresso()
                percent_label.configure(text=f"{progresso}%")

            root.update_idletasks()

        root.after(0,update)

#==============================================
# ✅ FUNÇÃO PARA RODAR O PROCESSO
#==============================================

    def rodar():
        try:
            funcao_processamento(atualiza_status)

            # Mostra sucesso 
            def mostrar_sucesso():
                animar_progresso(1)
                percent_label.configure(text="100%")

                label.configure(
                    text="✔ Processamento concluído",
                    text_color="#0C6832",
                    font=("Calibri", 12)
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