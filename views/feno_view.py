from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QDoubleSpinBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from controllers.feno_controller import FenoController
from controllers.lote_controller import LoteController
from utils.widgets import msg_box
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit, estilizar_calendario
from utils.excel_export import exportar_excel


class FenoDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.controller = FenoController()
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
        card.setMinimumSize(680, 520)
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

        title = QLabel("Editar Entrada" if self.registro else "Nova Entrada de Feno / Pré-Secado")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4E342E; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        card_layout.addSpacing(10)

        linha1 = QHBoxLayout()
        linha1.setSpacing(12)
        g1 = self._grupo("DATA", self._criar_data())
        g2 = self._grupo("TIPO", self._criar_tipo())
        linha1.addLayout(g1)
        linha1.addLayout(g2)
        card_layout.addLayout(linha1)

        linha2 = QHBoxLayout()
        linha2.setSpacing(12)
        g3 = self._grupo("PLACA", self._criar_placa())
        linha2.addLayout(g3)
        linha2.addStretch()
        card_layout.addLayout(linha2)

        linha_lote = QHBoxLayout()
        linha_lote.setSpacing(12)
        g_lote = self._grupo("LOTE", self._criar_lote())
        g_talhao = self._grupo("TALHÃO", self._criar_talhao())
        linha_lote.addLayout(g_lote)
        linha_lote.addLayout(g_talhao)
        card_layout.addLayout(linha_lote)

        linha3 = QHBoxLayout()
        linha3.setSpacing(12)
        g4 = self._grupo("PESO BRUTO (KG)", self._criar_peso_bruto())
        g5 = self._grupo("TARA (KG)", self._criar_tara())
        g6 = self._grupo("PESO LÍQUIDO (KG)", self._criar_peso_liquido())
        linha3.addLayout(g4)
        linha3.addLayout(g5)
        linha3.addLayout(g6)
        card_layout.addLayout(linha3)

        linha4 = QHBoxLayout()
        linha4.setSpacing(12)
        g7 = self._grupo("QUANTIDADE (UN)", self._criar_quantidade())
        g8 = self._grupo("MÉDIA (KG/UN)", self._criar_media())
        linha4.addLayout(g7)
        linha4.addLayout(g8)
        card_layout.addLayout(linha4)

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

    def _criar_tipo(self):
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItem("FENO", "FENO")
        self.cmb_tipo.addItem("PRÉ-SECADO", "PRÉ-SECADO")
        self.cmb_tipo.setStyleSheet(self._input_style())
        self.cmb_tipo.setCurrentText("FENO")
        return self.cmb_tipo

    def _criar_placa(self):
        self.txt_placa = UpperCaseLineEdit()
        self.txt_placa.setPlaceholderText("Placa do veículo")
        self.txt_placa.setMaxLength(8)
        self.txt_placa.setStyleSheet(self._input_style())
        return self.txt_placa

    def _criar_peso_bruto(self):
        self.spin_bruto = QDoubleSpinBox()
        self.spin_bruto.setRange(0, 999999)
        self.spin_bruto.setDecimals(2)
        self.spin_bruto.setFixedHeight(44)
        self.spin_bruto.setStyleSheet(self._field_style())
        self.spin_bruto.valueChanged.connect(self._calcular)
        return self.spin_bruto

    def _criar_tara(self):
        self.spin_tara = QDoubleSpinBox()
        self.spin_tara.setRange(0, 999999)
        self.spin_tara.setDecimals(2)
        self.spin_tara.setFixedHeight(44)
        self.spin_tara.setStyleSheet(self._field_style())
        self.spin_tara.valueChanged.connect(self._calcular)
        return self.spin_tara

    def _criar_peso_liquido(self):
        self.spin_liquido = QDoubleSpinBox()
        self.spin_liquido.setRange(0, 999999)
        self.spin_liquido.setDecimals(2)
        self.spin_liquido.setFixedHeight(44)
        self.spin_liquido.setReadOnly(True)
        self.spin_liquido.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #f0f0f0;
                color: #000;
            }
        """)
        return self.spin_liquido

    def _criar_quantidade(self):
        self.spin_qtd = QDoubleSpinBox()
        self.spin_qtd.setRange(0, 999999)
        self.spin_qtd.setDecimals(2)
        self.spin_qtd.setFixedHeight(44)
        self.spin_qtd.setStyleSheet(self._field_style())
        self.spin_qtd.valueChanged.connect(self._calcular)
        return self.spin_qtd

    def _criar_media(self):
        self.spin_media = QDoubleSpinBox()
        self.spin_media.setRange(0, 999999)
        self.spin_media.setDecimals(2)
        self.spin_media.setFixedHeight(44)
        self.spin_media.setReadOnly(True)
        self.spin_media.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #f0f0f0;
                color: #000;
            }
        """)
        return self.spin_media

    def _criar_lote(self):
        self.cmb_lote = QComboBox()
        self.cmb_lote.setStyleSheet(self._input_style())
        self.lote_controller = LoteController()
        self._popular_lotes()
        self.cmb_lote.currentIndexChanged.connect(self._popular_talhoes)
        self.cmb_tipo.currentIndexChanged.connect(self._popular_lotes)
        return self.cmb_lote

    def _popular_lotes(self):
        self.cmb_lote.blockSignals(True)
        self.cmb_lote.clear()
        self.cmb_lote.addItem("Selecione um lote", None)
        tipo_filtro = self.cmb_tipo.currentData().lower()
        if tipo_filtro:
            lotes = self.lote_controller.listar(tipo=tipo_filtro)
            for l in lotes:
                self.cmb_lote.addItem(l["nome_lote"], l["id"])
        self.cmb_lote.blockSignals(False)

    def _criar_talhao(self):
        self.cmb_talhao = QComboBox()
        self.cmb_talhao.setStyleSheet(self._input_style())
        return self.cmb_talhao

    def _popular_talhoes(self):
        self.cmb_talhao.blockSignals(True)
        self.cmb_talhao.clear()
        self.cmb_talhao.addItem("Selecione um talhão", None)
        lote_id = self.cmb_lote.currentData()
        if lote_id:
            talhoes = self.lote_controller.listar_talhoes(lote_id)
            for t in talhoes:
                label = t["nome"]
                if t.get("tamanho"):
                    label += f" ({t['tamanho']} ha)"
                self.cmb_talhao.addItem(label, t["id"])
        self.cmb_talhao.blockSignals(False)

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
                border-color: #795548;
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

    def _calcular(self):
        bruto = self.spin_bruto.value()
        tara = self.spin_tara.value()
        liquido = max(0, bruto - tara)
        self.spin_liquido.setValue(liquido)

        qtd = self.spin_qtd.value()
        if qtd > 0 and liquido > 0:
            media = liquido / qtd
            self.spin_media.setValue(round(media, 2))
        else:
            self.spin_media.setValue(0)

    def _preencher(self, r):
        qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
        if qd.isValid():
            self.date_data.setDate(qd)
        idx = self.cmb_tipo.findData(r["tipo"])
        if idx >= 0:
            self.cmb_tipo.setCurrentIndex(idx)
        self.txt_placa.setText(r.get("placa", ""))
        self.spin_bruto.setValue(r.get("peso_bruto", 0))
        self.spin_tara.setValue(r.get("tara", 0))
        self.spin_liquido.setValue(r.get("peso_liquido", 0))
        self.spin_qtd.setValue(r.get("quantidade", 0))
        self.spin_media.setValue(r.get("media_peso", 0))

        if r.get("lote_id"):
            idx = self.cmb_lote.findData(r["lote_id"])
            if idx >= 0:
                self.cmb_lote.setCurrentIndex(idx)
        if r.get("talhao_id"):
            idx = self.cmb_talhao.findData(r["talhao_id"])
            if idx >= 0:
                self.cmb_talhao.setCurrentIndex(idx)

    def _validar_salvar(self):
        if self.spin_bruto.value() <= 0:
            self._msg_erro("O peso bruto deve ser maior que zero.")
            self.spin_bruto.setFocus()
            return
        if self.spin_qtd.value() <= 0:
            self._msg_erro("A quantidade deve ser maior que zero.")
            self.spin_qtd.setFocus()
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
                padding: 8px 20px; background: #795548; color: white;
                border: none; border-radius: 6px; font-weight: 700; min-width: 80px;
            }
            QPushButton:hover { background: #8D6E63; }
        """)
        msg.exec()

    def obter_dados(self):
        return {
            "data": self.date_data.date().toString("yyyy-MM-dd"),
            "tipo": self.cmb_tipo.currentData(),
            "placa": self.txt_placa.text().strip(),
            "peso_bruto": self.spin_bruto.value(),
            "tara": self.spin_tara.value(),
            "peso_liquido": self.spin_liquido.value(),
            "quantidade": self.spin_qtd.value(),
            "media_peso": self.spin_media.value(),
            "lote_id": self.cmb_lote.currentData(),
            "talhao_id": self.cmb_talhao.currentData(),
        }

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class FenoView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.controller = FenoController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Entradas de Feno / Pré-Secado")
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

        self.cmb_filtro_tipo = QComboBox()
        self.cmb_filtro_tipo.addItem("Todos os tipos", None)
        self.cmb_filtro_tipo.addItem("FENO", "FENO")
        self.cmb_filtro_tipo.addItem("PRÉ-SECADO", "PRÉ-SECADO")
        self.cmb_filtro_tipo.setStyleSheet(self._combo_style())
        self.cmb_filtro_tipo.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_tipo)

        toolbar.addStretch()

        self.btn_novo = QPushButton("+ Nova Entrada")
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
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Data", "Tipo", "Lote", "Talhão", "Placa", "Peso Bruto",
             "Tara", "Peso Líquido", "Quantidade", "Média (Kg/Un)"]
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
        header_view.setSectionResizeMode(7, stretch)
        header_view.setSectionResizeMode(8, stretch)
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
                background: #F5F0EB;
                color: #4E342E;
                padding: 10px 14px;
                border: none;
                border-bottom: 2px solid #795548;
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
        self.lbl_resumo.setStyleSheet("color: #4E342E; font-size: 14px; font-weight: 700; padding: 10px 0 2px 0;")
        self.lbl_resumo.setAlignment(Qt.AlignRight)
        card_layout.addWidget(self.lbl_resumo)

        self.lbl_resumo_detalhe = QLabel()
        self.lbl_resumo_detalhe.setStyleSheet("color: #795548; font-size: 12px; font-weight: 600; padding: 0 0 10px 0;")
        self.lbl_resumo_detalhe.setAlignment(Qt.AlignRight)
        self.lbl_resumo_detalhe.setVisible(False)
        card_layout.addWidget(self.lbl_resumo_detalhe)

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

    def _carregar_dados(self):
        tipo = self.cmb_filtro_tipo.currentData()
        registros = self.controller.listar(tipo=tipo)
        self.table.setRowCount(len(registros))
        total_peso = total_qtd = 0
        for i, r in enumerate(registros):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            self.table.setItem(i, 1, QTableWidgetItem(data_str))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("tipo", "")))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("nome_lote", "")))
            self.table.setItem(i, 4, QTableWidgetItem(r.get("nome_talhao", "")))
            self.table.setItem(i, 5, QTableWidgetItem(r.get("placa", "")))
            self.table.setItem(i, 6, QTableWidgetItem(self._fmt_num(r.get("peso_bruto", 0))))
            self.table.setItem(i, 7, QTableWidgetItem(self._fmt_num(r.get("tara", 0))))
            self.table.setItem(i, 8, QTableWidgetItem(self._fmt_num(r.get("peso_liquido", 0))))
            self.table.setItem(i, 9, QTableWidgetItem(self._fmt_num(r.get("quantidade", 0))))
            self.table.setItem(i, 10, QTableWidgetItem(self._fmt_num(r.get("media_peso", 0))))
            total_peso += r.get("peso_liquido", 0) or 0
            total_qtd += r.get("quantidade", 0) or 0

        nome_filtro = self.cmb_filtro_tipo.currentText()
        self.lbl_resumo.setText(
            f"{nome_filtro}  |  "
            f"Total Peso: {self._fmt_num(total_peso)} kg  |  "
            f"Total Quantidade: {self._fmt_num(total_qtd)} un"
        )

        feno_total = feno_qtd = presecado_total = presecado_qtd = 0
        for r in registros:
            if r.get("tipo") == "FENO":
                feno_total += r.get("peso_liquido", 0) or 0
                feno_qtd += r.get("quantidade", 0) or 0
            else:
                presecado_total += r.get("peso_liquido", 0) or 0
                presecado_qtd += r.get("quantidade", 0) or 0
        detalhes = []
        if feno_qtd > 0:
            detalhes.append(f"Feno: {self._fmt_num(feno_qtd)} un  |  {self._fmt_num(feno_total)} kg")
        if presecado_qtd > 0:
            detalhes.append(f"Pré-Secado: {self._fmt_num(presecado_qtd)} un  |  {self._fmt_num(presecado_total)} kg")
        if detalhes:
            self.lbl_resumo_detalhe.setText("  |  ".join(detalhes))
            self.lbl_resumo_detalhe.setVisible(True)
        else:
            self.lbl_resumo_detalhe.setVisible(False)

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
        dialog = FenoDialog(self)
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
        dialog = FenoDialog(self, registro)
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
        tipo = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir a entrada de '{tipo}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(registro_id)
            self._carregar_dados()

    def _exportar(self):
        try:
            tipo = self.cmb_filtro_tipo.currentData()
            registros = self.controller.listar(tipo=tipo)
            cabecalhos = ["ID", "Data", "Tipo", "Lote", "Talhão", "Placa",
                           "Peso Bruto", "Tara", "Peso Líquido", "Quantidade", "Média (Kg/Un)"]
            dados = []
            for r in registros:
                qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
                data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
                dados.append((
                    r["id"], data_str, r.get("tipo", ""),
                    r.get("nome_lote", ""), r.get("nome_talhao", ""),
                    r.get("placa", ""), r.get("peso_bruto", 0),
                    r.get("tara", 0), r.get("peso_liquido", 0),
                    r.get("quantidade", 0), r.get("media_peso", 0),
                ))
            exportar_excel(self, "relatorio_feno.xlsx", "Feno / Pré-Secado", cabecalhos, dados)
        except Exception as e:
            import traceback
            msg_box(self, QMessageBox.Critical, "Erro",
                    f"Erro ao exportar:\n{e}\n\n{traceback.format_exc()}")
