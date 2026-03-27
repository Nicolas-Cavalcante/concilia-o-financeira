import os
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


#==============================================
# 📊 SALVA ARQUIVOS
#==============================================

def salvar(df_final, df_nao_localizados, path_corretos, path_incorretos):

    df_final.to_excel(path_corretos / "Corretos.xlsx", index=False)
    df_nao_localizados.to_excel(path_incorretos / "Pendências_EBTA.xlsx", index=False)
    
    # Esse caminho serve como base ao openpyxl para tratar o estilo na função abaixo
    df_nao_localizados_caminho = path_incorretos / "Pendências_EBTA.xlsx"
    # 3. Aplica a formatação visual (Ícones e Cores)
    aplicar_estilo_visual(df_nao_localizados_caminho)


#==============================================
# 📊 APLICA ESTILO NA COLUNA STATUS DO PROCESSAMENTO
#==============================================

def aplicar_estilo_visual(caminho_arquivo):
    """Abre o Excel e aplica ícones e cores na coluna 'Status do Processo'"""
    wb = openpyxl.load_workbook(caminho_arquivo)
    ws = wb.active

    # Configuração de Ícones e Cores (RGB Hex do Excel)
    # ⬤ = Círculo cheio | ◯ = Círculo vazio | ⚠ = Alerta
    estilos = {
        "Crítico": {"icone": "⚠", "cor": "FFC000"}, # Amarelo Alerta
        "Urgente": {"icone": "⬤", "cor": "C00000"}, # Vermelho
        "Alta":    {"icone": "◯", "cor": "ED7D31"}, # Laranja
        "Média":   {"icone": "◯", "cor": "FFD966"}, # Amarelo
        "Baixa":   {"icone": "⬤", "cor": "70AD47"}  # Verde
    }

    # Encontrar qual coluna é a 'Status do Processo'
    col_idx = None
    for cell in ws[1]: # Varre a primeira linha (cabeçalho)
        if cell.value == "Status do Processo":
            col_idx = cell.column
            break

    if not col_idx:
        return # Se não achar a coluna, não faz nada

    # Percorre da linha 2 até o fim
    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=col_idx)
        status_texto = str(cell.value).strip()

        if status_texto in estilos:
            config = estilos[status_texto]
            
            # 1. Adiciona o ícone antes do texto
            cell.value = f"{config['icone']} {status_texto}"
            
            # 2. Aplica a cor da fonte e negrito
            cell.font = Font(color=config['cor'], bold=True)
            
            # 3. Alinha à esquerda (estética idêntica ao Excel nativo)
            cell.alignment = Alignment(horizontal='left')

    # Ajusta a largura da coluna para não cortar o texto
    ws.column_dimensions[get_column_letter(col_idx)].width = 22

    # Salva as alterações no mesmo arquivo
    wb.save(caminho_arquivo)