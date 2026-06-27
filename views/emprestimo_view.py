from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QSpinBox,
    QDateEdit, QCheckBox, QTextEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from controllers.emprestimo_controller import EmprestimoController
from utils.widgets import msg_box
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit, estilizar_calendario
from utils.auto_save import AutoSaveMixin
from utils.excel_export import exportar_excel


class EmprestimoDialog(QDialog, AutoSaveMixin):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.controller = EmprestimoController()
        self.setWindowTitle("Editar Empréstimo" if registro else "Novo Empréstimo")
        self.setMinimumWidth(600)
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
        card.setMinimumSize(560, 540)
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

        title = QLabel("Editar Empréstimo" if self.registro else "Novo Empréstimo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4E342E; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        card_layout.addSpacing(10)

        lbl_tipo = QLabel("TIPO")
        lbl_tipo.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_tipo)

        tipo_row = QHBoxLayout()
        tipo_row.setSpacing(10)
        self.rd_emprestimo = QPushButton("Emprestando")
        self.rd_emprestimo.setCheckable(True)
        self.rd_emprestimo.setChecked(True)
        self.rd_emprestimo.setCursor(Qt.PointingHandCursor)
        self.rd_emprestimo.setFixedHeight(44)
        self.rd_emprestimo.setStyleSheet(self._btn_tipo_style(True))
        self.rd_emprestimo.clicked.connect(lambda: self._toggle_tipo(True))
        tipo_row.addWidget(self.rd_emprestimo)

        self.rd_tomado = QPushButton("Pegando Emprestado")
        self.rd_tomado.setCheckable(True)
        self.rd_tomado.setCursor(Qt.PointingHandCursor)
        self.rd_tomado.setFixedHeight(44)
        self.rd_tomado.setStyleSheet(self._btn_tipo_style(False))
        self.rd_tomado.clicked.connect(lambda: self._toggle_tipo(False))
        tipo_row.addWidget(self.rd_tomado)
        card_layout.addLayout(tipo_row)

        lbl_data = QLabel("DATA")
        lbl_data.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_data)

        self.date_data = QDateEdit()
        self.date_data.setDate(QDate.currentDate())
        self.date_data.setCalendarPopup(True)
        self.date_data.setDisplayFormat("dd/MM/yyyy")
        estilizar_calendario(self.date_data)
        self.date_data.setStyleSheet(self._input_style())
        card_layout.addWidget(self.date_data)

        lbl_entidade = QLabel("PARA QUEM")
        lbl_entidade.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_entidade)

        self.txt_entidade = UpperCaseLineEdit()
        self.txt_entidade.setPlaceholderText("Nome da pessoa / empresa")
        self.txt_entidade.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_entidade)

        lbl_produto = QLabel("PRODUTO / DESCRIÇÃO")
        lbl_produto.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_produto)

        self.txt_produto = UpperCaseLineEdit()
        self.txt_produto.setPlaceholderText("Descrição do produto")
        self.txt_produto.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_produto)

        valores_layout = QHBoxLayout()
        valores_layout.setSpacing(15)

        vl_qtd = QVBoxLayout()
        vl_qtd.setSpacing(4)
        lbl_qtd = QLabel("QUANTIDADE")
        lbl_qtd.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        vl_qtd.addWidget(lbl_qtd)

        self.spin_qtd = QSpinBox()
        self.spin_qtd.setRange(0, 999999)
        self.spin_qtd.setFixedHeight(44)
        self.spin_qtd.setStyleSheet(self._spin_style())
        vl_qtd.addWidget(self.spin_qtd)
        valores_layout.addLayout(vl_qtd)

        vl_un = QVBoxLayout()
        vl_un.setSpacing(4)
        lbl_un = QLabel("UNIDADE")
        lbl_un.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        vl_un.addWidget(lbl_un)

        self.cmb_unidade = QComboBox()
        self.cmb_unidade.addItems(["un", "kg", "m", "m³", "L", "saco", "peça", "caixa", "par", "pacote", "outro"])
        self.cmb_unidade.setEditable(True)
        self.cmb_unidade.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_unidade.setFixedHeight(44)
        self.cmb_unidade.setStyleSheet(self._input_style())
        vl_un.addWidget(self.cmb_unidade)
        valores_layout.addLayout(vl_un)

        card_layout.addLayout(valores_layout)

        self.chk_devolvido = QCheckBox("Devolvido")
        self.chk_devolvido.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
                font-size: 14px;
                font-weight: 700;
                color: #4E342E;
                padding: 8px 0;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid #795548;
                border-radius: 6px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #795548;
                border-color: #795548;
            }
        """)
        card_layout.addWidget(self.chk_devolvido)

        lbl_obs = QLabel("OBSERVAÇÃO")
        lbl_obs.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_obs)

        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Observações (data de devolução, etc)...")
        self.txt_obs.setMaximumHeight(80)
        self.txt_obs.setStyleSheet("""
            QTextEdit {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QTextEdit:focus {
                border-color: #795548;
                background: white;
            }
        """)
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

    def _btn_tipo_style(self, ativo):
        if ativo:
            return """
                QPushButton {
                    padding: 10px;
                    background: #795548;
                    color: white;
                    border: 2px solid #795548;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                }
            """
        return """
            QPushButton {
                padding: 10px;
                background: #f0f0f0;
                color: #555;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover { background: #e0e0e0; }
        """

    def _toggle_tipo(self, is_emprestimo):
        self.rd_emprestimo.setChecked(is_emprestimo)
        self.rd_tomado.setChecked(not is_emprestimo)
        self.rd_emprestimo.setStyleSheet(self._btn_tipo_style(is_emprestimo))
        self.rd_tomado.setStyleSheet(self._btn_tipo_style(not is_emprestimo))

    def _input_style(self):
        return """
            QLineEdit, QComboBox, QDateEdit {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
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

    def _spin_style(self):
        return """
            QSpinBox {
                padding: 10px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #000;
            }
            QSpinBox:focus {
                border-color: #795548;
                background: white;
            }
        """

    def _preencher(self, r):
        is_emprestimo = r["tipo"] == "emprestimo"
        self._toggle_tipo(is_emprestimo)
        qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
        if qd.isValid():
            self.date_data.setDate(qd)
        self.txt_entidade.setText(r.get("entidade", ""))
        self.txt_produto.setText(r.get("produto_descricao", ""))
        self.spin_qtd.setValue(int(r.get("quantidade", 0)))
        unidade = r.get("unidade", "un")
        ui = self.cmb_unidade.findText(unidade)
        if ui >= 0:
            self.cmb_unidade.setCurrentIndex(ui)
        else:
            self.cmb_unidade.setEditText(unidade)
        self.chk_devolvido.setChecked(bool(r.get("devolvido", 0)))
        self.txt_obs.setPlainText(r.get("observacao", ""))

    def _validar_salvar(self):
        self.accept()

    def obter_dados(self):
        return {
            "data": self.date_data.date().toString("yyyy-MM-dd"),
            "tipo": "emprestimo" if self.rd_emprestimo.isChecked() else "tomado",
            "entidade": self.txt_entidade.text().strip().upper(),
            "produto_descricao": self.txt_produto.text().strip().upper(),
            "quantidade": self.spin_qtd.value(),
            "unidade": self.cmb_unidade.currentText().strip(),
            "devolvido": self.chk_devolvido.isChecked(),
            "observacao": self.txt_obs.toPlainText().strip(),
        }

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class EmprestimoView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.controller = EmprestimoController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Empréstimos")
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

        toolbar.addStretch()

        self.btn_novo = QPushButton("+ Novo Empréstimo")
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

        btn_exportar = QPushButton("Exportar")
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
            ["ID", "Data", "Tipo", "Para Quem", "Produto", "Qtd", "Un", "Devolvido"]
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
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
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

    def _carregar_dados(self):
        registros = self.controller.listar()
        self.table.setRowCount(len(registros))
        pendentes = 0
        for i, r in enumerate(registros):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            self.table.setItem(i, 1, QTableWidgetItem(data_str))
            tipo = "Emprestando" if r["tipo"] == "emprestimo" else "Tomado"
            self.table.setItem(i, 2, QTableWidgetItem(tipo))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("entidade", "")))
            self.table.setItem(i, 4, QTableWidgetItem(r.get("produto_descricao", "")))
            self.table.setItem(i, 5, QTableWidgetItem(str(int(r.get("quantidade", 0)))))
            self.table.setItem(i, 6, QTableWidgetItem(r.get("unidade", "un")))
            dev = r.get("devolvido", 0)
            self.table.setItem(i, 7, QTableWidgetItem("Sim" if dev else "Não"))
            if not dev:
                pendentes += 1
        self.lbl_resumo.setText(f"Pendentes de devolução: {pendentes}")

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
        dialog = EmprestimoDialog(self)
        self._timer.stop()
        dialog.exec()
        self._carregar_dados()
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um empréstimo para editar.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        registro = self.controller.buscar_por_id(registro_id)
        if not registro:
            self._msg_box(QMessageBox.Warning, "Erro", "Empréstimo não encontrado.")
            return
        dialog = EmprestimoDialog(self, registro)
        self._timer.stop()
        dialog.exec()
        self._carregar_dados()
        self._timer.start(2000)

    def _excluir(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um empréstimo para excluir.")
            return
        if not self._confirmar_senha():
            return
        registro_id = int(self.table.item(row, 0).text())
        produto = self.table.item(row, 4).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir o empréstimo de '{produto}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(registro_id)
            self._carregar_dados()

    def _exportar(self):
        registros = self.controller.listar()
        cabecalhos = ["ID", "Data", "Tipo", "Para Quem", "Produto", "Quantidade", "Un", "Devolvido"]
        dados = []
        for r in registros:
            qd = QDate.fromString(r["data"][:10], "yyyy-MM-dd")
            data_str = qd.toString("dd/MM/yyyy") if qd.isValid() else r["data"][:10]
            tipo = "Emprestando" if r["tipo"] == "emprestimo" else "Tomado"
            dev = "Sim" if r.get("devolvido") else "Não"
            dados.append((
                r["id"], data_str, tipo, r.get("entidade", ""),
                r.get("produto_descricao", ""), int(r.get("quantidade", 0)),
                r.get("unidade", "un"), dev,
            ))
        exportar_excel(self, "relatorio_emprestimos.xlsx", "Emprestimos", cabecalhos, dados)
