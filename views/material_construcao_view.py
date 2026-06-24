from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QDoubleSpinBox,
    QDateEdit, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from controllers.material_construcao_controller import MaterialConstrucaoController
from utils.widgets import msg_box
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit, estilizar_calendario
from utils.excel_export import exportar_excel


class MaterialConstrucaoDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.controller = MaterialConstrucaoController()
        self.setWindowTitle("Editar Recebimento" if registro else "Novo Recebimento")
        self.setMinimumWidth(600)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self._setup_ui()
        self.showMaximized()
        if registro:
            self._preencher(registro)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setMinimumSize(560, 580)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 25, 35, 25)
        card_layout.setSpacing(8)

        title = QLabel("Editar Recebimento" if self.registro else "Novo Recebimento")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4E342E; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        card_layout.addSpacing(10)

        lbl_data = QLabel("DATA")
        lbl_data.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_data)

        self.date_data = QDateEdit()
        self.date_data.setDate(QDate.currentDate())
        self.date_data.setCalendarPopup(True)
        self.date_data.setDisplayFormat("dd/MM/yyyy")
        estilizar_calendario(self.date_data)
        self.date_data.setStyleSheet("""
            QDateEdit {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QDateEdit:focus {
                border-color: #795548;
                background: white;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
        """)
        card_layout.addWidget(self.date_data)

        lbl_material = QLabel("MATERIAL")
        lbl_material.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_material)

        self.cmb_material = QComboBox()
        self.cmb_material.setEditable(True)
        self.cmb_material.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_material.lineEdit().setPlaceholderText("Digite ou selecione o material")
        self.cmb_material.setStyleSheet(self._input_style())
        tipos = self.controller.listar_tipos_material()
        for t in tipos:
            self.cmb_material.addItem(t["nome"], t["id"])
        self.cmb_material.setCurrentText("")
        card_layout.addWidget(self.cmb_material)

        lbl_fornecedora = QLabel("EMPRESA FORNECEDORA")
        lbl_fornecedora.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_fornecedora)

        self.cmb_fornecedora = QComboBox()
        self.cmb_fornecedora.setEditable(True)
        self.cmb_fornecedora.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_fornecedora.lineEdit().setPlaceholderText("Selecione ou digite a fornecedora")
        self.cmb_fornecedora.setStyleSheet(self._input_style())
        self.cmb_fornecedora.addItem("Selecione...", None)
        for e in self.controller.listar_entidades():
            self.cmb_fornecedora.addItem(f"{e['razao_social']} ({e['cnpj_cpf']})", e["id"])
        card_layout.addWidget(self.cmb_fornecedora)

        lbl_transportadora = QLabel("TRANSPORTADORA")
        lbl_transportadora.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_transportadora)

        self.cmb_transportadora = QComboBox()
        self.cmb_transportadora.setEditable(True)
        self.cmb_transportadora.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_transportadora.lineEdit().setPlaceholderText("Selecione ou digite a transportadora")
        self.cmb_transportadora.setStyleSheet(self._input_style())
        self.cmb_transportadora.addItem("Selecione...", None)
        for e in self.controller.listar_entidades():
            self.cmb_transportadora.addItem(f"{e['razao_social']} ({e['cnpj_cpf']})", e["id"])
        card_layout.addWidget(self.cmb_transportadora)

        valores_layout = QHBoxLayout()
        valores_layout.setSpacing(15)

        vl_peso = QVBoxLayout()
        vl_peso.setSpacing(4)
        lbl_peso = QLabel("PESO (KG)")
        lbl_peso.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        vl_peso.addWidget(lbl_peso)

        self.spin_peso = QDoubleSpinBox()
        self.spin_peso.setRange(0, 999999.999)
        self.spin_peso.setDecimals(3)
        self.spin_peso.setFixedHeight(44)
        self.spin_peso.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QDoubleSpinBox:focus {
                border-color: #795548;
                background: white;
            }
        """)
        vl_peso.addWidget(self.spin_peso)
        valores_layout.addLayout(vl_peso)

        vl_qtd = QVBoxLayout()
        vl_qtd.setSpacing(4)
        lbl_qtd = QLabel("QUANTIDADE")
        lbl_qtd.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        vl_qtd.addWidget(lbl_qtd)

        qtd_row = QHBoxLayout()
        qtd_row.setSpacing(8)

        self.spin_metros = QDoubleSpinBox()
        self.spin_metros.setRange(0, 999999.999)
        self.spin_metros.setDecimals(3)
        self.spin_metros.setFixedHeight(44)
        self.spin_metros.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QDoubleSpinBox:focus {
                border-color: #795548;
                background: white;
            }
        """)
        qtd_row.addWidget(self.spin_metros)

        self.cmb_unidade = QComboBox()
        self.cmb_unidade.addItem("Metros (m)", "M")
        self.cmb_unidade.addItem("Metros Cúbicos (m³)", "M³")
        self.cmb_unidade.setCurrentIndex(1)
        self.cmb_unidade.setFixedHeight(44)
        self.cmb_unidade.setMinimumWidth(160)
        self.cmb_unidade.setStyleSheet("""
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QComboBox:focus {
                border-color: #795548;
                background: white;
            }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """)
        qtd_row.addWidget(self.cmb_unidade)

        vl_qtd.addLayout(qtd_row)
        valores_layout.addLayout(vl_qtd)

        card_layout.addLayout(valores_layout)

        card_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setFixedHeight(44)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 10px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #ccc; }
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setCursor(Qt.PointingHandCursor)
        btn_salvar.setFixedHeight(44)
        btn_salvar.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5D4037, stop:1 #795548);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #795548, stop:1 #8D6E63);
            }
        """)
        btn_salvar.clicked.connect(self._validar_salvar)
        btn_layout.addWidget(btn_salvar)

        card_layout.addLayout(btn_layout)

        layout.addWidget(card)

    def _input_style(self):
        return """
            QLineEdit, QComboBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #795548;
                background: white;
            }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """

    def _preencher(self, r):
        qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
        if qd.isValid():
            self.date_data.setDate(qd)
        idx = self.cmb_material.findData(r["material_id"])
        if idx >= 0:
            self.cmb_material.setCurrentIndex(idx)
        else:
            self.cmb_material.setCurrentText(r.get("material_nome", ""))
        fornecedora = r.get("empresa_fornecedora", "")
        idx = self.cmb_fornecedora.findText(fornecedora, Qt.MatchStartsWith)
        if idx >= 0:
            self.cmb_fornecedora.setCurrentIndex(idx)
        else:
            self.cmb_fornecedora.setEditText(fornecedora)

        transportadora = r.get("transportadora", "")
        idx = self.cmb_transportadora.findText(transportadora, Qt.MatchStartsWith)
        if idx >= 0:
            self.cmb_transportadora.setCurrentIndex(idx)
        else:
            self.cmb_transportadora.setEditText(transportadora)

        self.spin_peso.setValue(r.get("peso_kg", 0))
        self.spin_metros.setValue(r.get("metros_cubicos", 0))
        unidade = r.get("unidade", "M³")
        idx = self.cmb_unidade.findData(unidade)
        if idx >= 0:
            self.cmb_unidade.setCurrentIndex(idx)

    def _validar_salvar(self):
        material = self.cmb_material.currentText().strip()
        if not material:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Validação")
            msg.setText("O material é obrigatório.")
            msg.setStyleSheet("""
                QMessageBox { background: white; }
                QMessageBox QLabel { color: #333; font-size: 13px; }
                QPushButton {
                    padding: 8px 20px; background: #795548; color: white;
                    border: none; border-radius: 6px; font-weight: 700; min-width: 80px;
                }
                QPushButton:hover { background: #8D6E63; }
            """)
            msg.exec()
            self.cmb_material.setFocus()
            return
        self.accept()

    def obter_dados(self):
        fornecedora = self.cmb_fornecedora.currentText().strip()
        if fornecedora in ("", "Selecione..."):
            fornecedora = ""
        transportadora = self.cmb_transportadora.currentText().strip()
        if transportadora in ("", "Selecione..."):
            transportadora = ""
        return {
            "data": self.date_data.date().toString("yyyy-MM-dd"),
            "material": self.cmb_material.currentText().strip().upper(),
            "empresa_fornecedora": fornecedora,
            "transportadora": transportadora,
            "peso_kg": self.spin_peso.value(),
            "metros_cubicos": self.spin_metros.value(),
            "unidade": self.cmb_unidade.currentData(),
        }

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class MaterialConstrucaoView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.controller = MaterialConstrucaoController()
        self._setup_ui()
        self._atualizar_filtro_material()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Recebimentos Gerais")
        header.setStyleSheet("color: white; font-size: 22px; font-weight: 700; letter-spacing: 2px;")
        layout.addWidget(header)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.cmb_filtro_material = QComboBox()
        self.cmb_filtro_material.setStyleSheet(self._combo_style())
        self.cmb_filtro_material.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_material)

        toolbar.addStretch()

        self.btn_novo = QPushButton("+ Novo Recebimento")
        self.btn_novo.setCursor(Qt.PointingHandCursor)
        self.btn_novo.setFixedHeight(40)
        self.btn_novo.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5D4037, stop:1 #795548);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #795548, stop:1 #8D6E63);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3E2723, stop:1 #5D4037);
            }
        """)
        self.btn_novo.clicked.connect(self._novo)
        toolbar.addWidget(self.btn_novo)

        toolbar.addStretch()

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setCursor(Qt.PointingHandCursor)
        self.btn_editar.setFixedHeight(40)
        self.btn_editar.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover { background: #f1c40f; }
            QPushButton:pressed { background: #d68910; }
        """)
        self.btn_editar.clicked.connect(self._editar)
        toolbar.addWidget(self.btn_editar)

        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setCursor(Qt.PointingHandCursor)
        self.btn_excluir.setFixedHeight(40)
        self.btn_excluir.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover { background: #ec7063; }
            QPushButton:pressed { background: #c0392b; }
        """)
        self.btn_excluir.clicked.connect(self._excluir)
        toolbar.addWidget(self.btn_excluir)

        btn_exportar = QPushButton("📤 Exportar")
        btn_exportar.setCursor(Qt.PointingHandCursor)
        btn_exportar.setFixedHeight(40)
        btn_exportar.setStyleSheet("""
            QPushButton {
                padding: 8px 16px; background: #795548; color: white;
                border: none; border-radius: 8px; font-weight: 700; font-size: 12px;
            }
            QPushButton:hover { background: #8D6E63; }
            QPushButton:pressed { background: #5D4037; }
        """)
        btn_exportar.clicked.connect(self._exportar)
        toolbar.addWidget(btn_exportar)

        card_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Data", "Material", "Fornecedora", "Transportadora", "Peso (kg)", "Quantidade", "Unidade"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.doubleClicked.connect(self._editar)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.Stretch)
        header_view.setSectionResizeMode(4, QHeaderView.Stretch)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background: #ffffff;
                gridline-color: transparent;
                font-size: 14px;
                color: #000;
                selection-background-color: #d4d4d4;
            }
            QTableWidget::item {
                padding: 10px 16px;
            }
            QTableWidget::item:selected {
                background: #d4d4d4;
                color: #1a1a1a;
            }
            QTableWidget::item:hover {
                background: #dcdcdc;
            }
            QHeaderView::section {
                background: #F5F0EB;
                color: #4E342E;
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid #795548;
                border-right: 1px solid #e8e8e8;
                font-weight: 700;
                font-size: 13px;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget::item:alternate {
                background: #e6e6e6;
            }
        """)

        card_layout.addWidget(self.table)

        self.lbl_resumo = QLabel()
        self.lbl_resumo.setStyleSheet("color: #4E342E; font-size: 16px; font-weight: 700; padding: 10px 0;")
        self.lbl_resumo.setAlignment(Qt.AlignRight)
        card_layout.addWidget(self.lbl_resumo)

        layout.addWidget(card)

    def _combo_style(self):
        return """
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
                background: #fafafa;
                min-width: 250px;
                color: #000;
            }
            QComboBox:focus {
                border-color: #795548;
                background: white;
            }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """

    def _fmt_num(self, val):
        return f"{val:_.0f}".replace("_", ".")

    def _atualizar_filtro_material(self):
        current_id = self.cmb_filtro_material.currentData()
        self.cmb_filtro_material.blockSignals(True)
        self.cmb_filtro_material.clear()
        self.cmb_filtro_material.addItem("Todos os materiais", None)
        for t in self.controller.listar_tipos_material():
            self.cmb_filtro_material.addItem(t["nome"], t["id"])
        idx = self.cmb_filtro_material.findData(current_id)
        if idx >= 0:
            self.cmb_filtro_material.setCurrentIndex(idx)
        self.cmb_filtro_material.blockSignals(False)

    def _carregar_dados(self):
        registros = self.controller.listar()
        material_id = self.cmb_filtro_material.currentData()
        if material_id:
            registros = [r for r in registros if r["material_id"] == material_id]
        nome_material = self.cmb_filtro_material.currentText()

        self.table.setRowCount(len(registros))
        total_peso = total_quantidade = 0
        for i, r in enumerate(registros):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            self.table.setItem(i, 1, QTableWidgetItem(data_str))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("material_nome", "")))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("empresa_fornecedora", "")))
            self.table.setItem(i, 4, QTableWidgetItem(r.get("transportadora", "")))
            self.table.setItem(i, 5, QTableWidgetItem(self._fmt_num(r.get('peso_kg', 0))))
            self.table.setItem(i, 6, QTableWidgetItem(f"{r.get('metros_cubicos', 0):.2f}"))
            self.table.setItem(i, 7, QTableWidgetItem(r.get('unidade', 'M³')))
            total_peso += r.get("peso_kg", 0) or 0
            total_quantidade += r.get("metros_cubicos", 0) or 0
        if nome_material == "Todos os materiais":
            self.lbl_resumo.setText(
                f"Total: {self._fmt_num(total_peso)} kg  |  {total_quantidade:.3f} total"
            )
        else:
            self.lbl_resumo.setText(
                f"{nome_material}  |  Total: {self._fmt_num(total_peso)} kg  |  {total_quantidade:.3f} total"
            )

    def _msg_box(self, icone, titulo, texto, botoes=None):
        return msg_box(self, icone, titulo, texto, botoes)

    def _confirmar_senha(self):
        senha, ok = QInputDialog.getText(self, "Autenticação", "Digite sua senha:", QLineEdit.Password)
        if not ok or not senha:
            return False
        auth = AuthController()
        if auth.verificar_senha(senha):
            return True
        self._msg_box(QMessageBox.Warning, "Erro", "Senha incorreta.")
        return False

    def _novo(self):
        dialog = MaterialConstrucaoDialog(self)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.salvar(dados)
            self._atualizar_filtro_material()
            self._carregar_dados()
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um recebimento para editar.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        registro = self.controller.buscar_por_id(registro_id)
        if not registro:
            self._msg_box(QMessageBox.Warning, "Erro", "Recebimento não encontrado.")
            return
        dialog = MaterialConstrucaoDialog(self, registro)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.atualizar(registro_id, dados)
            self._atualizar_filtro_material()
            self._carregar_dados()
        self._timer.start(2000)

    def _excluir(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um recebimento para excluir.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        material = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir o recebimento de '{material}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(registro_id)
            self._carregar_dados()

    def _exportar(self):
        registros = self.controller.listar()
        material_id = self.cmb_filtro_material.currentData()
        if material_id:
            registros = [r for r in registros if r["material_id"] == material_id]
        cabecalhos = ["ID", "Data", "Material", "Fornecedora", "Transportadora", "Peso (kg)", "Quantidade", "Unidade"]
        dados = []
        for r in registros:
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            dados.append((
                r["id"], data_str, r.get("material_nome", ""),
                r.get("empresa_fornecedora", ""), r.get("transportadora", ""),
                r.get("peso_kg", 0), r.get("metros_cubicos", 0),
                r.get("unidade", "M³"),
            ))
        exportar_excel(self, "relatorio_materiais.xlsx", "Recebimentos", cabecalhos, dados)
