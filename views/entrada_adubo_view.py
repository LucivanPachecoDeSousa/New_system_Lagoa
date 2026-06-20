from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QDoubleSpinBox,
    QSpinBox, QDateEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from collections import defaultdict
from controllers.entrada_adubo_controller import EntradaAduboController
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit, estilizar_calendario


class EntradaAduboDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.controller = EntradaAduboController()
        self.setWindowTitle("Editar Entrada" if registro else "Nova Entrada")
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
        card.setMinimumSize(680, 620)
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

        title = QLabel("Editar Entrada" if self.registro else "Nova Entrada de Adubo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a3a1a; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        card_layout.addSpacing(10)

        # Primeira linha: Data e Placa
        linha1 = QHBoxLayout()
        linha1.setSpacing(12)
        g1 = self._grupo("DATA", self._criar_data())
        g2 = self._grupo("PLACA", self._criar_placa())
        linha1.addLayout(g1)
        linha1.addLayout(g2)
        card_layout.addLayout(linha1)

        # Segunda linha: Tipo de Adubo e Lote
        linha2 = QHBoxLayout()
        linha2.setSpacing(12)
        g3 = self._grupo("TIPO DE ADUBO", self._criar_adubo())
        g4 = self._grupo("LOTE", self._criar_lote())
        linha2.addLayout(g3)
        linha2.addLayout(g4)
        card_layout.addLayout(linha2)

        # Terceira linha: Fornecedor e Fazenda
        linha3 = QHBoxLayout()
        linha3.setSpacing(12)
        g5 = self._grupo("FORNECEDOR", self._criar_entidade())
        g6 = self._grupo("FAZENDA DESTINO", self._criar_fazenda())
        linha3.addLayout(g5)
        linha3.addLayout(g6)
        card_layout.addLayout(linha3)

        # Quarta linha: Quantidade (bag) e Peso Total (kg)
        linha4 = QHBoxLayout()
        linha4.setSpacing(12)
        g7 = self._grupo("QUANTIDADE (BAG)", self._criar_quantidade_bag())
        g8 = self._grupo("PESO TOTAL (KG)", self._criar_peso_total())
        linha4.addLayout(g7)
        linha4.addLayout(g8)
        card_layout.addLayout(linha4)

        # Quinta linha: Motorista e NF
        linha5 = QHBoxLayout()
        linha5.setSpacing(12)
        g9 = self._grupo("MOTORISTA", self._criar_motorista())
        g10 = self._grupo("NÚMERO NF", self._criar_numero_nf())
        linha5.addLayout(g9)
        linha5.addLayout(g10)
        card_layout.addLayout(linha5)

        # Observação
        lbl_obs = QLabel("OBSERVAÇÃO")
        lbl_obs.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_obs)

        self.txt_obs = UpperCaseLineEdit()
        self.txt_obs.setPlaceholderText("Observação (opcional)")
        self.txt_obs.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_obs)

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

    def _criar_placa(self):
        self.txt_placa = UpperCaseLineEdit()
        self.txt_placa.setPlaceholderText("Placa do veículo")
        self.txt_placa.setMaxLength(8)
        self.txt_placa.setStyleSheet(self._input_style())
        return self.txt_placa

    def _criar_adubo(self):
        self.cmb_adubo = QComboBox()
        self.cmb_adubo.setEditable(True)
        self.cmb_adubo.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_adubo.lineEdit().setPlaceholderText("Digite ou selecione")
        self.cmb_adubo.setStyleSheet(self._input_style())
        tipos = self.controller.listar_tipos_adubo()
        for t in tipos:
            self.cmb_adubo.addItem(t["nome"], t["id"])
        self.cmb_adubo.setCurrentText("")
        return self.cmb_adubo

    def _criar_lote(self):
        self.cmb_lote = QComboBox()
        self.cmb_lote.addItem("Sem lote", None)
        lotes = self.controller.listar_lotes_adubo()
        for l in lotes:
            self.cmb_lote.addItem(f"{l['nome_lote']} - {l.get('entidade_nome', '')}", l["id"])
        self.cmb_lote.setStyleSheet(self._input_style())
        return self.cmb_lote

    def _criar_entidade(self):
        self.cmb_entidade = QComboBox()
        self.cmb_entidade.setStyleSheet(self._input_style())
        entidades = self.controller.listar_entidades()
        for e in entidades:
            self.cmb_entidade.addItem(f"{e['razao_social']} ({e['cnpj_cpf']})", e["id"])
        return self.cmb_entidade

    def _criar_fazenda(self):
        self.cmb_fazenda = QComboBox()
        self.cmb_fazenda.addItem("Selecione a fazenda", None)
        fazendas = self.controller.listar_fazendas()
        for f in fazendas:
            self.cmb_fazenda.addItem(f["nome"], f["id"])
        self.cmb_fazenda.setStyleSheet(self._input_style())
        return self.cmb_fazenda

    def _criar_quantidade_bag(self):
        self.spin_bag = QSpinBox()
        self.spin_bag.setRange(0, 999999)
        self.spin_bag.setFixedHeight(44)
        self.spin_bag.setStyleSheet(self._field_style())
        return self.spin_bag

    def _criar_peso_total(self):
        self.spin_peso = QDoubleSpinBox()
        self.spin_peso.setRange(0, 999999)
        self.spin_peso.setDecimals(0)
        self.spin_peso.setFixedHeight(44)
        self.spin_peso.setStyleSheet(self._field_style())
        return self.spin_peso

    def _criar_motorista(self):
        self.txt_motorista = UpperCaseLineEdit()
        self.txt_motorista.setPlaceholderText("Nome do motorista")
        self.txt_motorista.setStyleSheet(self._input_style())
        return self.txt_motorista

    def _criar_numero_nf(self):
        self.txt_nf = UpperCaseLineEdit()
        self.txt_nf.setPlaceholderText("Número da Nota Fiscal")
        self.txt_nf.setStyleSheet(self._input_style())
        return self.txt_nf

    def _field_style(self):
        return """
            QDateEdit, QSpinBox, QDoubleSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
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

    def _preencher(self, r):
        qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
        if qd.isValid():
            self.date_data.setDate(qd)
        self.txt_placa.setText(r.get("placa", ""))
        idx = self.cmb_adubo.findData(r["adubo_tipo_id"])
        if idx >= 0:
            self.cmb_adubo.setCurrentIndex(idx)
        else:
            self.cmb_adubo.setCurrentText(r.get("adubo_nome", ""))
        idx_lote = self.cmb_lote.findData(r.get("lote_id"))
        if idx_lote >= 0:
            self.cmb_lote.setCurrentIndex(idx_lote)
        idx_ent = self.cmb_entidade.findData(r["entidade_id"])
        if idx_ent >= 0:
            self.cmb_entidade.setCurrentIndex(idx_ent)
        idx_faz = self.cmb_fazenda.findData(r.get("fazenda_id"))
        if idx_faz >= 0:
            self.cmb_fazenda.setCurrentIndex(idx_faz)
        self.spin_bag.setValue(r.get("quantidade_bag", 0))
        self.spin_peso.setValue(r.get("peso_total_kg", 0))
        self.txt_motorista.setText(r.get("motorista", ""))
        self.txt_nf.setText(r.get("numero_nf", ""))
        self.txt_obs.setText(r.get("observacao", ""))

    def _validar_salvar(self):
        adubo = self.cmb_adubo.currentText().strip()
        if not adubo:
            self._msg_erro("O tipo de adubo é obrigatório.")
            self.cmb_adubo.setFocus()
            return
        if self.cmb_entidade.currentData() is None:
            self._msg_erro("Selecione um fornecedor.")
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
        adubo_nome = self.cmb_adubo.currentText().strip().upper()
        adubo_id = self.cmb_adubo.currentData()
        if adubo_id is None:
            adubo_id = self.controller.adicionar_tipo_adubo(adubo_nome)
        return {
            "data": self.date_data.date().toString("yyyy-MM-dd"),
            "adubo_tipo_id": adubo_id,
            "lote_id": self.cmb_lote.currentData(),
            "entidade_id": self.cmb_entidade.currentData(),
            "quantidade_bag": self.spin_bag.value(),
            "peso_total_kg": self.spin_peso.value(),
            "placa": self.txt_placa.text().strip(),
            "motorista": self.txt_motorista.text().strip(),
            "fazenda_id": self.cmb_fazenda.currentData(),
            "numero_nf": self.txt_nf.text().strip(),
            "observacao": self.txt_obs.text().strip(),
        }

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class EntradaAduboView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.controller = EntradaAduboController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Entradas de Adubo")
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

        self.cmb_filtro_adubo = QComboBox()
        self.cmb_filtro_adubo.addItem("Todos os adubos", None)
        tipos = self.controller.listar_tipos_adubo()
        for t in tipos:
            self.cmb_filtro_adubo.addItem(t["nome"], t["id"])
        self.cmb_filtro_adubo.setStyleSheet(self._combo_style())
        self.cmb_filtro_adubo.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_adubo)

        self.cmb_filtro_fazenda = QComboBox()
        self.cmb_filtro_fazenda.addItem("Todas as fazendas", None)
        fazendas = self.controller.listar_fazendas()
        for f in fazendas:
            self.cmb_filtro_fazenda.addItem(f["nome"], f["id"])
        self.cmb_filtro_fazenda.setStyleSheet(self._combo_style())
        self.cmb_filtro_fazenda.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_fazenda)

        toolbar.addStretch()

        self.btn_novo = QPushButton("+ Nova Entrada")
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

        card_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Data", "Adubo", "Lote", "Fornecedor", "Fazenda",
             "Bags", "Peso (kg)", "Placa", "Motorista", "NF"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.doubleClicked.connect(self._editar)

        header_view = self.table.horizontalHeader()
        resize = QHeaderView.ResizeToContents
        stretch = QHeaderView.Stretch
        header_view.setSectionResizeMode(0, resize)
        header_view.setSectionResizeMode(1, resize)
        header_view.setSectionResizeMode(2, stretch)
        header_view.setSectionResizeMode(3, stretch)
        header_view.setSectionResizeMode(4, stretch)
        header_view.setSectionResizeMode(5, stretch)
        header_view.setSectionResizeMode(6, resize)
        header_view.setSectionResizeMode(7, resize)
        header_view.setSectionResizeMode(8, resize)
        header_view.setSectionResizeMode(9, stretch)
        header_view.setSectionResizeMode(10, stretch)

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

        self.lbl_resumo_fazendas = QLabel()
        self.lbl_resumo_fazendas.setStyleSheet("color: #2d6a2d; font-size: 12px; font-weight: 600; padding: 0 0 10px 0;")
        self.lbl_resumo_fazendas.setAlignment(Qt.AlignRight)
        self.lbl_resumo_fazendas.setVisible(False)
        card_layout.addWidget(self.lbl_resumo_fazendas)

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

    def _fmt_num(self, val):
        return f"{val:_.0f}".replace("_", ".")

    def _carregar_dados(self):
        registros = self.controller.listar()
        adubo_id = self.cmb_filtro_adubo.currentData()
        if adubo_id:
            registros = [r for r in registros if r["adubo_tipo_id"] == adubo_id]
        fazenda_id = self.cmb_filtro_fazenda.currentData()
        if fazenda_id:
            registros = [r for r in registros if r["fazenda_id"] == fazenda_id]
        nome_adubo = self.cmb_filtro_adubo.currentText()
        nome_fazenda = self.cmb_filtro_fazenda.currentText()
        self.table.setRowCount(len(registros))
        total_bag = total_peso = 0
        for i, r in enumerate(registros):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            self.table.setItem(i, 1, QTableWidgetItem(data_str))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("adubo_nome", "")))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("nome_lote", "")))
            self.table.setItem(i, 4, QTableWidgetItem(r.get("entidade_nome", "")))
            self.table.setItem(i, 5, QTableWidgetItem(r.get("fazenda_nome", "")))
            self.table.setItem(i, 6, QTableWidgetItem(str(r.get("quantidade_bag", 0))))
            self.table.setItem(i, 7, QTableWidgetItem(self._fmt_num(r.get("peso_total_kg", 0))))
            self.table.setItem(i, 8, QTableWidgetItem(r.get("placa", "")))
            self.table.setItem(i, 9, QTableWidgetItem(r.get("motorista", "")))
            self.table.setItem(i, 10, QTableWidgetItem(r.get("numero_nf", "")))
            total_bag += r.get("quantidade_bag", 0) or 0
            total_peso += r.get("peso_total_kg", 0) or 0
        self.lbl_resumo.setText(
            f"{nome_adubo} | {nome_fazenda}  |  "
            f"Total: {self._fmt_num(total_bag)} bags  |  {self._fmt_num(total_peso)} kg"
        )
        self._atualizar_resumo_fazendas()

    def _atualizar_resumo_fazendas(self):
        adubo_id = self.cmb_filtro_adubo.currentData()
        saldo = self.controller.resumo_saldo_fazendas(adubo_id)
        linhas = []
        if saldo:
            for s in saldo:
                linhas.append(
                    f"{s['fazenda_nome']}: "
                    f"Recebido {self._fmt_num(s['entregue'])} bags"
                    + (f"  |  Previsto {self._fmt_num(s['esperado'])}"
                       f"  |  Falta {self._fmt_num(s['saldo'])} bags"
                       if s['esperado'] > 0 else "")
                )
        registros = self.controller.listar()
        if adubo_id:
            registros = [r for r in registros if r["adubo_tipo_id"] == adubo_id]
        por_fazenda = defaultdict(lambda: {"bags": 0, "peso": 0})
        for r in registros:
            nome = r.get("fazenda_nome") or "SEM FAZENDA"
            por_fazenda[nome]["bags"] += r.get("quantidade_bag", 0) or 0
            por_fazenda[nome]["peso"] += r.get("peso_total_kg", 0) or 0
        for nome, v in sorted(por_fazenda.items()):
            if not any(nome in l for l in linhas):
                linhas.append(
                    f"{nome}: {self._fmt_num(v['bags'])} bags  |  {self._fmt_num(v['peso'])} kg"
                )
        if linhas:
            self.lbl_resumo_fazendas.setText("\n".join(linhas))
            self.lbl_resumo_fazendas.setVisible(True)
        else:
            self.lbl_resumo_fazendas.setVisible(False)

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
        dialog = EntradaAduboDialog(self)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.salvar(dados)
            self._carregar_dados()
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione uma entrada para editar.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        registro = self.controller.buscar_por_id(registro_id)
        if not registro:
            self._msg_box(QMessageBox.Warning, "Erro", "Entrada não encontrada.")
            return
        dialog = EntradaAduboDialog(self, registro)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.atualizar(registro_id, dados)
            self._carregar_dados()
        self._timer.start(2000)

    def _excluir(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione uma entrada para excluir.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        adubo = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir a entrada de '{adubo}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(registro_id)
            self._carregar_dados()
