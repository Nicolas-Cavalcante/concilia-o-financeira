import tkinter as tk
from tkinter import ttk
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
    caminho = os.path.join("outputs", "Incorretos", "Pendências_EBTA.xlsx")

    try:
        os.startfile(caminho)
    except:
        subprocess.call(["open", caminho])

#==============================================
#🔧 3. POPUP DE PROCESSAMENTO DO CÓDIGO
#==============================================

# Configurações da janela de processamento
def tela_processamento(funcao_processamento):
    root.deiconify()
    root.title("Processamento Pendências EBTA")

    root.update_idletasks()  # garante medidas corretas
    root.resizable(False, False)
        # tamanho da janela
    largura = 420
    altura = 260

    # tamanho da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # posição central
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    # aplica na janela
    root.geometry(f"{largura}x{altura}+{x}+{y}")
    root.configure(bg="#F5F6FA")

    root.attributes("-alpha", 0.0)

    def fade_in(opacity=0.0):
        opacity += 0.05
        if opacity <= 1:
            root.attributes("-alpha", opacity)
            root.after(10, fade_in, opacity)

    fade_in()
    
    # Inicia ajustes no container
    container = tk.Frame(root, bg="#F5F6FA")
    container.pack(expand=True, fill="both")

    title = tk.Label(
        container,
        text="Processamento EBTA",
        font=("Segoe UI", 14, "bold"),
        bg="#F5F6FA"
    )
    title.pack(pady=(20,10))

    label = tk.Label(
        container,
        text="Preparando...",
        font=("Segoe UI", 11),
        bg="#F5F6FA"
    )
    label.pack(pady=10)

    style = ttk.Style()
    style.theme_use('default')

    style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor="#E0E0E0",
        background="#2ECC71",  # verde mais moderno
        thickness=12
    )

    progress = ttk.Progressbar(
        container,
        style="Custom.Horizontal.TProgressbar",
        mode="determinate",
        length=300,
        maximum=100
    )
    progress.pack(pady=10)

    percent_label = tk.Label(
        container,
        text="0%",
        font=("Segoe UI", 10, "bold"),
        fg="#020704",
        bg="#F5F6FA"
    )

# CRIA BOTÃO PARA ABRIR O ARQUIVO NO FINAL DO PROCESSAMENTO
    buttons_frame = tk.Frame(container, bg="#F5F6FA")

    btn_abrir = tk.Button(
        buttons_frame,
        text="Abrir arquivo de pendências",
        font=("Segoe UI", 10),
        bg="#2ECC71",
        fg="white",
        relief="flat",
        padx=15,
        pady=10,
        command=lambda: abrir_arquivo()
    )
# CRIA BOTÃO PARA FECHAR O ARQUIVO NO FINAL DO PROCESSAMENTO
    btn_fechar = tk.Button(
        buttons_frame,
        text="Fechar",
        font=("Segoe UI", 10),
        bg="#BDC3C7",
        relief="flat",
        padx=15,
        pady=10,
        command=root.destroy
    )

    btn_abrir.pack(side="left", padx=5)
    btn_fechar.pack(side="left", padx=5)

# CONFIGURA LABEL DE SUCESSO AO CONCLUIR O PROCESSAMENTO
    success_frame = tk.Frame(container, bg="#E8F8F0", bd=0)
    success_label = tk.Label(
        success_frame,
        text="✔ Processamento concluído",
        font=("Segoe UI", 12, "bold"),
        fg="#0C6832",
        bg="#F5F6FA",
        padx=10,
        pady=8
    )
    success_label.pack()
    percent_label.pack(pady=(0,10))

# ✅ FUNÇÃO DE ATUALIZAÇÃO
    def atualiza_status(texto, progresso=None):
        def update():
            label.config(text=texto)
            if progresso is not None:
                progress['value'] = progresso
                percent_label.config(text=f"{progresso}%")
            root.update_idletasks()
        root.after(0,update)

# ✅ FUNÇÃO PARA RODAR O PROCESSO
    def rodar():
        try:
            funcao_processamento(atualiza_status)

            # MOSTRA SUCESSO 
            def mostrar_sucesso():
                progress['value'] = 100
                percent_label.config(text="100%")
                label.config(text="Processamento finalizado")

                success_frame.pack(pady=(10,5))   # mostra o bloco verde
                buttons_frame.pack(pady=(5,10))   # mostra os botões

            root.after(0, mostrar_sucesso)

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