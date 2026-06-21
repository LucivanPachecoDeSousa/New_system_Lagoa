from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QDoubleSpinBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor, QDoubleValidator
from controllers.vendas_controller import VendasController
from controllers.auth_controller import AuthController
from controllers.produto_controller import ProdutoController
from utils.widgets import UpperCaseLineEdit, estilizar_calendario
from utils.excel_export import exportar_excel


class VendasDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.controller = VendasController()
        self._calculando = False
        self.setWindowTitle("Editar Venda" if registro else "Nova Venda")
        self.setMinimumWidth(720)
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
        card.setMinimumSize(680, 480)
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

        title = QLabel("Editar Venda" if self.registro else "Nova Venda")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a3a1a; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        card_layout.addSpacing(10)

        linha1 = QHBoxLayout()
        linha1.setSpacing(12)
        g1 = self._grupo("DATA", self._criar_data())
        g2 = self._grupo("PRODUTO", self._criar_produto())
        linha1.addLayout(g1)
        linha1.addLayout(g2)
        card_layout.addLayout(linha1)

        linha2 = QHBoxLayout()
        linha2.setSpacing(12)
        g3 = self._grupo("QUANTIDADE (KG)", self._criar_quantidade())
        g4 = self._grupo("COMPRADOR", self._criar_comprador())
        linha2.addLayout(g3)
        linha2.addLayout(g4)
        card_layout.addLayout(linha2)

        linha3 = QHBoxLayout()
        linha3.setSpacing(12)
        g5 = self._grupo("VALOR UNITÁRIO (R$)", self._criar_valor_unitario())
        g6 = self._grupo("VALOR TOTAL (R$)", self._criar_valor_total())
        linha3.addLayout(g5)
        linha3.addLayout(g6)
        card_layout.addLayout(linha3)

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
                    stop:0 #1a4a1a, stop:1 #2d6a2d);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d6a2d, stop:1 #3e8a3e);
            }
        """)
        btn_salvar.clicked.connect(self._validar_salvar)
        btn_layout.addWidget(btn_salvar)

        card_layout.addLayout(btn_layout)

        layout.addWidget(card)

    def _grupo(self, label, widget):
        vb = QVBoxLayout()
        vb.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        vb.addWidget(lbl)
        vb.addWidget(widget)
        return vb

    def _criar_data(self):
        self.date_data = QDateEdit()
        self.date_data.setDate(QDate.currentDate())
        self.date_data.setCalendarPopup(True)
        self.date_data.setDisplayFormat("dd/MM/yyyy")
        estilizar_calendario(self.date_data)
        self.date_data.setStyleSheet(self._field_style())
        return self.date_data

    def _criar_produto(self):
        self.cmb_produto = QComboBox()
        self.cmb_produto.setEditable(True)
        self.cmb_produto.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_produto.lineEdit().setPlaceholderText("Selecione ou digite o produto")
        self.cmb_produto.setStyleSheet(self._input_style())
        produtos = ProdutoController().listar()
        for p in produtos:
            self.cmb_produto.addItem(p["nome"], p["id"])
        return self.cmb_produto

    def _criar_quantidade(self):
        self.txt_quantidade = UpperCaseLineEdit()
        self.txt_quantidade.setPlaceholderText("Ex: 1500 ou 1250.5")
        self.txt_quantidade.setValidator(QDoubleValidator(0, 999999, 3))
        self.txt_quantidade.setStyleSheet(self._input_style())
        self.txt_quantidade.textChanged.connect(self._calcular_unitario_para_total)
        return self.txt_quantidade

    def _criar_comprador(self):
        self.txt_comprador = UpperCaseLineEdit()
        self.txt_comprador.setPlaceholderText("Nome do comprador")
        self.txt_comprador.setStyleSheet(self._input_style())
        return self.txt_comprador

    def _criar_valor_unitario(self):
        self.spin_valor_unitario = QDoubleSpinBox()
        self.spin_valor_unitario.setRange(0, 999999999)
        self.spin_valor_unitario.setDecimals(2)
        self.spin_valor_unitario.setPrefix("R$ ")
        self.spin_valor_unitario.setFixedHeight(44)
        self.spin_valor_unitario.setStyleSheet(self._field_style())
        self.spin_valor_unitario.valueChanged.connect(self._calcular_unitario_para_total)
        return self.spin_valor_unitario

    def _criar_valor_total(self):
        self.spin_valor_total = QDoubleSpinBox()
        self.spin_valor_total.setRange(0, 999999999)
        self.spin_valor_total.setDecimals(2)
        self.spin_valor_total.setPrefix("R$ ")
        self.spin_valor_total.setFixedHeight(44)
        self.spin_valor_total.setStyleSheet(self._field_style())
        self.spin_valor_total.valueChanged.connect(self._calcular_total_para_unitario)
        return self.spin_valor_total

    def _field_style(self):
        return """
            QDateEdit, QDoubleSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QDateEdit:focus, QDoubleSpinBox:focus {
                border-color: #2d6a2d;
                background: white;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
        """

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
                border-color: #2d6a2d;
                background: white;
            }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """

    def _get_qtd(self):
        try:
            return float(self.txt_quantidade.text().strip() or 0)
        except ValueError:
            return 0

    def _calcular_unitario_para_total(self):
        if self._calculando:
            return
        self._calculando = True
        qtd = self._get_qtd()
        unitario = self.spin_valor_unitario.value()
        total = qtd * unitario
        self.spin_valor_total.setValue(round(total, 2))
        self._calculando = False

    def _calcular_total_para_unitario(self):
        if self._calculando:
            return
        qtd = self._get_qtd()
        total = self.spin_valor_total.value()
        if qtd > 0:
            self._calculando = True
            unitario = total / qtd
            self.spin_valor_unitario.setValue(round(unitario, 2))
            self._calculando = False

    def _preencher(self, r):
        qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
        if qd.isValid():
            self.date_data.setDate(qd)
        idx = self.cmb_produto.findText(r.get("produto", ""))
        if idx >= 0:
            self.cmb_produto.setCurrentIndex(idx)
        else:
            self.cmb_produto.setEditText(r.get("produto", ""))
        qtd = r.get("quantidade_kg", 0)
        if qtd == int(qtd):
            self.txt_quantidade.setText(str(int(qtd)))
        else:
            self.txt_quantidade.setText(str(qtd))
        self.txt_comprador.setText(r.get("comprador", ""))
        self.spin_valor_unitario.setValue(r.get("valor_unitario", 0))
        self.spin_valor_total.setValue(r.get("valor_total", 0))

    def _validar_salvar(self):
        if not self.cmb_produto.currentText().strip():
            self._msg_erro("Informe o nome do produto.")
            self.cmb_produto.setFocus()
            return
        if self._get_qtd() <= 0:
            self._msg_erro("A quantidade deve ser maior que zero.")
            self.txt_quantidade.setFocus()
            return
        if not self.txt_comprador.text().strip():
            self._msg_erro("Informe o nome do comprador.")
            self.txt_comprador.setFocus()
            return
        if self.spin_valor_unitario.value() <= 0 and self.spin_valor_total.value() <= 0:
            self._msg_erro("Informe o valor unitário ou o valor total.")
            self.spin_valor_unitario.setFocus()
            return
        self.accept()

    def _msg_erro(self, texto):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Validação")
        msg.setText(texto)
        msg.setStyleSheet("""
            QMessageBox { background: white; }
            QMessageBox QLabel { color: #333; font-size: 13px; }
            QPushButton {
                padding: 8px 20px; background: #2d6a2d; color: white;
                border: none; border-radius: 6px; font-weight: 700; min-width: 80px;
            }
            QPushButton:hover { background: #3e8a3e; }
        """)
        msg.exec()

    def obter_dados(self):
        return {
            "data": self.date_data.date().toString("yyyy-MM-dd"),
            "produto": self.cmb_produto.currentText().strip(),
            "quantidade_kg": self._get_qtd(),
            "comprador": self.txt_comprador.text().strip(),
            "valor_unitario": self.spin_valor_unitario.value(),
            "valor_total": self.spin_valor_total.value(),
        }

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class VendasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.controller = VendasController()
        self._setup_ui()
        self._popular_compradores()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Vendas")
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

        lbl_filtro = QLabel("Filtrar Comprador:")
        lbl_filtro.setStyleSheet("color: #555; font-size: 12px; font-weight: 700; letter-spacing: 1px;")
        toolbar.addWidget(lbl_filtro)

        self.cmb_filtro_comprador = QComboBox()
        self.cmb_filtro_comprador.setStyleSheet("""
            QComboBox {
                padding: 8px 14px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
                background: #fafafa;
                min-width: 220px;
                color: #000;
            }
            QComboBox:focus {
                border-color: #2d6a2d;
                background: white;
            }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """)
        self.cmb_filtro_comprador.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_comprador)

        toolbar.addStretch()

        self.btn_novo = QPushButton("+ Nova Venda")
        self.btn_novo.setCursor(Qt.PointingHandCursor)
        self.btn_novo.setFixedHeight(40)
        self.btn_novo.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a4a1a, stop:1 #2d6a2d);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d6a2d, stop:1 #3e8a3e);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f3a0f, stop:1 #1a5a1a);
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
                padding: 8px 16px; background: #27ae60; color: white;
                border: none; border-radius: 8px; font-weight: 700; font-size: 12px;
            }
            QPushButton:hover { background: #2ecc71; }
            QPushButton:pressed { background: #1e8449; }
        """)
        btn_exportar.clicked.connect(self._exportar)
        toolbar.addWidget(btn_exportar)

        card_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Data", "Produto", "Quantidade (Kg)", "Comprador",
             "Valor Unitário", "Valor Total"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.doubleClicked.connect(self._editar)

        header_view = self.table.horizontalHeader()
        stretch = QHeaderView.Stretch
        header_view.setSectionResizeMode(0, stretch)
        header_view.setSectionResizeMode(1, stretch)
        header_view.setSectionResizeMode(2, stretch)
        header_view.setSectionResizeMode(3, stretch)
        header_view.setSectionResizeMode(4, stretch)
        header_view.setSectionResizeMode(5, stretch)
        header_view.setSectionResizeMode(6, stretch)

        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background: #ffffff;
                gridline-color: transparent;
                font-size: 13px;
                color: #000;
                selection-background-color: #d4d4d4;
            }
            QTableWidget::item {
                padding: 8px 14px;
            }
            QTableWidget::item:selected {
                background: #d4d4d4;
                color: #1a1a1a;
            }
            QTableWidget::item:hover {
                background: #dcdcdc;
            }
            QHeaderView::section {
                background: #f5f7f5;
                color: #1a3a1a;
                padding: 10px 14px;
                border: none;
                border-bottom: 2px solid #2d6a2d;
                border-right: 1px solid #e8e8e8;
                font-weight: 700;
                font-size: 12px;
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
        self.lbl_resumo.setStyleSheet("color: #1a3a1a; font-size: 14px; font-weight: 700; padding: 10px 0 2px 0;")
        self.lbl_resumo.setAlignment(Qt.AlignRight)
        card_layout.addWidget(self.lbl_resumo)

        layout.addWidget(card)

    def _fmt_num(self, val):
        return f"{val:_.0f}".replace("_", ".")

    def _fmt_money(self, val):
        return f"R$ {val:_.2f}".replace("_", ".").replace(".", ",")

    def _fmt_qtd(self, val):
        if val == int(val):
            return str(int(val))
        return f"{val:.3f}".rstrip("0").rstrip(".")

    def _popular_compradores(self):
        self.cmb_filtro_comprador.blockSignals(True)
        atual = self.cmb_filtro_comprador.currentText()
        self.cmb_filtro_comprador.clear()
        self.cmb_filtro_comprador.addItem("Todos os compradores", None)
        compradores = self.controller.listar_compradores()
        for nome in compradores:
            self.cmb_filtro_comprador.addItem(nome, nome)
        idx = self.cmb_filtro_comprador.findText(atual)
        if idx >= 0:
            self.cmb_filtro_comprador.setCurrentIndex(idx)
        self.cmb_filtro_comprador.blockSignals(False)

    def _carregar_dados(self):
        comprador = self.cmb_filtro_comprador.currentData() or None
        registros = self.controller.listar(comprador=comprador)
        self.table.setRowCount(len(registros))
        total_kg = total_valor = 0
        for i, r in enumerate(registros):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            self.table.setItem(i, 1, QTableWidgetItem(data_str))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("produto", "")))
            self.table.setItem(i, 3, QTableWidgetItem(self._fmt_qtd(r.get("quantidade_kg", 0))))
            self.table.setItem(i, 4, QTableWidgetItem(r.get("comprador", "")))
            self.table.setItem(i, 5, QTableWidgetItem(self._fmt_money(r.get("valor_unitario", 0))))
            self.table.setItem(i, 6, QTableWidgetItem(self._fmt_money(r.get("valor_total", 0))))
            total_kg += r.get("quantidade_kg", 0) or 0
            total_valor += r.get("valor_total", 0) or 0

        self.lbl_resumo.setText(
            f"Total: {self._fmt_qtd(total_kg)} kg  |  "
            f"Valor Total: {self._fmt_money(total_valor)}"
        )

    def _msg_box(self, icone, titulo, texto, botoes=None):
        msg = QMessageBox(self)
        msg.setIcon(icone)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        if botoes:
            msg.setStandardButtons(botoes)
        msg.setStyleSheet("""
            QMessageBox { background: white; color: #333; }
            QMessageBox QLabel { color: #333; font-size: 13px; }
            QPushButton {
                padding: 8px 20px; background: #2d6a2d; color: white;
                border: none; border-radius: 6px; font-weight: 700; min-width: 80px;
            }
            QPushButton:hover { background: #3e8a3e; }
        """)
        return msg.exec()

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
        dialog = VendasDialog(self)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.salvar(dados)
            self._popular_compradores()
            self._carregar_dados()
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione uma venda para editar.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        registro = self.controller.buscar_por_id(registro_id)
        if not registro:
            self._msg_box(QMessageBox.Warning, "Erro", "Venda não encontrada.")
            return
        dialog = VendasDialog(self, registro)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.atualizar(registro_id, dados)
            self._popular_compradores()
            self._carregar_dados()
        self._timer.start(2000)

    def _excluir(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione uma venda para excluir.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        produto = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir a venda de '{produto}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(registro_id)
            self._popular_compradores()
            self._carregar_dados()

    def _exportar(self):
        comprador = self.cmb_filtro_comprador.currentData() or None
        registros = self.controller.listar(comprador=comprador)
        cabecalhos = ["ID", "Data", "Produto", "Quantidade (Kg)", "Comprador",
                       "Valor Unitário", "Valor Total"]
        dados = []
        for r in registros:
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            dados.append((
                r["id"], data_str, r.get("produto", ""),
                r.get("quantidade_kg", 0), r.get("comprador", ""),
                r.get("valor_unitario", 0), r.get("valor_total", 0),
            ))
        exportar_excel(self, "relatorio_vendas.xlsx", "Vendas", cabecalhos, dados)
