import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QIcon, QFont, QKeyEvent
from PySide6.QtWidgets import QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit
from database.models import criar_tabelas, seed_admin
from views.login import LoginView
from views.main_window import MainWindow


class EnterToTabFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            widget = QApplication.focusWidget()
            if isinstance(widget, (QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit)):
                tab = QKeyEvent(QEvent.KeyPress, Qt.Key_Tab, Qt.NoModifier)
                QApplication.sendEvent(widget, tab)
                return True
        return super().eventFilter(obj, event)


_STYLESHEET_GLOBAL = """
    QMessageBox { background: white; color: #333; }
    QMessageBox QWidget { background: white; }
    QMessageBox QFrame { background: white; }
    QMessageBox QLabel { color: #333; font-size: 13px; background: transparent; }

    QInputDialog { background: white; color: #333; }
    QInputDialog QWidget { background: white; }
    QInputDialog QLabel { color: #333; background: transparent; }
    QInputDialog QLineEdit { background: white; color: #000; border: 1px solid #ccc; padding: 6px; }
    QInputDialog QPushButton { padding: 6px 16px; background: #795548; color: white; border: none; border-radius: 4px; font-weight: 700; }
    QInputDialog QPushButton:hover { background: #8D6E63; }
"""

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema Campo Fértil")
    app.setStyle("Fusion")
    app.setStyleSheet(_STYLESHEET_GLOBAL)
    app.setFont(QFont("Segoe UI", 11))

    filter = EnterToTabFilter()
    app.installEventFilter(filter)
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
