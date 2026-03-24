import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox

#==============================================
#🔧 1. POPUP DE CONFIRMAÇÃO DE ENVIO DO E-MAIL
#==============================================

def perguntar_envio_email():
    root = tk.Tk()
    root.withdraw()

    resposta = messagebox.askyesno(
        "Envio de Email",
        "Deseja enviar o email ao final do processamento?"
    )

    root.destroy()
    return resposta


#==============================================
#🔧 1. POPUP DE PROCESSAMENTO DO CÓDIGO
#==============================================

def tela_processamento(funcao_processamento):

    root = tk.Tk()
    root.title("Processamento Pendências EBTA")

    label = tk.Label(root, text="Iniciando...")
    label.pack(padx=50, pady=30)

    progress = ttk.Progressbar(root, mode="indeterminate")
    progress.pack(padx=20, pady=10)
    progress.start()

    def rodar():
        try:
            label.config(text="Processando dados...")
            funcao_processamento()

            label.config(text="Concluído com sucesso!")
        except Exception as e:
            label.config(text=f"Erro: {e}")

        progress.stop()

    threading.Thread(target=rodar).start()

    root.mainloop()