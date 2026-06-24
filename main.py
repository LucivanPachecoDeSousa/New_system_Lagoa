import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont
from database.models import criar_tabelas, seed_admin
from views.login import LoginView
from views.main_window import MainWindow


_STYLESHEET_GLOBAL = """
    QMessageBox { background: white; color: #333; }
    QMessageBox > QWidget { background: white; }
    QMessageBox QLabel { color: #333; font-size: 13px; }
"""

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema Campo Fértil")
    app.setStyle("Fusion")
    app.setStyleSheet(_STYLESHEET_GLOBAL)
    app.setFont(QFont("Segoe UI", 11))
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instalador", "icone.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    criar_tabelas()
    seed_admin()

    login = LoginView()
    if login.exec() == LoginView.Accepted:
        user = login._user_data
        window = MainWindow(user)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
