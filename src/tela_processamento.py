import tkinter as tk
import threading
import traceback
import time
from PIL import Image, ImageOps, ImageTk
from pathlib import Path

import customtkinter as ctk

#==============================================
# Cores da identidade Flytour
#==============================================
C_LARANJA       = "#C8721A"
C_VERDE_BARRA   = "#2ECC71"
C_LARANJA_S     = "#9B6B3A"   # laranja suave (subtítulos, relógio)
C_ROSA          = "#C12767"
C_VERDE         = "#49BB37"
C_AMARELO       = "#E8A030"
C_NAVY          = "#1A1F35"
C_ICON          = "#0B1955"
C_PAINEL        = "#141828"
C_SURFACE       = "#1A1F35"
C_BORDA         = "#334155"
C_TEXT          = "#F8FAFC"
C_MUTED         = "#CBD5E1" # controla o nome das etapas, subtítulos e labels secundários
C_DIMMED        = "#94A3B8" # controla pontos quando a etapa ainda não foi iniciada

# Nomes das etapas exibidas nos indicadores
ETAPAS = [
    "Pendências",
    "Base e-mails",
    "Base interna",
    "Conciliação",
    "Exportação",
]


def tela_processamento(root, funcao_processamento, mostrar_menu_fn, abrir_resultado_fn, config, base_path=None):
    """
    Parâmetros
    ----------
    root                : ctk.CTk — janela raiz
    funcao_processamento: callable(atualiza_status) → (percentual_ok, percentual_pendente)
    mostrar_menu_fn     : callable() — volta ao menu
    abrir_resultado_fn  : callable(caminho) — abre arquivo no S.O.
    config              : módulo src.config com OUTPUT_CORRETOS / OUTPUT_INCORRETOS
    """
