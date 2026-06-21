from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog, QInputDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QFormLayout,
    QGroupBox,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QColor
from controllers.entidade_controller import EntidadeController
from controllers.auth_controller import AuthController
from services.cnpj_service import consultar_cnpj
from utils.widgets import UpperCaseLineEdit


class ConsultaCNPJThread(QThread):
    resultado = Signal(bool, object)

    def __init__(self, cnpj):
        super().__init__()
        self.cnpj = cnpj

    def run(self):
        ok, data = consultar_cnpj(self.cnpj)
        self.resultado.emit(ok, data)


class EntidadeDialog(QDialog):
    def __init__(self, parent=None, entidade=None):
        super().__init__(parent)
        self.entidade = entidade
        self.setWindowTitle("Editar Entidade" if entidade else "Nova Entidade")
        self.setMinimumWidth(720)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self._setup_ui()
        self.showMaximized()
        if entidade:
            self._preencher(entidade)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setMinimumSize(680, 560)
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
        card_layout.setContentsMargins(30, 20, 30, 20)
        card_layout.setSpacing(8)

        title = QLabel("Editar Entidade" if self.entidade else "Nova Entidade")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a3a1a; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        doc_layout = QHBoxLayout()
        doc_layout.setSpacing(8)

        self.cmb_tipo_doc = QComboBox()
        self.cmb_tipo_doc.addItem("CNPJ (automático)", "cnpj")
        self.cmb_tipo_doc.addItem("CPF (manual)", "cpf")
        self.cmb_tipo_doc.setStyleSheet(self._input_style())
        self.cmb_tipo_doc.currentIndexChanged.connect(self._toggle_doc_mode)
        doc_layout.addWidget(self.cmb_tipo_doc)

        self.txt_doc = UpperCaseLineEdit()
        self.txt_doc.setPlaceholderText("Digite o CNPJ ou CPF")
        self.txt_doc.setStyleSheet(self._input_style())
        doc_layout.addWidget(self.txt_doc)

        self.btn_consultar = QPushButton("Consultar")
        self.btn_consultar.setCursor(Qt.PointingHandCursor)
        self.btn_consultar.setFixedHeight(40)
        self.btn_consultar.setStyleSheet("""
            QPushButton {
                padding: 8px 18px;
                background: #2d6a2d;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover { background: #3e8a3e; }
            QPushButton:pressed { background: #1a4a1a; }
        """)
        self.btn_consultar.clicked.connect(self._consultar_cnpj)
        doc_layout.addWidget(self.btn_consultar)

        card_layout.addLayout(doc_layout)

        form = QFormLayout()
        form.setSpacing(6)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.txt_razao = UpperCaseLineEdit()
        self.txt_razao.setPlaceholderText("Razão social / Nome completo")
        self.txt_razao.setStyleSheet(self._input_style())
        form.addRow("Razão Social *:", self.txt_razao)

        self.txt_fantasia = UpperCaseLineEdit()
        self.txt_fantasia.setPlaceholderText("Nome fantasia")
        self.txt_fantasia.setStyleSheet(self._input_style())
        form.addRow("Nome Fantasia:", self.txt_fantasia)

        self.cmb_tipo_pessoa = QComboBox()
        self.cmb_tipo_pessoa.addItem("Jurídica (CNPJ)", "juridica")
        self.cmb_tipo_pessoa.addItem("Física (CPF)", "fisica")
        self.cmb_tipo_pessoa.setStyleSheet(self._input_style())
        form.addRow("Tipo:", self.cmb_tipo_pessoa)

        end_layout = QHBoxLayout()
        self.txt_logradouro = UpperCaseLineEdit()
        self.txt_logradouro.setPlaceholderText("Logradouro")
        self.txt_logradouro.setStyleSheet(self._input_style())
        end_layout.addWidget(self.txt_logradouro)
        self.txt_numero = UpperCaseLineEdit()
        self.txt_numero.setPlaceholderText("Nº")
        self.txt_numero.setFixedWidth(80)
        self.txt_numero.setStyleSheet(self._input_style())
        end_layout.addWidget(self.txt_numero)
        form.addRow("Endereço:", end_layout)

        self.txt_complemento = UpperCaseLineEdit()
        self.txt_complemento.setPlaceholderText("Complemento")
        self.txt_complemento.setStyleSheet(self._input_style())
        form.addRow("Complemento:", self.txt_complemento)

        cidade_layout = QHBoxLayout()
        self.txt_bairro = UpperCaseLineEdit()
        self.txt_bairro.setPlaceholderText("Bairro")
        self.txt_bairro.setStyleSheet(self._input_style())
        cidade_layout.addWidget(self.txt_bairro)
        self.txt_cidade = UpperCaseLineEdit()
        self.txt_cidade.setPlaceholderText("Cidade")
        self.txt_cidade.setStyleSheet(self._input_style())
        cidade_layout.addWidget(self.txt_cidade)
        self.txt_estado = UpperCaseLineEdit()
        self.txt_estado.setPlaceholderText("UF")
        self.txt_estado.setFixedWidth(60)
        self.txt_estado.setStyleSheet(self._input_style())
        cidade_layout.addWidget(self.txt_estado)
        form.addRow("Cidade:", cidade_layout)

        self.txt_cep = UpperCaseLineEdit()
        self.txt_cep.setPlaceholderText("CEP")
        self.txt_cep.setStyleSheet(self._input_style())
        form.addRow("CEP:", self.txt_cep)

        contato_layout = QHBoxLayout()
        self.txt_telefone = UpperCaseLineEdit()
        self.txt_telefone.setPlaceholderText("Telefone")
        self.txt_telefone.setStyleSheet(self._input_style())
        contato_layout.addWidget(self.txt_telefone)
        self.txt_email = UpperCaseLineEdit()
        self.txt_email.setPlaceholderText("E-mail")
        self.txt_email.setStyleSheet(self._input_style())
        contato_layout.addWidget(self.txt_email)
        form.addRow("Contato:", contato_layout)

        self.txt_ie = UpperCaseLineEdit()
        self.txt_ie.setPlaceholderText("Inscrição Estadual")
        self.txt_ie.setStyleSheet(self._input_style())
        form.addRow("Insc. Estadual:", self.txt_ie)

        card_layout.addLayout(form)
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
        btn_salvar.setStyleSheet(self._btn_style())
        btn_salvar.clicked.connect(self._validar_salvar)
        btn_layout.addWidget(btn_salvar)

        card_layout.addLayout(btn_layout)
        layout.addWidget(card)

    def _toggle_doc_mode(self):
        is_cnpj = self.cmb_tipo_doc.currentData() == "cnpj"
        self.btn_consultar.setVisible(is_cnpj)
        self.txt_doc.setPlaceholderText("Digite o CNPJ" if is_cnpj else "Digite o CPF")
        if is_cnpj:
            self.cmb_tipo_pessoa.setCurrentIndex(0)
        else:
            self.cmb_tipo_pessoa.setCurrentIndex(1)

    def _consultar_cnpj(self):
        cnpj = self.txt_doc.text().strip()
        if not cnpj:
            self._msg_box(QMessageBox.Warning, "Aviso", "Digite um CNPJ.")
            return
        self.btn_consultar.setEnabled(False)
        self.btn_consultar.setText("Consultando...")
        self.thread = ConsultaCNPJThread(cnpj)
        self.thread.resultado.connect(self._resultado_consulta)
        self.thread.start()

    def _resultado_consulta(self, ok, data):
        self.btn_consultar.setEnabled(True)
        self.btn_consultar.setText("Consultar")
        if ok:
            self._preencher(data)
        else:
            self._msg_box(QMessageBox.Warning, "Erro", data)

    def _preencher(self, d):
        self.txt_doc.setText(d.get("cnpj_cpf", ""))
        self.txt_razao.setText(d.get("razao_social", ""))
        self.txt_fantasia.setText(d.get("nome_fantasia", ""))
        tipo = d.get("tipo_pessoa", "juridica")
        idx = self.cmb_tipo_pessoa.findData(tipo)
        if idx >= 0:
            self.cmb_tipo_pessoa.setCurrentIndex(idx)
        self.txt_logradouro.setText(d.get("logradouro", ""))
        self.txt_numero.setText(d.get("numero", ""))
        self.txt_complemento.setText(d.get("complemento", ""))
        self.txt_bairro.setText(d.get("bairro", ""))
        self.txt_cidade.setText(d.get("cidade", ""))
        self.txt_estado.setText(d.get("estado", ""))
        self.txt_cep.setText(d.get("cep", ""))
        self.txt_telefone.setText(d.get("telefone", ""))
        self.txt_email.setText(d.get("email", ""))
        ie_principal = d.get("inscricao_estadual", "")
        ies_extra = d.get("inscricoes_estaduais", [])
        if ies_extra:
            todas = [ie_principal] if ie_principal else []
            for ie in ies_extra:
                if isinstance(ie, dict) and ie.get("inscricao_estadual"):
                    val = ie["inscricao_estadual"]
                    if val != ie_principal:
                        todas.append(val)
            self.txt_ie.setText(", ".join(todas))
        else:
            self.txt_ie.setText(ie_principal)

    def _validar_salvar(self):
        doc = self.txt_doc.text().strip()
        if not doc:
            self._msg_box(QMessageBox.Warning, "Validação", "CNPJ/CPF é obrigatório.")
            return
        if not self.txt_razao.text().strip():
            self._msg_box(QMessageBox.Warning, "Validação", "Razão social é obrigatória.")
            return
        self.accept()

    def obter_dados(self):
        return {
            "cnpj_cpf": self.txt_doc.text().strip(),
            "tipo_pessoa": self.cmb_tipo_pessoa.currentData(),
            "razao_social": self.txt_razao.text().strip(),
            "nome_fantasia": self.txt_fantasia.text().strip(),
            "logradouro": self.txt_logradouro.text().strip(),
            "numero": self.txt_numero.text().strip(),
            "complemento": self.txt_complemento.text().strip(),
            "bairro": self.txt_bairro.text().strip(),
            "cidade": self.txt_cidade.text().strip(),
            "estado": self.txt_estado.text().strip(),
            "cep": self.txt_cep.text().strip(),
            "telefone": self.txt_telefone.text().strip(),
            "email": self.txt_email.text().strip(),
            "inscricao_estadual": self.txt_ie.text().strip(),
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
            QLineEdit, QComboBox {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
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


class EntidadeView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = EntidadeController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Cadastro de Entidades")
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

        self.txt_busca = UpperCaseLineEdit()
        self.txt_busca.setPlaceholderText("Buscar por nome ou CNPJ/CPF...")
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

        self.btn_novo = QPushButton("+ Nova Entidade")
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

        self.btn_excluir = QPushButton("Excluir")
        self.btn_excluir.setCursor(Qt.PointingHandCursor)
        self.btn_excluir.setFixedHeight(40)
        self.btn_excluir.setStyleSheet(self._btn_danger())
        self.btn_excluir.clicked.connect(self._excluir)
        toolbar.addWidget(self.btn_excluir)

        card_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "CNPJ/CPF", "Razão Social", "Fantasia", "Cidade", "UF", "Telefone", "Tipo"]
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
        entidades = self.controller.listar()
        if busca:
            entidades = [
                e for e in entidades
                if busca in e["razao_social"].lower()
                or busca in e.get("nome_fantasia", "").lower()
                or busca in e.get("cnpj_cpf", "")
            ]

        self.table.setRowCount(len(entidades))
        for i, e in enumerate(entidades):
            self.table.setItem(i, 0, QTableWidgetItem(str(e["id"])))
            doc = e.get("cnpj_cpf", "")
            if not doc.isdigit():
                doc = "---"
            self.table.setItem(i, 1, QTableWidgetItem(doc))
            self.table.setItem(i, 2, QTableWidgetItem(e["razao_social"]))
            self.table.setItem(i, 3, QTableWidgetItem(e.get("nome_fantasia", "")))
            self.table.setItem(i, 4, QTableWidgetItem(e.get("cidade", "")))
            self.table.setItem(i, 5, QTableWidgetItem(e.get("estado", "")))
            self.table.setItem(i, 6, QTableWidgetItem(e.get("telefone", "")))
            tipo = "PJ" if e.get("tipo_pessoa") == "juridica" else "PF"
            self.table.setItem(i, 7, QTableWidgetItem(tipo))

    def _novo(self):
        dialog = EntidadeDialog(self)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            try:
                self.controller.salvar(dados)
                self._carregar_dados()
            except ValueError as e:
                self._msg_box(QMessageBox.Warning, "Erro", str(e))
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione uma entidade para editar.")
            return
        if not self._confirmar_senha():
            return
        entidade_id = int(self.table.item(row, 0).text())
        entidade = self.controller.buscar_por_id(entidade_id)
        if not entidade:
            self._msg_box(QMessageBox.Warning, "Erro", "Entidade não encontrada.")
            return
        dialog = EntidadeDialog(self, entidade)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            try:
                self.controller.atualizar(entidade_id, dados)
                self._carregar_dados()
            except ValueError as e:
                self._msg_box(QMessageBox.Warning, "Erro", str(e))
        self._timer.start(2000)

    def _excluir(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione uma entidade para excluir.")
            return
        if not self._confirmar_senha():
            return
        entidade_id = int(self.table.item(row, 0).text())
        nome = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja excluir '{nome}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.controller.remover(entidade_id)
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
