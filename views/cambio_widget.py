from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class CambioWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)
        self.setStyleSheet("""
            QFrame {
                background: rgba(15, 30, 15, 180);
                border-radius: 16px;
            }
        """)
        self.setMinimumWidth(200)
        self.setMaximumWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(4)

        header = QLabel("Câmbio")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 10px; font-weight: 700; letter-spacing: 2px; background: none; border: none;")
        layout.addWidget(header)

        self._dolar_label = QLabel("Dólar: --")
        self._dolar_label.setAlignment(Qt.AlignCenter)
        self._dolar_label.setStyleSheet("color: white; font-size: 14px; font-weight: 700; background: none; border: none;")
        layout.addWidget(self._dolar_label)

        self._euro_label = QLabel("Euro: --")
        self._euro_label.setAlignment(Qt.AlignCenter)
        self._euro_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px; font-weight: 700; background: none; border: none;")
        layout.addWidget(self._euro_label)

    def definir_cambio(self, dados):
        def fmt(valor, variacao):
            seta = "▲" if variacao >= 0 else "▼"
            cor = "#8D6E63" if variacao >= 0 else "#e74c3c"
            return f'R$ {valor:.2f} <span style="color:{cor}; font-size:11px;">{seta} {abs(variacao):.2f}%</span>'

        if "USD" in dados:
            d = dados["USD"]
            self._dolar_label.setText(f'Dólar: {fmt(d["bid"], d["pctChange"])}')
        if "EUR" in dados:
            e = dados["EUR"]
            self._euro_label.setText(f'Euro: {fmt(e["bid"], e["pctChange"])}')