#==============================================
# limpa e configura janela
#==============================================
    for w in root.winfo_children():
        w.destroy()
    root.configure(fg_color=C_NAVY)


    if base_path is not None:
        caminho = Path(base_path) / "fundo_fly.png"
    else:
        caminho = Path(__file__).resolve().parent / "fundo_fly.png"

    if caminho.exists():
        bg_original = Image.open(caminho).convert("RGBA")

        overlay = Image.new("RGBA", bg_original.size, (0, 0, 0, 145))
        bg_original = Image.alpha_composite(bg_original, overlay)

        canvas = tk.Canvas(root, highlightthickness=0, bd=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        

        def redesenhar(event=None):
            largura = max(canvas.winfo_width(), 1)
            altura = max(canvas.winfo_height(), 1)

            img = ImageOps.fit(bg_original, (largura, altura), Image.LANCZOS)
            
            bg_tk = ImageTk.PhotoImage(img)
            canvas.bg_tk = bg_tk

            canvas.delete("all")
            canvas.create_image(
                0,
                0,
                anchor="nw",
                image=bg_tk
            )

        canvas.bind("<Configure>", redesenhar)
        root.after(0, redesenhar)

        # função força a entrada do fundo_fly ao processar
        def baixar_canvas():
            try:
                canvas.lower()
            except tk.TclError:
                pass

        root.after(10, baixar_canvas)

#==============================================
# estado interno
#==============================================
    estado = {
        "erro":          False,
        "animacao":      True,
        "pct_atual":     0.0,
        "pct_alvo":      0.0,
        "etapa_atual":   -1,
        "etapas_feitas": set(),
        "elapsed":       0,
        "clock_id":      None,
    }

#==============================================
# painel central
#==============================================
    painel = ctk.CTkFrame(
        root,
        width=720,
        height=610,
        corner_radius=10,
        fg_color=C_PAINEL,
        border_width=1,
        border_color=C_BORDA,
    )
    painel.place(relx=0.5, rely=0.5, anchor="center")
    painel.grid_propagate(False)
    painel.grid_columnconfigure(0, weight=1)

#==============================================
# linha 0: header
#==============================================
    header = ctk.CTkFrame(painel, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=36, pady=(28, 0))
    header.grid_columnconfigure(1, weight=1)

    icon_f = ctk.CTkFrame(header, width=32, height=32, corner_radius=7, fg_color=C_ICON)
    icon_f.grid(row=0, column=0, rowspan=2)
    icon_f.grid_propagate(False)
    ctk.CTkLabel(icon_f, text="✦", font=("Segoe UI", 13, "bold"), text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

    nome_f = ctk.CTkFrame(header, fg_color="transparent")
    nome_f.grid(row=0, column=1, sticky="w", padx=(10, 0))
    # Titulos do container
    ctk.CTkLabel(nome_f, text="SmartCheck", font=("Segoe UI", 14, "bold"), text_color=C_TEXT).pack(side="left")
    ctk.CTkLabel(nome_f, text="  Conciliação EBTA", font=("Segoe UI", 10), text_color=C_LARANJA_S).pack(side="left")

    # label tempo de execução
    lbl_clock = ctk.CTkLabel(
        header,
        text="00:00",
        font=("Segoe UI", 11),
        text_color=C_TEXT,
        fg_color=C_SURFACE,
        corner_radius=20,
        padx=10,
        pady=3,
    )
    lbl_clock.grid(row=0, column=2)

#==============================================
    # ── linha 1: separador
#==============================================
    ctk.CTkFrame(painel, height=1, fg_color=C_BORDA).grid(row=1, column=0, sticky="ew", padx=0, pady=(14, 0))

#==============================================
    # ── linha 2: status principal
#==============================================
    lbl_status = ctk.CTkLabel(
        painel,
        text="Iniciando processo",
        font=("Segoe UI", 16, "bold"),
        text_color=C_TEXT,
    )
    lbl_status.grid(row=2, column=0, pady=(18, 2))

    # label sub
    lbl_sub = ctk.CTkLabel(
        painel,
        text="",
        font=("Segoe UI", 11, "bold"),
        text_color=C_MUTED,
    )
    lbl_sub.grid(row=3, column=0, pady=(0, 0))

#==============================================
    # ── linha 3: barra de progresso
#==============================================
    prog_wrap = ctk.CTkFrame(painel, fg_color="transparent")
    prog_wrap.grid(row=4, column=0, sticky="ew", padx=36, pady=(16, 0))
    prog_wrap.grid_columnconfigure(0, weight=1)

    lbl_etapa = ctk.CTkLabel(prog_wrap, text="—", font=("Segoe UI", 10, "bold"), text_color=C_MUTED, anchor="w")
    lbl_etapa.grid(row=0, column=0, sticky="w")

    lbl_pct = ctk.CTkLabel(prog_wrap, text="0%", font=("Segoe UI", 11, "bold"), text_color=C_VERDE, anchor="e")
    lbl_pct.grid(row=0, column=1, sticky="e")

    progressbar = ctk.CTkProgressBar(
        prog_wrap,
        height=5,
        corner_radius=3,
        progress_color=C_VERDE_BARRA,
        fg_color=C_DIMMED,
    )
    progressbar.set(0)
    progressbar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
    progressbar.configure(mode="indeterminate")
    progressbar.start()

#==============================================
    # ── linha 4: indicadores de etapa
#==============================================
    etapas_frame = ctk.CTkFrame(painel, fg_color="transparent")
    etapas_frame.grid(row=5, column=0, sticky="ew", padx=36, pady=(16, 0))
    for i in range(5):
        etapas_frame.grid_columnconfigure(i, weight=1)

    dot_labels  = []
    nome_labels = []

    for i, nome in enumerate(ETAPAS):
        col_f = ctk.CTkFrame(etapas_frame, fg_color=C_SURFACE, corner_radius=6, border_width=1, border_color=C_BORDA)
        col_f.grid(row=0, column=i, sticky="ew", padx=(0, 5) if i < 4 else 0, ipady=8)
        col_f.grid_columnconfigure(0, weight=1)

        dot = ctk.CTkLabel(
            col_f,
            text="●",
            font=("Segoe UI", 11),
            text_color=C_DIMMED
            )
        dot.grid(row=0, column=0, pady=(6, 2))

    # ajusta nome das labels
        nome_lbl = ctk.CTkLabel( 
            col_f,
            text=nome,
            font=("Segoe UI", 11, "bold"),
            text_color=C_MUTED)
        nome_lbl.grid(row=1, column=0, pady=(0, 8))

        dot_labels.append(dot)
        nome_labels.append(nome_lbl)

    # referências guardadas para atualização
    etapa_frames = []
    for widget in etapas_frame.winfo_children():
        etapa_frames.append(widget)

#==============================================
    # ── linha 5: métricas (visível durante execução)
#==============================================
    metrics_frame = ctk.CTkFrame(painel, fg_color="transparent")
    metrics_frame.grid(row=6, column=0, sticky="ew", padx=36, pady=(14, 0))
    for i in range(3):
        metrics_frame.grid_columnconfigure(i, weight=1)

    def _metric_card(parent, col, label):
        card = ctk.CTkFrame(parent, fg_color=C_SURFACE, corner_radius=6, border_width=1, border_color=C_BORDA)
        card.grid(row=0, column=col, sticky="ew", padx=(0, 8) if col < 2 else 0, ipady=8)
        card.grid_columnconfigure(0, weight=1)

        # ajusta cards com resumo do que foi lido, conciliado e pendente
        ctk.CTkLabel(card, text=label, font=("Segoe UI", 11, "bold"), text_color=C_MUTED).grid(row=0, column=0, pady=(8, 2))
        val = ctk.CTkLabel(card, text="—", font=("Segoe UI", 14, "bold"), text_color=C_MUTED)
        val.grid(row=1, column=0, pady=(0, 8))
        return val

    m_registros = _metric_card(metrics_frame, 0, "REGISTROS LIDOS")
    m_ok        = _metric_card(metrics_frame, 1, "CONCILIADOS")
    m_pend      = _metric_card(metrics_frame, 2, "PENDENTES")

#==============================================
    # ── linha 6: log ao vivo
#==============================================
    log_outer = ctk.CTkFrame(painel, fg_color=C_SURFACE, corner_radius=6, border_width=1, border_color=C_BORDA)
    log_outer.grid(row=7, column=0, sticky="ew", padx=36, pady=(12, 0))
    log_outer.grid_columnconfigure(0, weight=1)

    # ajusta formatação no log
    ctk.CTkLabel(log_outer, text="LOG DE EXECUÇÃO", font=("Segoe UI", 8, "bold"), text_color=C_MUTED, anchor="w").grid(
        row=0, column=0, sticky="w", padx=12, pady=(8, 4)
    )

    log_entries_frame = ctk.CTkFrame(log_outer, fg_color="transparent", height=52)
    log_entries_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
    log_entries_frame.grid_propagate(False)
    log_entries_frame.grid_columnconfigure(0, weight=1)

    log_linhas = []   # lista de CTkLabel no log
    
    # descrição do log 
    def _add_log(msg):
        ts = time.strftime("%H:%M:%S")
        for lbl in log_linhas:
            lbl.configure(text_color=C_DIMMED)
        novo = ctk.CTkLabel(
            log_entries_frame,
            text=f"{ts}  ▸ {msg}",
            font=("Segoe UI", 9),
            text_color=C_AMARELO,
            anchor="w",
        )
        log_linhas.append(novo)
        # mantém máx 3 linhas
        if len(log_linhas) > 3:
            log_linhas[0].destroy()
            log_linhas.pop(0)
        for idx, lbl in enumerate(log_linhas):
            lbl.grid(row=idx, column=0, sticky="w")

#==============================================
    # ── linha 7: cards de resultado (ocultos durante execução)
#==============================================
    resultado_frame = ctk.CTkFrame(painel, fg_color="transparent")
    # não colocamos no grid ainda — aparece só ao final

    def _result_card(parent, col, label, cor_borda, cor_pct):
        card = ctk.CTkFrame(
            parent,
            fg_color=C_SURFACE,
            corner_radius=8,
            border_width=1,
            border_color=cor_borda,
        )
        card.grid(row=0, column=col, sticky="ew", padx=(0, 10) if col == 0 else 0, ipady=12)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=16, pady=8)

        ctk.CTkLabel(left, text=label, font=("Segoe UI", 9, "bold"), text_color=C_MUTED).pack(anchor="w")
        count_lbl = ctk.CTkLabel(left, text="—", font=("Segoe UI", 20, "bold"), text_color=C_TEXT)
        count_lbl.pack(anchor="w")
        ctk.CTkLabel(left, text="registros", font=("Segoe UI", 10), text_color=C_MUTED).pack(anchor="w")

        pct_lbl = ctk.CTkLabel(card, text="—%", font=("Segoe UI", 26, "bold"), text_color=cor_pct)
        pct_lbl.grid(row=0, column=1, padx=16)

        return count_lbl, pct_lbl

    resultado_frame.grid_columnconfigure((0, 1), weight=1)
    r_ok_count,   r_ok_pct   = _result_card(resultado_frame, 0, "CONCILIADOS", C_VERDE, C_VERDE)
    r_pend_count, r_pend_pct = _result_card(resultado_frame, 1, "PENDENTES",   C_ROSA,  C_ROSA)

#==============================================
    # ── linha 8: botões
#==============================================
    btns_exec  = ctk.CTkFrame(painel, fg_color="transparent")
    btns_exec.grid(row=9, column=0, pady=(16, 28))

    btns_done  = ctk.CTkFrame(painel, fg_color="transparent")
    # aparece só no final

    # ajusta botões finais conciliados, pendentes e nova conciliação
    def _btn(parent, text, fg, hover, txt_cor, cmd):
        return ctk.CTkButton(
            parent,
            text=text,
            width=155,
            height=38,
            corner_radius=7,
            fg_color=fg,
            hover_color=hover,
            text_color=txt_cor,
            font=("Segoe UI", 12, "bold"),
            command=cmd,
            border_width=1,
            border_color="#4B5563"
        )

#==============================================
    # ── animação de pontos
#==============================================
    lbl_pontos = ctk.CTkLabel(painel, text="", font=("Segoe UI", 13, "bold"), text_color=C_LARANJA, fg_color="transparent")
    lbl_pontos.grid(row=8, column=0, pady=(4, 0))

#==============================================
    # ── relógio
#==============================================
    def _tick():
        estado["elapsed"] += 1
        m, s = divmod(estado["elapsed"], 60)
        try: lbl_clock.configure(text=f"{m:02d}:{s:02d}")
        except tk.TclError: return
        estado["clock_id"] = root.after(1000, _tick)

    estado["clock_id"] = root.after(1000, _tick)

#==============================================
    # ── animação suave da barra
#==============================================
    def _animar_barra():
        diff = estado["pct_alvo"] - estado["pct_atual"]
        if abs(diff) > 0.002:
            estado["pct_atual"] += diff * 0.07
            try:
                progressbar.set(estado["pct_atual"])
                lbl_pct.configure(text=f"{int(estado['pct_atual'] * 100)}%")
            except tk.TclError:
                return
            root.after(16, _animar_barra)
        else:
            estado["pct_atual"] = estado["pct_alvo"]
            try:
                progressbar.set(estado["pct_atual"])
                lbl_pct.configure(text=f"{int(estado['pct_atual'] * 100)}%")
            except tk.TclError:
                pass

#==============================================
    # ── atualizar indicador de etapa
#==============================================
    def _set_etapa(idx, estado_etapa):
        frame = etapa_frames[idx]
        dot   = dot_labels[idx]
        nome  = nome_labels[idx]

        if estado_etapa == "ativo":
            frame.configure(
                border_color=C_LARANJA,
                fg_color=C_NAVY
            )
            dot.configure(text_color=C_LARANJA)
            nome.configure(text_color=C_LARANJA)

        elif estado_etapa == "feito":
            frame.configure(
                border_color=C_VERDE,
                fg_color=C_SURFACE
            )
            dot.configure(text_color=C_VERDE)
            nome.configure(text_color=C_VERDE)

        else:
            frame.configure(
                border_color=C_BORDA,
                fg_color=C_SURFACE
            )
            dot.configure(text_color=C_DIMMED)
            nome.configure(text_color=C_MUTED)

#==============================================
    # ── exibir erro
#==============================================
    def _exibir_erro(mensagem, tipo="sistema"):
            """
            tipo='usuario' → laranja, orientação clara de o que fazer
            tipo='sistema' → vermelho, orienta a contatar suporte
            """
            estado["erro"]     = True
            estado["animacao"] = False
            if estado["clock_id"]:
                root.after_cancel(estado["clock_id"])

            try:
                progressbar.stop()
            except tk.TclError:
                pass

            # Cores por tipo
            if tipo == "usuario":
                cor_titulo  = "#F59E0B"   # âmbar — problema que o usuário resolve
                cor_sub     = "#FCD34D"
                cor_borda   = "#92400E"
                cor_bg      = "#1C1200"
                titulo      = "Ação necessária"
            else:
                cor_titulo  = "#EF4444"   # vermelho — erro interno
                cor_sub     = "#FCA5A5"
                cor_borda   = "#7F1D1D"
                cor_bg      = "#1C0A0A"
                titulo      = "Erro no processamento"

            try:
                lbl_status.configure(text=titulo, text_color=cor_titulo)
                #lbl_sub.configure(text=mensagem[:90] + ("..." if len(mensagem) > 90 else ""), text_color=cor_sub)
                lbl_pct.configure(text="!" if tipo == "usuario" else "Erro")
                btns_exec.grid_remove()
                metrics_frame.grid_remove()
                log_outer.grid_remove()

                # Caixa de detalhe inline
                erro_box = ctk.CTkFrame(
                    painel,
                    fg_color=cor_bg,
                    corner_radius=6,
                    border_width=1,
                    border_color=cor_borda,
                )
                erro_box.grid(row=7, column=0, sticky="ew", padx=36, pady=(8, 0))
                erro_box.grid_columnconfigure(0, weight=1)

                icone = "⚠" if tipo == "usuario" else "✕"
                ctk.CTkLabel(
                    erro_box,
                    text=f"{icone}  {titulo.upper()}",
                    font=("Segoe UI", 9, "bold"),
                    text_color=cor_sub,
                    anchor="w",
                ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

                ctk.CTkLabel(
                    erro_box,
                    text=mensagem,
                    font=("Segoe UI", 11),
                    text_color=cor_sub,
                    anchor="w",
                    wraplength=580,
                    justify="left",
                ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))

                # Botão voltar
                btn_voltar = ctk.CTkFrame(painel, fg_color="transparent")
                btn_voltar.grid(row=9, column=0, pady=(16, 28))
                _btn(
                    btn_voltar,
                    "← Voltar ao menu",
                    "transparent",
                    C_BORDA,
                    C_MUTED,
                    mostrar_menu_fn,
                ).pack()

            except tk.TclError:
                pass

#==============================================
    # ── callback de status (chamado do main.py)
#==============================================
    def atualiza_status(texto, progresso=None, etapa=None, log=None, registros=None, ok=None, pendentes=None):
        """
        Parâmetros opcionais além de texto/progresso:
          etapa     : int 0-4  → marca etapa como ativa
          log       : (chave, msg) → adiciona linha no log
          registros : int → atualiza card "registros lidos"
          ok        : int → atualiza card "conciliados"
          pendentes : int → atualiza card "pendentes"
        """
        def update():
            if estado["erro"]:
                return
            try:
                if texto:
                    lbl_status.configure(text=texto.rstrip("."), text_color=C_TEXT)

                if progresso is not None:
                    progressbar.stop()
                    progressbar.configure(mode="determinate")
                    estado["pct_alvo"] = progresso / 100
                    _animar_barra()

                if etapa is not None and etapa not in estado["etapas_feitas"]:
                    if estado["etapa_atual"] >= 0:
                        _set_etapa(estado["etapa_atual"], "feito")
                        estado["etapas_feitas"].add(estado["etapa_atual"])
                    estado["etapa_atual"] = etapa
                    _set_etapa(etapa, "ativo")
                    lbl_etapa.configure(text=f"etapa {etapa + 1} de {len(ETAPAS)}")
                    #lbl_sub.configure(text=ETAPAS[etapa])

                if log:
                    _add_log(log[1])

                if registros is not None:
                    m_registros.configure(text=str(registros), text_color=C_TEXT)

                if ok is not None:
                    m_ok.configure(text=str(ok), text_color=C_VERDE)

                if pendentes is not None:
                    m_pend.configure(text=str(pendentes), text_color=C_ROSA)

                root.update_idletasks()

            except tk.TclError as e:
                _exibir_erro(str(e))

        root.after(0, update)

#==============================================
    # ── thread de execução
#==============================================
    def rodar():
        try:
            resultado = funcao_processamento(atualiza_status)

            if not resultado:
                raise RuntimeError("Processamento encerrado sem resultado.")

            percentual_ok, percentual_pendente = resultado

            def mostrar_sucesso():
                estado["animacao"] = False
                if estado["clock_id"]:
                    root.after_cancel(estado["clock_id"])

                # finaliza última etapa
                if estado["etapa_atual"] >= 0:
                    _set_etapa(estado["etapa_atual"], "feito")

                estado["pct_alvo"] = 1.0
                _animar_barra()

                lbl_status.configure(text="Processamento concluído", text_color=C_VERDE)
                #lbl_sub.configure(text=f"tempo total · {lbl_clock.cget('text')}")
                lbl_etapa.configure(text="concluído")
                lbl_pct.configure(text="100%")
                lbl_pontos.configure(text="")

                # total de registros para calcular contagens
                try:
                    total_txt = m_registros.cget("text")
                    total = int(total_txt) if total_txt.isdigit() else 0
                    ok_count   = round(total * percentual_ok / 100)
                    pend_count = total - ok_count
                except Exception:
                    ok_count   = "—"
                    pend_count = "—"

                # oculta métricas e log
                metrics_frame.grid_remove()
                log_outer.grid_remove()

                # exibe cards de resultado
                r_ok_count.configure(text=str(ok_count))
                r_ok_pct.configure(text=f"{percentual_ok:.1f}%")
                r_pend_count.configure(text=str(pend_count))
                r_pend_pct.configure(text=f"{percentual_pendente:.1f}%")
                resultado_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=36, pady=(14, 0))

                # botões finais
                btns_exec.grid_remove()
                btns_done.grid(row=9, column=0, pady=(16, 28))

                _btn(
                    btns_done, "Conciliados",
                    "transparent", C_SURFACE, C_VERDE,
                    lambda: abrir_resultado_fn(config.OUTPUT_CORRETOS / "Conciliados.xlsx"),
                ).pack(side="left", padx=6)

                _btn(
                    btns_done, "Pendentes",
                    "transparent", C_SURFACE, C_ROSA,
                    lambda: abrir_resultado_fn(config.OUTPUT_INCORRETOS / "Pendências_EBTA.xlsx"),
                ).pack(side="left", padx=6)

                _btn(
                    btns_done, "Nova conciliação",
                    "transparent", C_BORDA, C_MUTED,
                    mostrar_menu_fn,
                ).pack(side="left", padx=6)

            root.after(0, mostrar_sucesso)

        except PermissionError as e:
            err_msg = "Um arquivo está aberto no Excel. Feche-o e execute novamente."
            print(f"[USUARIO] {e}")
            root.after(0, lambda m=err_msg: _exibir_erro(m, tipo="usuario"))
 
        except Exception as e:
            # Verifica se é SmartCheckError (já classificado pelo main.py)
            tipo      = getattr(e, "tipo", "sistema")
            msg       = getattr(e, "mensagem_usuario", None) or str(e)
            detalhe   = getattr(e, "detalhe", str(e))
 
            print(traceback.format_exc())
            print(f"[{tipo.upper()}] {detalhe}")
 
            #err_msg  = msg
            #err_tipo = tipo
            root.after(0, lambda m=msg, t=tipo: _exibir_erro(m, tipo=t))

    root.after(80, lambda: threading.Thread(target=rodar, daemon=True).start())
