import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont
from database.models import criar_tabelas, seed_admin
from views.login import LoginView
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema Fazenda")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 11))

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
