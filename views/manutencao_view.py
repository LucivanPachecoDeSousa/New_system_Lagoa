from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QSpinBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from controllers.manutencao_controller import ManutencaoController
from utils.widgets import msg_box
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit, estilizar_calendario
from utils.excel_export import exportar_excel


class ManutencaoDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.controller = ManutencaoController()
        self.setWindowTitle("Editar Manutenção" if registro else "Nova Manutenção")
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
        card.setMinimumSize(680, 580)
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

        title = QLabel("Editar Manutenção" if self.registro else "Nova Manutenção")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4E342E; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)
        card_layout.addSpacing(10)

        linha1 = QHBoxLayout()
        linha1.setSpacing(12)
        linha1.addLayout(self._grupo("DATA", self._criar_data()))
        linha1.addLayout(self._grupo("VEÍCULO / MÁQUINA", self._criar_veiculo()))
        card_layout.addLayout(linha1)

        linha2 = QHBoxLayout()
        linha2.setSpacing(12)
        linha2.addLayout(self._grupo("SERVIÇO", self._criar_servico()))
        linha2.addLayout(self._grupo("KM / HORÍMETRO", self._criar_km()))
        card_layout.addLayout(linha2)

        lbl_desc = QLabel("DESCRIÇÃO / PEÇAS")
        lbl_desc.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_desc)

        self.txt_descricao = UpperCaseLineEdit()
        self.txt_descricao.setPlaceholderText("Descrição dos serviços e peças utilizadas")
        self.txt_descricao.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_descricao)

        lbl_resp = QLabel("RESPONSÁVEL")
        lbl_resp.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_resp)

        self.txt_responsavel = UpperCaseLineEdit()
        self.txt_responsavel.setPlaceholderText("Quem realizou a troca / manutenção")
        self.txt_responsavel.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_responsavel)

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

    def _criar_veiculo(self):
        self.txt_veiculo = UpperCaseLineEdit()
        self.txt_veiculo.setPlaceholderText("Ex: TRATOR 5065, CAMINHÃO MERCEDES")
        self.txt_veiculo.setStyleSheet(self._input_style())
        return self.txt_veiculo

    def _criar_servico(self):
        self.cmb_servico = QComboBox()
        self.cmb_servico.setEditable(True)
        self.cmb_servico.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_servico.lineEdit().setPlaceholderText("Digite ou selecione")
        self.cmb_servico.setStyleSheet(self._input_style())
        tipos = self.controller.listar_tipos_servico()
        for t in tipos:
            self.cmb_servico.addItem(t["nome"], t["id"])
        self.cmb_servico.setCurrentText("")
        return self.cmb_servico

    def _criar_km(self):
        self.spin_km = QSpinBox()
        self.spin_km.setRange(0, 9999999)
        self.spin_km.setFixedHeight(44)
        self.spin_km.setStyleSheet(self._field_style())
        return self.spin_km

    def _field_style(self):
        return """
            QDateEdit, QSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QDateEdit:focus, QSpinBox:focus {
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
        self.txt_veiculo.setText(r.get("veiculo", ""))
        idx = self.cmb_servico.findData(r.get("servico_tipo_id"))
        if idx >= 0:
            self.cmb_servico.setCurrentIndex(idx)
        else:
            self.cmb_servico.setCurrentText(r.get("servico_nome", ""))
        self.txt_descricao.setText(r.get("descricao_pecas", ""))
        self.txt_responsavel.setText(r.get("responsavel", ""))
        self.spin_km.setValue(r.get("kilometragem_horimetro", 0))

    def _validar_salvar(self):
        if not self.txt_veiculo.text().strip():
            self._msg_erro("Informe o veículo ou máquina.")
            self.txt_veiculo.setFocus()
            return
        if not self.txt_responsavel.text().strip():
            self._msg_erro("Informe o responsável.")
            self.txt_responsavel.setFocus()
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
        servico_nome = self.cmb_servico.currentText().strip().upper()
        servico_id = self.cmb_servico.currentData()
        if servico_id is None and servico_nome:
            servico_id = self.controller.adicionar_tipo_servico(servico_nome)
        return {
            "data": self.date_data.date().toString("yyyy-MM-dd"),
            "veiculo": self.txt_veiculo.text().strip().upper(),
            "servico_tipo_id": servico_id,
            "descricao_pecas": self.txt_descricao.text().strip(),
            "responsavel": self.txt_responsavel.text().strip().upper(),
            "kilometragem_horimetro": self.spin_km.value(),
        }

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class ManutencaoView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.controller = ManutencaoController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Manutenções")
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

        self.cmb_filtro_servico = QComboBox()
        self.cmb_filtro_servico.addItem("Todos os serviços", None)
        tipos = self.controller.listar_tipos_servico()
        for t in tipos:
            self.cmb_filtro_servico.addItem(t["nome"], t["id"])
        self.cmb_filtro_servico.setStyleSheet(self._combo_style())
        self.cmb_filtro_servico.currentIndexChanged.connect(self._carregar_dados)
        toolbar.addWidget(self.cmb_filtro_servico)

        toolbar.addStretch()

        self.btn_novo = QPushButton("+ Nova Manutenção")
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Data", "Veículo", "Serviço", "Descrição", "Responsável", "KM / Horímetro"]
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
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.Stretch)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.ResizeToContents)

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
        layout.addWidget(card)

    def _combo_style(self):
        return """
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
                background: #fafafa;
                min-width: 220px;
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
        registros = self.controller.listar()
        servico_id = self.cmb_filtro_servico.currentData()
        if servico_id:
            registros = [r for r in registros if r["servico_tipo_id"] == servico_id]
        self.table.setRowCount(len(registros))
        for i, r in enumerate(registros):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            self.table.setItem(i, 1, QTableWidgetItem(data_str))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("veiculo", "")))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("servico_nome", "")))
            self.table.setItem(i, 4, QTableWidgetItem(r.get("descricao_pecas", "")))
            self.table.setItem(i, 5, QTableWidgetItem(r.get("responsavel", "")))
            km = r.get("kilometragem_horimetro", 0) or 0
            self.table.setItem(i, 6, QTableWidgetItem(self._fmt_num(km)))

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
        dialog = ManutencaoDialog(self)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.salvar(dados)
            self._carregar_dados()
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um registro para editar.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        registro = self.controller.buscar_por_id(registro_id)
        if not registro:
            self._msg_box(QMessageBox.Warning, "Erro", "Registro não encontrado.")
            return
        dialog = ManutencaoDialog(self, registro)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.controller.atualizar(registro_id, dados)
            self._carregar_dados()
        self._timer.start(2000)

    def _excluir(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um registro para excluir.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        veiculo = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir a manutenção de '{veiculo}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(registro_id)
            self._carregar_dados()

    def _exportar(self):
        registros = self.controller.listar()
        servico_id = self.cmb_filtro_servico.currentData()
        if servico_id:
            registros = [r for r in registros if r["servico_tipo_id"] == servico_id]
        cabecalhos = ["ID", "Data", "Veículo", "Serviço", "Descrição", "Responsável", "KM / Horímetro"]
        dados = []
        for r in registros:
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            dados.append((
                r["id"], data_str, r.get("veiculo", ""),
                r.get("servico_nome", ""), r.get("descricao_pecas", ""),
                r.get("responsavel", ""), r.get("kilometragem_horimetro", 0),
            ))
        exportar_excel(self, "relatorio_manutencoes.xlsx", "Manutenções", cabecalhos, dados)
