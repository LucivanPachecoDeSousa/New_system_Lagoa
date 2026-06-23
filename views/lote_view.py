from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QDoubleSpinBox,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from controllers.lote_controller import LoteController
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit


class LoteDialog(QDialog):
    def __init__(self, parent=None, lote=None):
        super().__init__(parent)
        self.lote = lote
        self.controller = LoteController()
        self.fazenda_spins = {}
        self.lbl_total_rateio = None
        self.setWindowTitle("Editar Lote" if lote else "Novo Lote")
        self.setMinimumWidth(880)
        self.setMinimumHeight(720)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self._setup_ui()
        self.showMaximized()
        if lote:
            self._preencher(lote)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setMinimumSize(840, 680)
        card.setStyleSheet("""
            QFrame { background: white; border-radius: 20px; }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 20, 30, 20)
        card_layout.setSpacing(8)

        title = QLabel("Editar Lote" if self.lote else "Novo Lote")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a3a1a; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        lbl_tipo = QLabel("TIPO")
        lbl_tipo.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")

        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItem("Carregamento", "carregamento")
        self.cmb_tipo.addItem("Adubo", "adubo")
        self.cmb_tipo.addItem("Calcário", "calcario")
        self.cmb_tipo.setStyleSheet(self._input_style())
        self.cmb_tipo.currentIndexChanged.connect(self._toggle_campos)
        card_layout.addWidget(lbl_tipo)
        card_layout.addWidget(self.cmb_tipo)

        lbl_entidade = QLabel("ENTIDADE")
        lbl_entidade.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")

        self.cmb_entidade = QComboBox()
        self.cmb_entidade.setStyleSheet(self._input_style())
        entidades = self.controller.listar_entidades()
        for e in entidades:
            self.cmb_entidade.addItem(f"{e['razao_social']} ({e['cnpj_cpf']})", e["id"])
        self.entidade_widget = lbl_entidade
        self.entidade_combo = self.cmb_entidade
        card_layout.addWidget(lbl_entidade)
        card_layout.addWidget(self.cmb_entidade)

        lbl_lote = QLabel("NOME DO LOTE")
        lbl_lote.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")

        self.txt_nome_lote = UpperCaseLineEdit()
        self.txt_nome_lote.setPlaceholderText("Nome do lote")
        self.txt_nome_lote.setStyleSheet(self._input_style())
        card_layout.addWidget(lbl_lote)
        card_layout.addWidget(self.txt_nome_lote)

        lbl_adubo_tipo = QLabel("TIPO DE ADUBO")
        lbl_adubo_tipo.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")

        self.cmb_adubo_tipo = QComboBox()
        self.cmb_adubo_tipo.setEditable(True)
        self.cmb_adubo_tipo.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_adubo_tipo.lineEdit().setPlaceholderText("Digite ou selecione o tipo de adubo")
        self.cmb_adubo_tipo.setStyleSheet(self._input_style())
        tipos = self.controller.listar_tipos_adubo()
        for t in tipos:
            self.cmb_adubo_tipo.addItem(t["nome"], t["id"])
        self.adubo_widget = lbl_adubo_tipo
        self.adubo_combo = self.cmb_adubo_tipo
        card_layout.addWidget(lbl_adubo_tipo)
        card_layout.addWidget(self.cmb_adubo_tipo)

        lbl_calcario_tipo = QLabel("TIPO DE CALCÁRIO")
        lbl_calcario_tipo.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")

        self.cmb_calcario_tipo = QComboBox()
        self.cmb_calcario_tipo.setEditable(True)
        self.cmb_calcario_tipo.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_calcario_tipo.lineEdit().setPlaceholderText("Digite ou selecione o tipo de calcário")
        self.cmb_calcario_tipo.setStyleSheet(self._input_style())
        tipos_calc = self.controller.listar_tipos_calcario()
        for t in tipos_calc:
            self.cmb_calcario_tipo.addItem(t["nome"], t["id"])
        self.calcario_widget = lbl_calcario_tipo
        self.calcario_combo = self.cmb_calcario_tipo
        card_layout.addWidget(lbl_calcario_tipo)
        card_layout.addWidget(self.cmb_calcario_tipo)

        lbl_qtd = QLabel("QUANTIDADE DO PEDIDO")
        lbl_qtd.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")

        self.spn_quantidade = QDoubleSpinBox()
        self.spn_quantidade.setRange(0, 999999)
        self.spn_quantidade.setDecimals(3)
        self.spn_quantidade.setStyleSheet(self._input_style())

        self.cmb_unidade = QComboBox()
        self.cmb_unidade.addItems(["TON", "KG", "BAG"])
        self.cmb_unidade.setStyleSheet(self._input_style())

        qtd_row = QWidget()
        qtd_row_layout = QHBoxLayout(qtd_row)
        qtd_row_layout.setContentsMargins(0, 0, 0, 0)
        qtd_row_layout.setSpacing(8)
        qtd_row_layout.addWidget(self.spn_quantidade, 1)
        qtd_row_layout.addWidget(self.cmb_unidade)

        self.qtd_widgets = [lbl_qtd, qtd_row]
        card_layout.addWidget(lbl_qtd)
        card_layout.addWidget(qtd_row)

        lbl_valor_unitario = QLabel("VALOR UNITÁRIO (R$)")
        lbl_valor_unitario.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")

        self.spn_valor_unitario = QDoubleSpinBox()
        self.spn_valor_unitario.setRange(0, 999999)
        self.spn_valor_unitario.setDecimals(4)
        self.spn_valor_unitario.setPrefix("R$ ")
        self.spn_valor_unitario.setStyleSheet(self._input_style())
        self.spn_valor_unitario.setVisible(False)
        self.lbl_valor_unitario = lbl_valor_unitario
        card_layout.addWidget(lbl_valor_unitario)
        card_layout.addWidget(self.spn_valor_unitario)

        lbl_fazendas = QLabel("RATEIO POR FAZENDA")
        lbl_fazendas.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-top: 5px;")
        self.fazenda_header = lbl_fazendas
        card_layout.addWidget(lbl_fazendas)

        self.fazendas_widget = QWidget()
        fz_layout = QVBoxLayout(self.fazendas_widget)
        fz_layout.setContentsMargins(0, 0, 0, 0)
        fz_layout.setSpacing(5)

        fazendas = self.controller.listar_fazendas()
        for f in fazendas:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            nome = QLabel(f["nome"])
            nome.setStyleSheet("color: #333; font-size: 13px; font-weight: 600;")
            nome.setFixedWidth(160)
            row_layout.addWidget(nome)

            spin = QDoubleSpinBox()
            spin.setRange(0, 999999)
            spin.setDecimals(3)
            spin.setMinimumWidth(200)
            spin.setStyleSheet(self._input_style())
            spin.valueChanged.connect(self._atualizar_total_rateio)
            row_layout.addWidget(spin, 1)

            self.fazenda_spins[f["id"]] = {"spin": spin, "nome": f["nome"]}
            fz_layout.addWidget(row)

        card_layout.addWidget(self.fazendas_widget)

        self.lbl_total_rateio = QLabel("Total rateado: 0")
        self.lbl_total_rateio.setStyleSheet("color: #888; font-size: 12px; font-style: italic;")
        self.lbl_total_rateio.setAlignment(Qt.AlignRight)
        card_layout.addWidget(self.lbl_total_rateio)

        self.fazenda_section = [lbl_fazendas, self.fazendas_widget, self.lbl_total_rateio]

        card_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setFixedHeight(44)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                padding: 10px; background: #e0e0e0; color: #333;
                border: none; border-radius: 10px; font-weight: 700; font-size: 13px;
            }
            QPushButton:hover { background: #ccc; }
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setCursor(Qt.PointingHandCursor)
        btn_salvar.setFixedHeight(44)
        btn_salvar.setStyleSheet(self._btn_style())
        btn_salvar.clicked.connect(self._validar_salvar)
        btn_layout.addWidget(btn_salvar)

        card_layout.addLayout(btn_layout)
        layout.addWidget(card)

        self._toggle_campos()

    def _toggle_campos(self):
        tipo = self.cmb_tipo.currentData()

        show_entidade = tipo in ("carregamento", "calcario")
        self.entidade_widget.setVisible(show_entidade)
        self.entidade_combo.setVisible(show_entidade)

        show_valor = tipo == "carregamento"
        self.lbl_valor_unitario.setVisible(show_valor)
        self.spn_valor_unitario.setVisible(show_valor)

        show_adubo = tipo == "adubo"
        show_calcario = tipo == "calcario"
        show_qtd = tipo in ("adubo", "carregamento")
        self.adubo_widget.setVisible(show_adubo)
        self.adubo_combo.setVisible(show_adubo)
        self.calcario_widget.setVisible(show_calcario)
        self.calcario_combo.setVisible(show_calcario)
        for w in self.qtd_widgets:
            w.setVisible(show_qtd)
        for w in self.fazenda_section:
            w.setVisible(show_adubo)

    def _atualizar_total_rateio(self):
        total = sum(d["spin"].value() for d in self.fazenda_spins.values())
        pedido = self.spn_quantidade.value()
        self.lbl_total_rateio.setText(f"Total rateado: {total:.3f} / {pedido:.3f}")
        cor = "#e74c3c" if total > pedido else "#2d6a2d" if total == pedido and total > 0 else "#888"
        self.lbl_total_rateio.setStyleSheet(f"color: {cor}; font-size: 12px; font-style: italic;")

    def _preencher(self, l):
        idx = self.cmb_tipo.findData(l["tipo"])
        if idx >= 0:
            self.cmb_tipo.setCurrentIndex(idx)

        if l.get("entidade_id"):
            idx = self.cmb_entidade.findData(l["entidade_id"])
            if idx >= 0:
                self.cmb_entidade.setCurrentIndex(idx)

        self.txt_nome_lote.setText(l.get("nome_lote", ""))

        if l.get("tipo_adubo_id"):
            idx = self.cmb_adubo_tipo.findData(l["tipo_adubo_id"])
            if idx >= 0:
                self.cmb_adubo_tipo.setCurrentIndex(idx)

        if l.get("tipo_calcario_id"):
            idx = self.cmb_calcario_tipo.findData(l["tipo_calcario_id"])
            if idx >= 0:
                self.cmb_calcario_tipo.setCurrentIndex(idx)
            else:
                self.cmb_calcario_tipo.setCurrentText(l.get("tipo_calcario_nome", ""))

        if l.get("quantidade_pedido"):
            self.spn_quantidade.setValue(float(l["quantidade_pedido"]))
        if l.get("unidade"):
            idx = self.cmb_unidade.findText(l["unidade"])
            if idx >= 0:
                self.cmb_unidade.setCurrentIndex(idx)

        if l.get("valor_unitario"):
            self.spn_valor_unitario.setValue(float(l["valor_unitario"]))

        for item in l.get("fazendas", []):
            fid = item["fazenda_id"]
            if fid in self.fazenda_spins:
                self.fazenda_spins[fid]["spin"].setValue(float(item["quantidade"]))

    def _validar_salvar(self):
        if not self.txt_nome_lote.text().strip():
            self._msg_box(QMessageBox.Warning, "Validação", "Nome do lote é obrigatório.")
            return
        tipo = self.cmb_tipo.currentData()
        if tipo in ("carregamento", "calcario") and self.cmb_entidade.count() > 0 and self.cmb_entidade.currentData() is None:
            self._msg_box(QMessageBox.Warning, "Validação", "Selecione uma entidade.")
            return

        if tipo == "adubo":
            total_rateio = sum(d["spin"].value() for d in self.fazenda_spins.values())
            pedido = self.spn_quantidade.value()
            if total_rateio > pedido:
                self._msg_box(QMessageBox.Warning, "Validação",
                    f"O total rateado ({total_rateio:.3f}) excede o pedido ({pedido:.3f}).")
                return

        self.accept()

    def obter_dados(self):
        tipo = self.cmb_tipo.currentData()

        tipo_adubo_id = None
        if tipo == "adubo":
            texto_adubo = self.cmb_adubo_tipo.currentText().strip().upper()
            if texto_adubo:
                tipo_adubo_id = self.controller.adicionar_tipo_adubo(texto_adubo)

        tipo_calcario_id = None
        if tipo == "calcario":
            texto_calc = self.cmb_calcario_tipo.currentText().strip().upper()
            if texto_calc:
                tipo_calcario_id = self.controller.adicionar_tipo_calcario(texto_calc)

        fazendas = []
        for fid, d in self.fazenda_spins.items():
            qtd = d["spin"].value()
            if qtd > 0:
                fazendas.append({"fazenda_id": fid, "quantidade": qtd})

        tem_qtd = tipo in ("adubo", "carregamento")

        return {
            "tipo": tipo,
            "entidade_id": self.cmb_entidade.currentData() if tipo in ("carregamento", "calcario") else None,
            "nome_lote": self.txt_nome_lote.text().strip(),
            "tipo_adubo_id": tipo_adubo_id,
            "tipo_calcario_id": tipo_calcario_id,
            "quantidade_pedido": self.spn_quantidade.value() if tem_qtd else None,
            "unidade": self.cmb_unidade.currentText() if tem_qtd else None,
            "valor_unitario": self.spn_valor_unitario.value(),
            "fazendas": fazendas,
        }

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

    def _input_style(self):
        return """
            QLineEdit, QComboBox, QDoubleSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
                background: #fafafa;
                color: #000;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border-color: #2d6a2d;
                background: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #ddd;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """

    def _btn_style(self):
        return """
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
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f3a0f, stop:1 #1a5a1a);
            }
        """

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class LoteView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = LoteController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Lotes / Contratos")
        header.setStyleSheet("color: white; font-size: 22px; font-weight: 700; letter-spacing: 2px;")
        layout.addWidget(header)

        card = QFrame()
        card.setStyleSheet("""
            QFrame { background: white; border-radius: 20px; }
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

        self.cmb_filtro_tipo = QComboBox()
        self.cmb_filtro_tipo.addItem("Todos os tipos", None)
        self.cmb_filtro_tipo.addItem("Carregamento", "carregamento")
        self.cmb_filtro_tipo.addItem("Adubo", "adubo")
        self.cmb_filtro_tipo.addItem("Calcário", "calcario")
        self.cmb_filtro_tipo.setStyleSheet("""
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
                background: #fafafa;
                min-width: 160px;
                color: #000;
            }
            QComboBox:focus { border-color: #2d6a2d; background: white; }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """)
        self.cmb_filtro_tipo.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_tipo)

        self.txt_busca = UpperCaseLineEdit()
        self.txt_busca.setPlaceholderText("Buscar lote...")
        self.txt_busca.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
                background: #fafafa;
                min-width: 250px;
                color: #333;
            }
            QLineEdit:focus { border-color: #2d6a2d; background: white; }
        """)
        self.txt_busca.textChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.txt_busca)

        btn_atualizar = QPushButton("🔄 Atualizar")
        btn_atualizar.setCursor(Qt.PointingHandCursor)
        btn_atualizar.setFixedHeight(40)
        btn_atualizar.setStyleSheet("""
            QPushButton {
                padding: 8px 16px; background: #3498db; color: white;
                border: none; border-radius: 8px; font-weight: 700; font-size: 12px;
            }
            QPushButton:hover { background: #5dade2; }
            QPushButton:pressed { background: #2980b9; }
        """)
        btn_atualizar.clicked.connect(self._carregar_dados)
        toolbar.addWidget(btn_atualizar)

        toolbar.addStretch()

        self.btn_novo = QPushButton("+ Novo Lote")
        self.btn_novo.setCursor(Qt.PointingHandCursor)
        self.btn_novo.setFixedHeight(40)
        self.btn_novo.setStyleSheet(self._btn_primary())
        self.btn_novo.clicked.connect(self._novo)
        toolbar.addWidget(self.btn_novo)

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setCursor(Qt.PointingHandCursor)
        self.btn_editar.setFixedHeight(40)
        self.btn_editar.setStyleSheet(self._btn_warning())
        self.btn_editar.clicked.connect(self._editar)
        toolbar.addWidget(self.btn_editar)

        self.btn_encerrar = QPushButton("Encerrar")
        self.btn_encerrar.setCursor(Qt.PointingHandCursor)
        self.btn_encerrar.setFixedHeight(40)
        self.btn_encerrar.setStyleSheet(self._btn_danger())
        self.btn_encerrar.clicked.connect(self._encerrar)
        toolbar.addWidget(self.btn_encerrar)

        self.btn_reativar = QPushButton("Reativar")
        self.btn_reativar.setCursor(Qt.PointingHandCursor)
        self.btn_reativar.setFixedHeight(40)
        self.btn_reativar.setStyleSheet(self._btn_success())
        self.btn_reativar.clicked.connect(self._reativar)
        toolbar.addWidget(self.btn_reativar)

        card_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tipo", "Entidade", "Lote", "Tipo", "Qtd", "Unid.", "Criado em", "Status"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.doubleClicked.connect(self._editar)

        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.Stretch)
        h.setSectionResizeMode(3, QHeaderView.Stretch)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(8, QHeaderView.ResizeToContents)

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
        layout.addWidget(card)

    def _carregar_dados(self):
        busca = self.txt_busca.text().strip().lower()
        filtro_tipo = self.cmb_filtro_tipo.currentData()
        lotes = self.controller.listar()
        if filtro_tipo:
            lotes = [l for l in lotes if l["tipo"] == filtro_tipo]
        if busca:
            lotes = [
                l for l in lotes
                if busca in l["nome_lote"].lower()
                or busca in (l.get("entidade_nome") or "").lower()
            ]

        tipos_label = {"carregamento": "Carregamento", "adubo": "Adubo", "calcario": "Calcário"}

        self.table.setRowCount(len(lotes))
        for i, l in enumerate(lotes):
            self.table.setItem(i, 0, QTableWidgetItem(str(l["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(tipos_label.get(l["tipo"], l["tipo"])))
            self.table.setItem(i, 2, QTableWidgetItem(l.get("entidade_nome", "")))
            self.table.setItem(i, 3, QTableWidgetItem(l["nome_lote"]))
            nome_tipo = l.get("tipo_adubo_nome") or l.get("tipo_calcario_nome") or ""
            self.table.setItem(i, 4, QTableWidgetItem(nome_tipo))
            qtd = l.get("quantidade_pedido") or 0
            self.table.setItem(i, 5, QTableWidgetItem(f"{qtd:.3f}"))
            self.table.setItem(i, 6, QTableWidgetItem(l.get("unidade", "")))
            dt = l.get("created_at", "")
            if dt:
                qd = QDate.fromString(dt[:10], "yyyy-MM-dd")
                dt = qd.toString("dd/MM/yyyy") if qd.isValid() else dt
            self.table.setItem(i, 7, QTableWidgetItem(dt))
            ativo = l.get("ativo", 1)
            status_item = QTableWidgetItem("Ativo" if ativo else "Inativo")
            status_item.setForeground(QColor("#2d6a2d") if ativo else QColor("#e74c3c"))
            self.table.setItem(i, 8, status_item)

    def _novo(self):
        dialog = LoteDialog(self)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.salvar(dados)
            self._carregar_dados()
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um lote para editar.")
            return
        if not self._confirmar_senha():
            return
        lote_id = int(self.table.item(row, 0).text())
        lote = self.controller.buscar_por_id(lote_id)
        if not lote:
            self._msg_box(QMessageBox.Warning, "Erro", "Lote não encontrado.")
            return
        dialog = LoteDialog(self, lote)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.atualizar(lote_id, dados)
            self._carregar_dados()
        self._timer.start(2000)

    def _encerrar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um lote para encerrar.")
            return
        lote_id = int(self.table.item(row, 0).text())
        nome = self.table.item(row, 3).text()
        ativo = self.table.item(row, 8).text() == "Ativo"
        if not ativo:
            self._msg_box(QMessageBox.Information, "Aviso", "Este lote já está encerrado.")
            return
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja encerrar o lote '{nome}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(lote_id)
            self._carregar_dados()

    def _reativar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um lote para reativar.")
            return
        lote_id = int(self.table.item(row, 0).text())
        nome = self.table.item(row, 3).text()
        ativo = self.table.item(row, 8).text() == "Ativo"
        if ativo:
            self._msg_box(QMessageBox.Information, "Aviso", "Este lote já está ativo.")
            return

        senha, ok = QInputDialog.getText(self, "Autenticação", "Digite sua senha:", QLineEdit.Password)
        if not ok or not senha:
            return

        auth = AuthController()
        if not auth.verificar_senha(senha):
            self._msg_box(QMessageBox.Warning, "Erro", "Senha incorreta.")
            return

        self.controller.reativar(lote_id)
        self._msg_box(QMessageBox.Information, "Sucesso", "Lote reativado com sucesso.")
        self._carregar_dados()

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

    def _btn_primary(self):
        return """
            QPushButton {
                padding: 8px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a4a1a, stop:1 #2d6a2d);
                color: white; border: none; border-radius: 8px;
                font-weight: 700; font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d6a2d, stop:1 #3e8a3e);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f3a0f, stop:1 #1a5a1a);
            }
        """

    def _btn_warning(self):
        return """
            QPushButton {
                padding: 8px 20px; background: #f39c12; color: white;
                border: none; border-radius: 8px; font-weight: 700; font-size: 12px;
            }
            QPushButton:hover { background: #f1c40f; }
            QPushButton:pressed { background: #d68910; }
        """

    def _btn_danger(self):
        return """
            QPushButton {
                padding: 8px 20px; background: #e74c3c; color: white;
                border: none; border-radius: 8px; font-weight: 700; font-size: 12px;
            }
            QPushButton:hover { background: #ec7063; }
            QPushButton:pressed { background: #c0392b; }
        """

    def _btn_success(self):
        return """
            QPushButton {
                padding: 8px 20px; background: #27ae60; color: white;
                border: none; border-radius: 8px; font-weight: 700; font-size: 12px;
            }
            QPushButton:hover { background: #2ecc71; }
            QPushButton:pressed { background: #1e8449; }
        """
