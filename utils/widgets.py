from PySide6.QtWidgets import QLineEdit


class UpperCaseLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self._force_upper)

    def _force_upper(self):
        self.blockSignals(True)
        pos = self.cursorPosition()
        upper = self.text().upper()
        if upper != self.text():
            self.setText(upper)
            self.setCursorPosition(min(pos, len(upper)))
        self.blockSignals(False)


def estilizar_calendario(date_edit):
    cal = date_edit.calendarWidget()
    cal.setStyleSheet("""
        QCalendarWidget {
            background: white;
            color: #000;
        }
        QCalendarWidget QToolButton {
            color: #000;
            background: #f0f0f0;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-weight: 700;
        }
        QCalendarWidget QToolButton:hover {
            background: #ddd;
        }
        QCalendarWidget QToolButton::menu-indicator {
            image: none;
        }
        QCalendarWidget QAbstractItemView:enabled {
            color: #000;
            background: white;
            selection-background-color: #795548;
            selection-color: white;
        }
        QCalendarWidget QAbstractItemView:disabled {
            color: #aaa;
        }
        QCalendarWidget QWidget#qt_calendar_navigationbar {
            background: #f5f5f5;
        }
    """)
