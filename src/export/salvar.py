import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.drawing.image import Image
from openpyxl import Workbook
from pathlib import Path

#Esse arquivo é responsável pela importação das bases
# E aplicação do layout em cada arquivo.
#==============================================
# 📑 SALVA ARQUIVOS
#==============================================

def salvar(df_final, df_nao_localizados, df_sql, df_planilha, path, path_corretos, path_incorretos):

    salvar_df_final_formatado(
        df_final,
        path_corretos / "Conciliados.xlsx",
        #Caminho da Logo do bradesco
        caminho_logo= Path("inputs") / "Logo_Bradesco.png"
        )
    
    df_nao_localizados.to_excel(path_incorretos / "Pendências_EBTA.xlsx", index=False)
    df_sql.to_excel(path / "df_sql.xlsx", index=False)
    df_planilha.to_excel(path / "df_planilha.xlsx", index=False)

    # Esse caminho serve como base ao openpyxl para tratar o estilo na função abaixo
    df_nao_localizados_caminho = path_incorretos / "Pendências_EBTA.xlsx"
    df_planilha= path / "df_planilha.xlsx"
    
    # 3. Aplica a formatação visual
    aplicar_estilo_visual([df_nao_localizados_caminho, df_planilha])


#==============================================
# ✒️ APLICA ESTILO NAS TABELAS
#==============================================

def aplicar_layout(ws):
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    # =========================
    # CABEÇALHO
    # =========================
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.row_dimensions[1].height = 25

    # =========================
    # FILTRO + FREEZE
    # =========================
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = "A2"

    # =========================
    # BORDA LEVE
    # =========================
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for row in ws.iter_rows():
        for cell in row:
            cell.border = border

    # =========================
    # LARGURA AUTOMÁTICA
    # =========================
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        ws.column_dimensions[col_letter].width = min(max_length + 2, 40)


#==============================================
# ✒️ APLICA ESTILO SOMENTE EM DF_FINAL PARA EXPORTAR NO LAYOUT DO BRADESCO
#==============================================

def salvar_df_final_formatado(df_final, caminho_arquivo, caminho_logo):

    wb = Workbook()
    ws = wb.active

    HEADER_ROW = 4
    DATA_START_ROW = 5

    # =========================
    # TÍTULO INICIAL
    # =========================
    ws["A1"] = "GERENCIAR PENDÊNCIAS"
    ws["A1"].font = Font("Arial",size=10, bold=True)
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")

    # =========================
    # LOGO
    # =========================
    img = Image(caminho_logo)
    img.height = 52
    img.width = 256
    ws.add_image(img, "A2")

    # =========================
    # DEFINE ALTURA DAS LINHAS
    # =========================
    ws.row_dimensions[2].height = 12.8
    ws.row_dimensions[3].height = 33.8

    ws.row_dimensions[HEADER_ROW].height = 23.3

    
    # =========================
    # CRIA ESTILO DA TABELA
    # =========================

    thin = Side(style="thin", color="000000")

    border = Border(
        left=thin,
        right=thin,
        top=thin,
        bottom=thin
    )

    # =========================
    # CABEÇALHO (LINHA 4)
    # =========================
    header_fill = PatternFill("solid", fgColor="969696")
    header_font = Font(
        name="Arial",
        size=8,
        color="333399",
        bold=True
        )

    for col_idx, col_name in enumerate(df_final.columns, start=1):
        cell = ws.cell(row=HEADER_ROW, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # =========================
    # DADOS (A PARTIR DA LINHA 5)
    # =========================
    row_font = Font(
        name="Arial",
        size=10
    )

    for row_idx, row in enumerate(df_final.values, start=DATA_START_ROW):
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = row_font

    for r in ws.iter_rows(
        min_row=HEADER_ROW,
        max_row=ws.max_row,
        min_col=1,
        max_col=len(df_final.columns)
    ):
        for cell in r:
            cell.border = border

    # =========================
    # FILTRO + FREEZE
    # =========================
    ws.auto_filter.ref = f"A{HEADER_ROW}:{ws.cell(row=4, column=len(df_final.columns)).coordinate}"
    ws.freeze_panes = f"A{DATA_START_ROW}"

    # =========================
    # AJUSTE DE COLUNA
    # =========================
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        ws.column_dimensions[col_letter].width = min(max_length + 2, 40)

    wb.save(caminho_arquivo)


def aplicar_estilo_visual(caminhos):

    for caminho in caminhos:
        wb = openpyxl.load_workbook(caminho)
        ws = wb.active

        aplicar_layout(ws)   # SEMPRE aplica

        wb.save(caminho)