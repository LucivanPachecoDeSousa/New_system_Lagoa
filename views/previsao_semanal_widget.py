from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve


class DiaCard(QFrame):
    def __init__(self, dados, destaque=False):
        super().__init__()
        self.setFixedSize(90, 90)
        bg = "rgba(255,255,255,0.15)" if destaque else "rgba(255,255,255,0.08)"
        border = "1px solid rgba(255,255,255,0.2)" if destaque else "1px solid rgba(255,255,255,0.08)"
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: {border};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)

        lbl_dia = QLabel(f"{dados['dia']} {dados['dia_mes']}/{dados['mes']}")
        lbl_dia.setAlignment(Qt.AlignCenter)
        lbl_dia.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 9px; font-weight: 700; background: none; border: none;")
        layout.addWidget(lbl_dia)

        lbl_icone = QLabel(dados["icone"])
        lbl_icone.setAlignment(Qt.AlignCenter)
        lbl_icone.setStyleSheet("font-size: 20px; background: none; border: none;")
        layout.addWidget(lbl_icone)

        temp_layout = QHBoxLayout()
        temp_layout.setAlignment(Qt.AlignCenter)
        temp_layout.setSpacing(4)

        lbl_max = QLabel(f"{dados['temp_max']:.0f}°" if dados["temp_max"] is not None else "--")
        lbl_max.setStyleSheet("color: white; font-size: 11px; font-weight: 700; background: none; border: none;")
        temp_layout.addWidget(lbl_max)

        lbl_min = QLabel(f"{dados['temp_min']:.0f}°" if dados["temp_min"] is not None else "--")
        lbl_min.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 10px; background: none; border: none;")
        temp_layout.addWidget(lbl_min)

        layout.addLayout(temp_layout)


class PrevisaoSemanalWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._offset = 0
        self._max_offset = 0
        self._card_width = 100

        self.setFixedHeight(110)
        self.setStyleSheet("""
            QFrame {
                background: rgba(15, 30, 15, 180);
                border-radius: 16px;
            }
        """)

        self._container = QWidget(self)
        self._container.setStyleSheet("background: transparent;")
        self._container_layout = QHBoxLayout(self._container)
        self._container_layout.setContentsMargins(8, 4, 8, 4)
        self._container_layout.setSpacing(6)
        self._container_layout.setAlignment(Qt.AlignLeft)

        self._anim = QPropertyAnimation(self._container, b"pos")
        self._anim.setDuration(400)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._avancar)
        self._timer.start(5000)

    def definir_previsao(self, dados_semana):
        for child in self._container.findChildren(QFrame):
            child.deleteLater()

        for i, dado in enumerate(dados_semana):
            card = DiaCard(dado, destaque=(i == 0))
            self._container_layout.addWidget(card)

        self._container.adjustSize()
        self._recalcular_max_offset()
        self._offset = 0
        self._container.move(10, 0)

    def _recalcular_max_offset(self):
        container_w = self._container.width()
        self._max_offset = max(0, container_w - self.width() + 20)

    def _avancar(self):
        if self._max_offset <= 0:
            return
        self._offset += self._card_width
        if self._offset > self._max_offset:
            self._offset = 0
        self._anim.setStartValue(self._container.pos())
        self._anim.setEndValue(QPoint(-self._offset + 10, 0))
        self._anim.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._container.setFixedHeight(self.height())
        self._recalcular_max_offset()
