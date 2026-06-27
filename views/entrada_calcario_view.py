from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QDoubleSpinBox,
    QSpinBox, QDateEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from controllers.entrada_calcario_controller import EntradaCalcarioController
from utils.widgets import msg_box
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit, estilizar_calendario
from utils.auto_save import AutoSaveMixin
from utils.excel_export import exportar_excel


class EntradaCalcarioDialog(QDialog, AutoSaveMixin):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.controller = EntradaCalcarioController()
        self.setWindowTitle("Editar Entrada" if registro else "Nova Entrada")
        self.setMinimumWidth(720)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self._setup_ui()
        self._iniciar_auto_save(self.controller, registro)
        self.showMaximized()
        if registro:
            self._auto_save_bloqueado = True
            self._preencher(registro)
            self._auto_save_bloqueado = False

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

        title = QLabel("Editar Entrada" if self.registro else "Nova Entrada de Calcário")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4E342E; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        card_layout.addSpacing(10)

        linha1 = QHBoxLayout()
        linha1.setSpacing(12)
        linha1.addLayout(self._grupo("DATA", self._criar_data()))
        linha1.addLayout(self._grupo("PLACA", self._criar_placa()))
        card_layout.addLayout(linha1)

        linha2 = QHBoxLayout()
        linha2.setSpacing(12)
        linha2.addLayout(self._grupo("TIPO DE CALCÁRIO", self._criar_calcario()))
        linha2.addLayout(self._grupo("LOTE", self._criar_lote()))
        card_layout.addLayout(linha2)

        linha3 = QHBoxLayout()
        linha3.setSpacing(12)
        linha3.addLayout(self._grupo("FORNECEDOR", self._criar_entidade()))
        linha3.addLayout(self._grupo("LOCAL DE DESCARGA", self._criar_local_descarga()))
        card_layout.addLayout(linha3)

        linha4 = QHBoxLayout()
        linha4.setSpacing(12)
        linha4.addLayout(self._grupo("PESO TOTAL (KG)", self._criar_peso_total()))
        card_layout.addLayout(linha4)

        linha5 = QHBoxLayout()
        linha5.setSpacing(12)
        linha5.addLayout(self._grupo("MOTORISTA", self._criar_motorista()))
        linha5.addLayout(self._grupo("NÚMERO NF", self._criar_numero_nf()))
        card_layout.addLayout(linha5)

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

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setFixedHeight(44)
        btn_fechar.setStyleSheet("""
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
        btn_fechar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_fechar)

        card_layout.addLayout(btn_layout)

        layout.addWidget(card)
        self._conectar_auto_save()

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

    def _criar_calcario(self):
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.setEditable(True)
        self.cmb_tipo.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_tipo.lineEdit().setPlaceholderText("Digite ou selecione")
        self.cmb_tipo.setStyleSheet(self._input_style())
        tipos = self.controller.listar_tipos_calcario()
        for t in tipos:
            self.cmb_tipo.addItem(t["nome"], t["id"])
        self.cmb_tipo.setCurrentText("")
        return self.cmb_tipo

    def _criar_lote(self):
        self.cmb_lote = QComboBox()
        self.cmb_lote.addItem("Sem lote", None)
        lotes = self.controller.listar_lotes_calcario()
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

    def _criar_local_descarga(self):
        self.txt_local_descarga = UpperCaseLineEdit()
        self.txt_local_descarga.setPlaceholderText("Onde o calcário foi descarregado")
        self.txt_local_descarga.setStyleSheet(self._input_style())
        return self.txt_local_descarga

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

    def _preencher(self, r):
        qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
        if qd.isValid():
            self.date_data.setDate(qd)
        self.txt_placa.setText(r.get("placa", ""))
        idx = self.cmb_tipo.findData(r["calcario_tipo_id"])
        if idx >= 0:
            self.cmb_tipo.setCurrentIndex(idx)
        else:
            self.cmb_tipo.setCurrentText(r.get("calcario_nome", ""))
        idx_lote = self.cmb_lote.findData(r.get("lote_id"))
        if idx_lote >= 0:
            self.cmb_lote.setCurrentIndex(idx_lote)
        idx_ent = self.cmb_entidade.findData(r["entidade_id"])
        if idx_ent >= 0:
            self.cmb_entidade.setCurrentIndex(idx_ent)
        self.txt_local_descarga.setText(r.get("local_descarga", ""))
        self.spin_peso.setValue(r.get("peso_total_kg", 0))
        self.txt_motorista.setText(r.get("motorista", ""))
        self.txt_nf.setText(r.get("numero_nf", ""))
        self.txt_obs.setText(r.get("observacao", ""))

    def _validar_salvar(self):
        tipo = self.cmb_tipo.currentText().strip()
        if not tipo:
            self._msg_erro("O tipo de calcário é obrigatório.")
            self.cmb_tipo.setFocus()
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
                padding: 8px 20px; background: #795548; color: white;
                border: none; border-radius: 6px; font-weight: 700; min-width: 80px;
            }
            QPushButton:hover { background: #8D6E63; }
        """)
        msg.exec()

    def obter_dados(self):
        tipo_nome = self.cmb_tipo.currentText().strip().upper()
        tipo_id = self.cmb_tipo.currentData()
        if tipo_id is None:
            tipo_id = self.controller.adicionar_tipo_calcario(tipo_nome)
        return {
            "data": self.date_data.date().toString("yyyy-MM-dd"),
            "calcario_tipo_id": tipo_id,
            "lote_id": self.cmb_lote.currentData(),
            "entidade_id": self.cmb_entidade.currentData(),
            "peso_total_kg": self.spin_peso.value(),
            "placa": self.txt_placa.text().strip(),
            "motorista": self.txt_motorista.text().strip(),
            "local_descarga": self.txt_local_descarga.text().strip(),
            "numero_nf": self.txt_nf.text().strip(),
            "observacao": self.txt_obs.text().strip(),
        }

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class EntradaCalcarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.controller = EntradaCalcarioController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Entradas de Calcário")
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
        tipos = self.controller.listar_tipos_calcario()
        for t in tipos:
            self.cmb_filtro_tipo.addItem(t["nome"], t["id"])
        self.cmb_filtro_tipo.setStyleSheet(self._combo_style())
        self.cmb_filtro_tipo.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_tipo)

        self.cmb_filtro_local = QComboBox()
        self.cmb_filtro_local.setEditable(True)
        self.cmb_filtro_local.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_filtro_local.lineEdit().setPlaceholderText("Filtrar local...")
        self.cmb_filtro_local.setStyleSheet("""
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
                background: #fafafa;
                min-width: 180px;
                color: #000;
            }
            QComboBox:focus { border-color: #795548; background: white; }
            QComboBox QAbstractItemView {
                color: #000;
                background: white;
                selection-background-color: #e6e6e6;
                selection-color: #000;
            }
        """)
        self.cmb_filtro_local.currentTextChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_local)

        self.date_filtro_inicio = QDateEdit()
        self.date_filtro_inicio.setCalendarPopup(True)
        self.date_filtro_inicio.setDisplayFormat("dd/MM/yyyy")
        self.date_filtro_inicio.setDate(QDate(2025, 1, 1))
        self.date_filtro_inicio.setSpecialValueText("Início")
        self.date_filtro_inicio.setStyleSheet(self._date_filter_style())
        estilizar_calendario(self.date_filtro_inicio)
        self.date_filtro_inicio.dateChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.date_filtro_inicio)

        self.date_filtro_fim = QDateEdit()
        self.date_filtro_fim.setCalendarPopup(True)
        self.date_filtro_fim.setDisplayFormat("dd/MM/yyyy")
        self.date_filtro_fim.setDate(QDate.currentDate())
        self.date_filtro_fim.setSpecialValueText("Fim")
        self.date_filtro_fim.setStyleSheet(self._date_filter_style())
        estilizar_calendario(self.date_filtro_fim)
        self.date_filtro_fim.dateChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.date_filtro_fim)

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
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Data", "Calcário", "Lote", "Fornecedor", "Local",
             "Peso (kg)", "Placa", "Motorista", "NF"]
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
        header_view.setSectionResizeMode(5, resize)
        header_view.setSectionResizeMode(6, resize)
        header_view.setSectionResizeMode(7, resize)
        header_view.setSectionResizeMode(8, stretch)
        header_view.setSectionResizeMode(9, stretch)

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

    def _date_filter_style(self):
        return """
            QDateEdit {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
                background: #fafafa;
                color: #000;
                min-width: 130px;
            }
            QDateEdit:focus {
                border-color: #795548;
                background: white;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
        """

    def _fmt_num(self, val):
        return f"{val:_.0f}".replace("_", ".")

    def _carregar_dados(self):
        registros = self.controller.listar()
        tipo_id = self.cmb_filtro_tipo.currentData()
        if tipo_id:
            registros = [r for r in registros if r["calcario_tipo_id"] == tipo_id]
        filtro_local = self.cmb_filtro_local.currentData()
        if filtro_local:
            registros = [r for r in registros if r.get("local_descarga", "").upper() == filtro_local.upper()]
        data_inicio = self.date_filtro_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.date_filtro_fim.date().toString("yyyy-MM-dd")
        registros = [
            r for r in registros
            if data_inicio <= r["data"][:10] <= data_fim
        ]
        nome_tipo = self.cmb_filtro_tipo.currentText()
        self.table.setRowCount(len(registros))
        total_peso = 0
        for i, r in enumerate(registros):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            self.table.setItem(i, 1, QTableWidgetItem(data_str))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("calcario_nome", "")))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("nome_lote", "")))
            self.table.setItem(i, 4, QTableWidgetItem(r.get("entidade_nome", "")))
            self.table.setItem(i, 5, QTableWidgetItem(r.get("local_descarga", "")))
            self.table.setItem(i, 6, QTableWidgetItem(self._fmt_num(r.get("peso_total_kg", 0))))
            self.table.setItem(i, 7, QTableWidgetItem(r.get("placa", "")))
            self.table.setItem(i, 8, QTableWidgetItem(r.get("motorista", "")))
            self.table.setItem(i, 9, QTableWidgetItem(r.get("numero_nf", "")))
            total_peso += r.get("peso_total_kg", 0) or 0
        total_cargas = len(registros)
        self.lbl_resumo.setText(
            f"{self._fmt_num(total_peso)} kg  |  {total_cargas} carga(s)"
        )
        self._popular_filtro_local()
    def _popular_filtro_local(self):
        texto_atual = self.cmb_filtro_local.currentText()
        self.cmb_filtro_local.blockSignals(True)
        self.cmb_filtro_local.clear()
        self.cmb_filtro_local.addItem("Todos os locais", None)
        locais = self.controller.listar_locais()
        for l in locais:
            self.cmb_filtro_local.addItem(l, l)
        idx = self.cmb_filtro_local.findText(texto_atual)
        if idx >= 0:
            self.cmb_filtro_local.setCurrentIndex(idx)
        elif texto_atual:
            self.cmb_filtro_local.setCurrentText(texto_atual)
        self.cmb_filtro_local.blockSignals(False)

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
        dialog = EntradaCalcarioDialog(self)
        self._timer.stop()
        dialog.exec()
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
        dialog = EntradaCalcarioDialog(self, registro)
        self._timer.stop()
        dialog.exec()
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
        calcario = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir a entrada de '{calcario}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(registro_id)
            self._carregar_dados()

    def _exportar(self):
        registros = self.controller.listar()
        tipo_id = self.cmb_filtro_tipo.currentData()
        if tipo_id:
            registros = [r for r in registros if r["calcario_tipo_id"] == tipo_id]
        filtro_local = self.cmb_filtro_local.currentData()
        if filtro_local:
            registros = [r for r in registros if r.get("local_descarga", "").upper() == filtro_local.upper()]
        data_inicio = self.date_filtro_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.date_filtro_fim.date().toString("yyyy-MM-dd")
        registros = [r for r in registros if data_inicio <= r["data"][:10] <= data_fim]
        cabecalhos = ["ID", "Data", "Calcário", "Lote", "Fornecedor", "Local",
                       "Peso (kg)", "Placa", "Motorista", "NF"]
        dados = []
        for r in registros:
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            dados.append((
                r["id"], data_str, r.get("calcario_nome", ""),
                r.get("nome_lote", ""), r.get("entidade_nome", ""),
                r.get("local_descarga", ""), r.get("peso_total_kg", 0),
                r.get("placa", ""), r.get("motorista", ""),
                r.get("numero_nf", ""),
            ))
        exportar_excel(self, "relatorio_entradas_calcario.xlsx", "Entradas Calcário", cabecalhos, dados)
