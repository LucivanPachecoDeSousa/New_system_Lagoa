from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame,
    QGraphicsDropShadowEffect, QWidget, QApplication,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QPen, QFontDatabase
from controllers.auth_controller import AuthController
from utils.widgets import UpperCaseLineEdit


class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor("#3E2723"))
        gradient.setColorAt(0.4, QColor("#4E342E"))
        gradient.setColorAt(0.6, QColor("#f0f4f0"))
        gradient.setColorAt(1.0, QColor("#f8faf8"))
        painter.fillRect(self.rect(), QBrush(gradient))


class LoginView(QDialog):
    login_successful = Signal(dict)

    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self._user_data = None
        self._error_label = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Sistema Campo Fértil - Login")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen.width(), screen.height())
        self.showFullScreen()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        bg = BackgroundWidget()
        bg_layout = QHBoxLayout(bg)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)

        self._create_left_panel(bg_layout)
        self._create_right_panel(bg_layout)

        layout.addWidget(bg)

        QTimer.singleShot(50, self._animate_in)

    def _animate_in(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def _create_left_panel(self, parent_layout):
        left = QWidget()
        left.setFixedWidth(600)
        left_layout = QVBoxLayout(left)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setContentsMargins(60, 40, 60, 40)

        icon = QLabel("🌾")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 100px;")
        left_layout.addWidget(icon)

        left_layout.addSpacing(15)

        brand = QLabel("CAMPO FÉRTIL")
        brand.setAlignment(Qt.AlignCenter)
        brand.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: 900;
            letter-spacing: 8px;
        """)
        left_layout.addWidget(brand)

        left_layout.addSpacing(5)

        sub = QLabel("Sistema de Controle Agropecuário")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 15px; letter-spacing: 2px;")
        left_layout.addWidget(sub)

        left_layout.addSpacing(20)

        separator = QFrame()
        separator.setFixedSize(60, 3)
        separator.setStyleSheet("background: rgba(255,255,255,0.3); border-radius: 2px;")
        separator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sep_layout = QHBoxLayout()
        sep_layout.addStretch()
        sep_layout.addWidget(separator)
        sep_layout.addStretch()
        left_layout.addLayout(sep_layout)

        left_layout.addSpacing(20)

        features = QLabel("Carregamento · Recebimento · Estoque · Relatórios")
        features.setAlignment(Qt.AlignCenter)
        features.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px; letter-spacing: 1px;")
        left_layout.addWidget(features)

        left_layout.addStretch()

        footer = QLabel("v1.0.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: rgba(255,255,255,0.2); font-size: 11px;")
        left_layout.addWidget(footer)

        parent_layout.addWidget(left)

    def _create_right_panel(self, parent_layout):
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedSize(420, 510)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(80)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 15)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(45, 40, 45, 40)
        card_layout.setSpacing(10)

        card_layout.addStretch(1)

        avatar = QLabel("🔐")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 50px;")
        card_layout.addWidget(avatar)

        card_layout.addSpacing(5)

        welcome = QLabel("Bem-vindo")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: #1a1a2e; font-size: 26px; font-weight: 700;")
        card_layout.addWidget(welcome)

        welcome_sub = QLabel("Acesse sua conta para continuar")
        welcome_sub.setAlignment(Qt.AlignCenter)
        welcome_sub.setStyleSheet("color: #999; font-size: 13px; margin-bottom: 10px;")
        card_layout.addWidget(welcome_sub)

        card_layout.addSpacing(5)

        self._error_label = QLabel("")
        self._error_label.setAlignment(Qt.AlignCenter)
        self._error_label.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: 600;")
        self._error_label.setFixedHeight(20)
        self._error_label.hide()
        card_layout.addWidget(self._error_label)

        lbl_user = QLabel("USUÁRIO")
        lbl_user.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_user)

        self.txt_username = UpperCaseLineEdit()
        self.txt_username.setPlaceholderText("Digite seu usuário")
        self.txt_username.setStyleSheet(self._input_style(False))
        self.txt_username.textChanged.connect(self._clear_error)
        card_layout.addWidget(self.txt_username)

        card_layout.addSpacing(5)

        lbl_pass = QLabel("SENHA")
        lbl_pass.setStyleSheet("color: #555; font-size: 11px; font-weight: 700; letter-spacing: 1.5px;")
        card_layout.addWidget(lbl_pass)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Digite sua senha")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet(self._input_style(False))
        self.txt_password.textChanged.connect(self._clear_error)
        card_layout.addWidget(self.txt_password)

        card_layout.addSpacing(5)

        self.btn_login = QPushButton("ENTRAR")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setFixedHeight(48)
        self.btn_login.setStyleSheet(self._btn_style())
        self.btn_login.clicked.connect(self.handle_login)
        card_layout.addWidget(self.btn_login)

        card_layout.addSpacing(5)

        forgot = QLabel("Esqueceu sua senha? Fale com o administrador")
        forgot.setAlignment(Qt.AlignCenter)
        forgot.setStyleSheet("color: #bbb; font-size: 11px;")
        card_layout.addWidget(forgot)

        card_layout.addStretch(2)

        self.txt_password.returnPressed.connect(self.handle_login)
        self.btn_login.setDefault(True)

        right_layout.addWidget(card)
        parent_layout.addWidget(right)

    def _clear_error(self):
        if self._error_label and self._error_label.isVisible():
            self._error_label.hide()
            self.txt_username.setStyleSheet(self._input_style(False))
            self.txt_password.setStyleSheet(self._input_style(False))

    def _show_error(self, message):
        if self._error_label:
            self._error_label.setText(message)
            self._error_label.show()
            self.txt_username.setStyleSheet(self._input_style(True))
            self.txt_password.setStyleSheet(self._input_style(True))

    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        success, result = self.auth_controller.login(username, password)

        if success:
            self._user_data = result
            self.login_successful.emit(result)
            self.accept()
        else:
            self._show_error(result)
            self.txt_password.clear()
            self.txt_username.setFocus()

    def _input_style(self, error):
        border = "#e74c3c" if error else "#ddd"
        return f"""
            QLineEdit {{
                padding: 12px 15px;
                border: 2px solid {border};
                border-radius: 10px;
                font-size: 14px;
                background: #fafafa;
                color: #333;
            }}
            QLineEdit:focus {{
                border-color: {"#e74c3c" if error else "#795548"};
                background: white;
            }}
            QLineEdit:hover {{
                border-color: {"#e74c3c" if error else "#bbb"};
            }}
        """

    def _btn_style(self):
        return """
            QPushButton {
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5D4037, stop:1 #795548);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
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
            pass
        super().keyPressEvent(event)
