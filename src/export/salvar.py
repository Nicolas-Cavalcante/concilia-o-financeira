import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


#==============================================
# 📑 SALVA ARQUIVOS
#==============================================

def salvar(df_final, df_nao_localizados, df_sql, path, path_corretos, path_incorretos):

    df_final.to_excel(path_corretos / "Conciliados.xlsx", index=False)
    df_nao_localizados.to_excel(path_incorretos / "Pendências_EBTA.xlsx", index=False)
    df_sql.to_excel(path / "df_sql.xlsx", index=False)

    # Esse caminho serve como base ao openpyxl para tratar o estilo na função abaixo
    df_nao_localizados_caminho = path_incorretos / "Pendências_EBTA.xlsx"
    df_final_caminho = path_corretos / "Conciliados.xlsx"
    # 3. Aplica a formatação visual (Ícones e Cores)
    aplicar_estilo_visual([df_nao_localizados_caminho, df_final_caminho])


#==============================================
# ⚙️ APLICA ESTILO NAS TABELAS
#==============================================

def aplicar_layout(ws):
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    # Cabeçalho
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.row_dimensions[1].height = 25

    # Filtro + Freeze
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = "A2"

    # Borda leve
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for row in ws.iter_rows():
        for cell in row:
            cell.border = border

    # Largura automática
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        ws.column_dimensions[col_letter].width = min(max_length + 2, 40)


#==============================================
# ⚙️ APLICA ESTILO NA COLUNA STATUS DO PROCESSAMENTO
#==============================================

def aplicar_status(ws):
    from openpyxl.styles import Font, Alignment

    estilos = {
        "Crítico": {"icone": "⚠", "cor": "C00000"},
        "Urgente": {"icone": "⬤", "cor": "FD4C00"},
        "Alta":    {"icone": "⬤", "cor": "ED7D31"},
        "Média":   {"icone": "⬤", "cor": "EDBE33"},
        "Baixa":   {"icone": "⬤", "cor": "70AD47"}
    }

    col_idx = None
    for cell in ws[1]:
        if cell.value == "Status do Processo":
            col_idx = cell.column
            break

    if not col_idx:
        return

    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=col_idx)
        status = str(cell.value).strip()

        if status in estilos:
            config = estilos[status]
            cell.value = f"{config['icone']} {status}"
            cell.font = Font(bold=True)  # sem cor, como você decidiu
            cell.alignment = Alignment(horizontal='left')

def aplicar_estilo_visual(caminhos):

    for caminho in caminhos:
        wb = openpyxl.load_workbook(caminho)
        ws = wb.active

        aplicar_layout(ws)   # SEMPRE aplica
        aplicar_status(ws)   # SÓ se existir

        wb.save(caminho)