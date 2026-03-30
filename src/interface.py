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
#🔧 3. POPUP DE PROCESSAMENTO DO CÓDIGO
#==============================================

def tela_processamento(funcao_processamento):
    root.deiconify()
    root.title("Processamento Pendências EBTA")
    root.geometry("420x220")
    root.configure(bg="#F5F6FA")

    container = tk.Frame(root, bg="#F5F6FA")
    container.pack(expand=True)

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

    success_label = tk.Label(
        container,
        text="✔ Processamento concluído",
        font=("Segoe UI", 11, "bold"),
        fg="#0C6832",
        bg="#F5F6FA"
    )

    percent_label.pack(pady=(0,10))
    # ✅ função de atualização
    def atualiza_status(texto, progresso=None):
        def update():
            label.config(text=texto)
            if progresso is not None:
                progress['value'] = progresso
                percent_label.config(text=f"{progresso}%")
            root.update_idletasks()
        root.after(0,update)

    def rodar():
        try:
            funcao_processamento(atualiza_status)

            def mostrar_sucesso():
                progress['value'] = 100
                percent_label.config(text="100%")
                label.config(text="")

                if not success_label.winfo_ismapped():
                    success_label.pack(pady=(10,0))
                root.after(2000, root.destroy)
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