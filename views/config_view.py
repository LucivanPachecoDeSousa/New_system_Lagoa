from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QFrame, QDialog,
    QAbstractItemView, QGraphicsDropShadowEffect, QFileDialog,
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor
from controllers.usuario_controller import UsuarioController
from controllers.backup_controller import BackupController
from utils.widgets import msg_box
from controllers.migracao_controller import MigracaoController
from utils.widgets import UpperCaseLineEdit


class UsuarioDialog(QDialog):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setWindowTitle("Editar Usuário" if usuario else "Novo Usuário")
        self.setMinimumWidth(600)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self._setup_ui()
        self.showMaximized()
        if usuario:
            self._preencher(usuario)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setMinimumSize(560, 450)
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
        card_layout.setSpacing(10)

        title = QLabel("Editar Usuário" if self.usuario else "Novo Usuário")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4E342E; font-size: 20px; font-weight: 700; letter-spacing: 2px;")
        card_layout.addWidget(title)

        lbl_user = QLabel("USUÁRIO")
        lbl_user.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_user)

        self.txt_username = UpperCaseLineEdit()
        self.txt_username.setPlaceholderText("Nome de usuário")
        self.txt_username.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_username)

        lbl_nome = QLabel("NOME COMPLETO")
        lbl_nome.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_nome)

        self.txt_nome = UpperCaseLineEdit()
        self.txt_nome.setPlaceholderText("Nome completo")
        self.txt_nome.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_nome)

        lbl_pass = QLabel("SENHA" + (" (deixe em branco para manter)" if self.usuario else ""))
        lbl_pass.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_pass)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Senha")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet(self._input_style())
        card_layout.addWidget(self.txt_password)

        lbl_tipo = QLabel("TIPO")
        lbl_tipo.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_tipo)

        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItem("Administrador", "admin")
        self.cmb_tipo.addItem("Operador", "operador")
        self.cmb_tipo.setStyleSheet(self._input_style())
        card_layout.addWidget(self.cmb_tipo)

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

    def _preencher(self, u):
        self.txt_username.setText(u["username"])
        self.txt_nome.setText(u["nome_completo"])
        idx = self.cmb_tipo.findData(u["tipo"])
        if idx >= 0:
            self.cmb_tipo.setCurrentIndex(idx)

    def _validar_salvar(self):
        if not self.txt_username.text().strip():
            self._msg_box(QMessageBox.Warning, "Validação", "Nome de usuário é obrigatório.")
            return
        if not self.txt_nome.text().strip():
            self._msg_box(QMessageBox.Warning, "Validação", "Nome completo é obrigatório.")
            return
        if not self.usuario and not self.txt_password.text():
            self._msg_box(QMessageBox.Warning, "Validação", "Senha é obrigatória para novos usuários.")
            return
        self.accept()

    def obter_dados(self):
        return {
            "username": self.txt_username.text().strip(),
            "nome_completo": self.txt_nome.text().strip(),
            "password": self.txt_password.text(),
            "tipo": self.cmb_tipo.currentData(),
        }

    def _input_style(self):
        return """
            QLineEdit, QComboBox {
                padding: 12px 14px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 13px;
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

    def _btn_style(self):
        return """
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
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3E2723, stop:1 #5D4037);
            }
        """

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)


class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.usuario_controller = UsuarioController()
        self.backup_controller = BackupController()
        self.migracao_controller = MigracaoController()
        self._setup_ui()
        self._carregar_dados()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_dados)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        header = QLabel("Configuração")
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

        self.btn_novo = QPushButton("+ Novo Usuário")
        self.btn_novo.setCursor(Qt.PointingHandCursor)
        self.btn_novo.setFixedHeight(40)
        self.btn_novo.setStyleSheet(self._btn_primary())
        self.btn_novo.clicked.connect(self._novo)
        toolbar.addWidget(self.btn_novo)

        toolbar.addStretch()

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setCursor(Qt.PointingHandCursor)
        self.btn_editar.setFixedHeight(40)
        self.btn_editar.setStyleSheet(self._btn_warning())
        self.btn_editar.clicked.connect(self._editar)
        toolbar.addWidget(self.btn_editar)

        self.btn_desativar = QPushButton("Desativar")
        self.btn_desativar.setCursor(Qt.PointingHandCursor)
        self.btn_desativar.setFixedHeight(40)
        self.btn_desativar.setStyleSheet(self._btn_danger())
        self.btn_desativar.clicked.connect(self._desativar)
        toolbar.addWidget(self.btn_desativar)

        card_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Usuário", "Nome Completo", "Tipo", "Criado em"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.doubleClicked.connect(self._editar)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)

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

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #eee;")
        card_layout.addWidget(sep)

        backup_header = QLabel("BACKUP / RESTAURAR")
        backup_header.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-top: 5px;")
        card_layout.addWidget(backup_header)

        backup_buttons = QHBoxLayout()
        backup_buttons.setSpacing(8)

        btn_backup = QPushButton("Fazer Backup")
        btn_backup.setCursor(Qt.PointingHandCursor)
        btn_backup.setFixedHeight(40)
        btn_backup.setStyleSheet(self._btn_primary())
        btn_backup.clicked.connect(self._fazer_backup)
        backup_buttons.addWidget(btn_backup)

        btn_restaurar = QPushButton("Restaurar Backup")
        btn_restaurar.setCursor(Qt.PointingHandCursor)
        btn_restaurar.setFixedHeight(40)
        btn_restaurar.setStyleSheet(self._btn_warning())
        btn_restaurar.clicked.connect(self._restaurar_backup)
        backup_buttons.addWidget(btn_restaurar)

        backup_buttons.addStretch()
        card_layout.addLayout(backup_buttons)

        import_header = QLabel("IMPORTAR DADOS DE BACKUP ANTIGO")
        import_header.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-top: 5px;")
        card_layout.addWidget(import_header)

        import_buttons = QHBoxLayout()
        import_buttons.setSpacing(8)

        btn_importar = QPushButton("Importar Backup Antigo")
        btn_importar.setCursor(Qt.PointingHandCursor)
        btn_importar.setFixedHeight(40)
        btn_importar.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #a569bd);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a569bd, stop:1 #bb8fce);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6c3483, stop:1 #8e44ad);
            }
        """)
        btn_importar.clicked.connect(self._importar_backup_antigo)
        import_buttons.addWidget(btn_importar)

        import_buttons.addStretch()
        card_layout.addLayout(import_buttons)

        layout.addWidget(card)

    def _msg_box(self, icone, titulo, texto, botoes=None):
        return msg_box(self, icone, titulo, texto, botoes)

    def _fazer_backup(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecione onde salvar o backup")
        if not pasta:
            return
        ok, resultado = self.backup_controller.fazer_backup(pasta)
        if ok:
            self._msg_box(QMessageBox.Information, "Backup", f"Backup salvo em:\n{resultado}")
        else:
            self._msg_box(QMessageBox.Critical, "Erro", f"Falha ao fazer backup:\n{resultado}")

    def _restaurar_backup(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo de backup", "",
            "Arquivos de banco (*.db *.sqlite);;Todos (*.*)"
        )
        if not arquivo:
            return
        confirm = self._msg_box(
            QMessageBox.Question, "Restaurar Backup",
            "Isso substituirá todos os dados atuais pelo backup.\nTem certeza?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, resultado = self.backup_controller.restaurar_backup(arquivo)
        if ok:
            self._msg_box(QMessageBox.Information, "Restaurado", resultado)
            self._carregar_dados()
        else:
            self._msg_box(QMessageBox.Critical, "Erro", f"Falha ao restaurar:\n{resultado}")

    def _importar_backup_antigo(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo de backup antigo", "",
            "Arquivos de banco (*.db *.sqlite);;Todos (*.*)"
        )
        if not arquivo:
            return
        confirm = self._msg_box(
            QMessageBox.Question, "Importar Dados",
            "Isso adicionará os dados do backup antigo ao sistema atual.\n"
            "Dados existentes não serão alterados.\n\n"
            "Tem certeza que deseja continuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        self._timer.stop()
        resultado = self.migracao_controller.importar_backup(arquivo)
        if resultado["sucesso"]:
            self._msg_box(QMessageBox.Information, "Importação Concluída", resultado["mensagem"])
        else:
            self._msg_box(QMessageBox.Critical, "Erro na Importação", resultado["mensagem"])
        self._carregar_dados()
        self._timer.start(2000)

    def _btn_primary(self):
        return """
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
        """

    def _btn_warning(self):
        return """
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
        """

    def _btn_danger(self):
        return """
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
        """

    def _carregar_dados(self):
        usuarios = self.usuario_controller.listar()

        self.table.setRowCount(len(usuarios))
        for i, u in enumerate(usuarios):
            self.table.setItem(i, 0, QTableWidgetItem(str(u["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(u["username"]))
            self.table.setItem(i, 2, QTableWidgetItem(u["nome_completo"]))
            tipo_label = "Administrador" if u["tipo"] == "admin" else "Operador"
            self.table.setItem(i, 3, QTableWidgetItem(tipo_label))
            dt = u.get("created_at", "")
            if dt:
                qd = QDate.fromString(dt[:10], "yyyy-MM-dd")
                dt = qd.toString("dd/MM/yyyy") if qd.isValid() else dt
            self.table.setItem(i, 4, QTableWidgetItem(dt))

    def _novo(self):
        dialog = UsuarioDialog(self)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            ok, result = self.usuario_controller.criar(dados)
            if ok:
                self._carregar_dados()
            else:
                self._msg_box(QMessageBox.Warning, "Erro", result)
        self._timer.start(2000)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um usuário para editar.")
            return
        usuario_id = int(self.table.item(row, 0).text())
        usuario = self.usuario_controller.buscar_por_id(usuario_id)
        if not usuario:
            self._msg_box(QMessageBox.Warning, "Erro", "Usuário não encontrado.")
            return
        dialog = UsuarioDialog(self, usuario)
        self._timer.stop()
        if dialog.exec():
            dados = dialog.obter_dados()
            self.usuario_controller.atualizar(usuario_id, dados)
            self._carregar_dados()
        self._timer.start(2000)

    def _desativar(self):
        row = self.table.currentRow()
        if row < 0:
            self._msg_box(QMessageBox.Information, "Selecione", "Selecione um usuário para desativar.")
            return
        usuario_id = int(self.table.item(row, 0).text())
        nome = self.table.item(row, 2).text()
        self._timer.stop()
        confirm = self._msg_box(
            QMessageBox.Question, "Confirmar",
            f"Tem certeza que deseja desativar o usuário '{nome}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        self._timer.start(2000)
        if confirm == QMessageBox.Yes:
            self.usuario_controller.desativar(usuario_id)
            self._carregar_dados()
