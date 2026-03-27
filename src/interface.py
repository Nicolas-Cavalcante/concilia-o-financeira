import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox
from tkinter import filedialog
from src.main import main
import traceback


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
    tela_processamento(lambda: main(input1, input2, enviar_email))

#==============================================
#🔧 2. CONFIRMAÇÃO DE ENVIO DO E-MAIL
#==============================================

def perguntar_envio_email():
    return messagebox.askyesno(
        "Envio de Email",
        "Deseja enviar o email ao final do processamento?"
    )


#==============================================
#🔧 3. POPUP DE PROCESSAMENTO DO CÓDIGO
#==============================================

def tela_processamento(funcao_processamento):
    root.deiconify()
    root.title("Processamento Pendências EBTA")
    root.geometry("380x200")

    label = tk.Label(root, text="Iniciando...", font=("Arial", 12))
    label.pack(padx=50, pady=30)

    progress = ttk.Progressbar(root, mode="indeterminate")
    progress.pack(padx=20, pady=10)
    progress.start()

    def rodar():
        try:
            root.after(0, lambda: label.config(text="Processando dados..."))
            funcao_processamento()

            root.after(0, lambda: label.config(text="Concluído com sucesso!"))
            root.after(2000, root.destroy)

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

        finally:
            root.after(0, progress.stop)

    threading.Thread(target=rodar, daemon=True).start()
    root.mainloop()

# ==============================
# 4. EXECUÇÃO
# ==============================
if __name__ == "__main__":
    iniciar_processo()