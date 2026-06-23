from PySide6.QtWidgets import QFileDialog, QMessageBox


def exportar_excel(parent, nome_sugerido, titulo_aba, cabecalhos, dados, col_decimals=None):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    path, _ = QFileDialog.getSaveFileName(
        parent, "Exportar Relatório", nome_sugerido, "Excel (*.xlsx)"
    )
    if not path:
        return

    wb = Workbook()
    ws = wb.active
    ws.title = titulo_aba[:31]

    cols = len(cabecalhos)

    green_fill = PatternFill(start_color="2d6a2d", end_color="2d6a2d", fill_type="solid")
    header_font = Font(color="ffffff", bold=True, size=11, name="Calibri")
    thin_border = Border(
        left=Side(style='thin', color="cccccc"),
        right=Side(style='thin', color="cccccc"),
        top=Side(style='thin', color="cccccc"),
        bottom=Side(style='thin', color="cccccc"),
    )

    ws.row_dimensions[1].height = 28
    for col, titulo in enumerate(cabecalhos, 1):
        cell = ws.cell(row=1, column=col, value=titulo)
        cell.fill = green_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    for i, linha in enumerate(dados, 2):
        ws.row_dimensions[i].height = 20
        for col, val in enumerate(linha, 1):
            cell = ws.cell(row=i, column=col, value=val)
            cell.border = thin_border
            cell.font = Font(size=10, name="Calibri")
            if isinstance(val, float):
                dec = (col_decimals or {}).get(col, 2)
                cell.number_format = f'#,##0.{"0" * dec}'
                cell.alignment = Alignment(horizontal='right')
            elif isinstance(val, int):
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal='right')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center')

    ws.column_dimensions['A'].width = 6
    for col in range(2, cols + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.tabColor = "2d6a2d"

    wb.save(path)

    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Exportado")
    msg.setText(f"Relatório salvo em:\n{path}")
    msg.setStyleSheet("""
        QMessageBox { background: white; color: #333; }
        QMessageBox QLabel { color: #333; font-size: 13px; }
        QPushButton {
            padding: 8px 20px; background: #795548; color: white;
            border: none; border-radius: 6px; font-weight: 700; min-width: 80px;
        }
        QPushButton:hover { background: #8D6E63; }
    """)
    msg.exec()
