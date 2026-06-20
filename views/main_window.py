from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QStackedWidget, QPushButton, QLabel, QFrame,
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject
from PySide6.QtGui import QPainter, QLinearGradient, QBrush, QColor
from datetime import datetime
from views.produto_view import ProdutoView
from views.config_view import ConfigView
from views.entidade_view import EntidadeView
from views.lote_view import LoteView
from views.carregamento_view import CarregamentoView
from views.material_construcao_view import MaterialConstrucaoView
from views.entrada_adubo_view import EntradaAduboView
from views.entrada_calcario_view import EntradaCalcarioView
from views.previsao_semanal_widget import PrevisaoSemanalWidget
from services.clima_service import obter_localizacao, obter_clima


class ClimaWorker(QObject):
    finished = Signal(dict)

    def run(self):
        lat, lon, cidade, estado = obter_localizacao()
        if lat is None:
            self.finished.emit({"erro": "Localização indisponível"})
            return
        clima = obter_clima(lat, lon)
        local = f"{cidade}, {estado}" if estado else cidade
        if clima:
            self.finished.emit({"local": local, **clima})
        else:
            self.finished.emit({"local": local, "erro": "Clima indisponível"})


class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor("#0f1f0f"))
        gradient.setColorAt(0.4, QColor("#1a3a1a"))
        gradient.setColorAt(0.6, QColor("#8c8c8c"))
        gradient.setColorAt(1.0, QColor("#666666"))
        painter.fillRect(self.rect(), QBrush(gradient))


class MainWindow(QMainWindow):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Sistema Fazenda - {self.user['nome_completo']}")
        self.setMinimumSize(1024, 700)

        self._create_central_widget()
        self._create_status_bar()

        self.showMaximized()

    def navigate_to(self, widget):
        while self.stack.count() > 1:
            w = self.stack.widget(1)
            self.stack.removeWidget(w)
            w.deleteLater()
        if widget is not None:
            self.stack.addWidget(widget)
            self.stack.setCurrentWidget(widget)

    def _go_home(self):
        self.stack.setCurrentWidget(self._home_widget)

    def _create_central_widget(self):
        central = BackgroundWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # top bar
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            QFrame {
                background: rgba(15, 30, 15, 200);
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 5, 20, 5)

        brand = QLabel("🌾  FAZENDA")
        brand.setStyleSheet("color: white; font-size: 16px; font-weight: 900; letter-spacing: 4px;")
        top_layout.addWidget(brand)

        top_layout.addStretch()

        btn_home = QPushButton("Início")
        btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.setStyleSheet(self._nav_btn_style())
        btn_home.clicked.connect(self._go_home)
        top_layout.addWidget(btn_home)

        btn_produtos = QPushButton("Produtos")
        btn_produtos.setCursor(Qt.PointingHandCursor)
        btn_produtos.setStyleSheet(self._nav_btn_style())
        btn_produtos.clicked.connect(lambda: self.navigate_to(ProdutoView()))
        top_layout.addWidget(btn_produtos)

        btn_entidades = QPushButton("Entidades")
        btn_entidades.setCursor(Qt.PointingHandCursor)
        btn_entidades.setStyleSheet(self._nav_btn_style())
        btn_entidades.clicked.connect(lambda: self.navigate_to(EntidadeView()))
        top_layout.addWidget(btn_entidades)

        btn_lotes = QPushButton("Lotes")
        btn_lotes.setCursor(Qt.PointingHandCursor)
        btn_lotes.setStyleSheet(self._nav_btn_style())
        btn_lotes.clicked.connect(lambda: self.navigate_to(LoteView()))
        top_layout.addWidget(btn_lotes)

        btn_carregamentos = QPushButton("Carregamentos")
        btn_carregamentos.setCursor(Qt.PointingHandCursor)
        btn_carregamentos.setStyleSheet(self._nav_btn_style())
        btn_carregamentos.clicked.connect(lambda: self.navigate_to(CarregamentoView()))
        top_layout.addWidget(btn_carregamentos)

        btn_material = QPushButton("Materiais")
        btn_material.setCursor(Qt.PointingHandCursor)
        btn_material.setStyleSheet(self._nav_btn_style())
        btn_material.clicked.connect(lambda: self.navigate_to(MaterialConstrucaoView()))
        top_layout.addWidget(btn_material)

        btn_entrada_adubo = QPushButton("Adubo")
        btn_entrada_adubo.setCursor(Qt.PointingHandCursor)
        btn_entrada_adubo.setStyleSheet(self._nav_btn_style())
        btn_entrada_adubo.clicked.connect(lambda: self.navigate_to(EntradaAduboView()))
        top_layout.addWidget(btn_entrada_adubo)

        btn_entrada_calcario = QPushButton("Calcário")
        btn_entrada_calcario.setCursor(Qt.PointingHandCursor)
        btn_entrada_calcario.setStyleSheet(self._nav_btn_style())
        btn_entrada_calcario.clicked.connect(lambda: self.navigate_to(EntradaCalcarioView()))
        top_layout.addWidget(btn_entrada_calcario)

        btn_config = QPushButton("Configuração")
        btn_config.setCursor(Qt.PointingHandCursor)
        btn_config.setStyleSheet(self._nav_btn_style())
        btn_config.clicked.connect(lambda: self.navigate_to(ConfigView()))
        top_layout.addWidget(btn_config)

        btn_sair = QPushButton("Sair")
        btn_sair.setCursor(Qt.PointingHandCursor)
        btn_sair.setStyleSheet("""
            QPushButton {
                padding: 8px 18px;
                background: rgba(231, 76, 60, 0.8);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover { background: rgba(231, 76, 60, 1); }
        """)
        btn_sair.clicked.connect(self.close)
        top_layout.addWidget(btn_sair)

        layout.addWidget(top_bar)

        # content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        content_layout.addWidget(self.stack, 1)

        # previsao semanal fora do card
        self._previsao_widget = PrevisaoSemanalWidget()
        self._previsao_widget.setVisible(False)
        content_layout.addWidget(self._previsao_widget)

        sair_layout = QHBoxLayout()
        sair_layout.setContentsMargins(10, 2, 10, 2)
        lbl_sair = QLabel('<a href="#" style="color: rgba(255,255,255,0.5); text-decoration: none; font-size: 11px;">Sair do Sistema</a>')
        lbl_sair.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        lbl_sair.linkActivated.connect(self.close)
        sair_layout.addWidget(lbl_sair)
        sair_layout.addStretch()
        content_layout.addLayout(sair_layout)

        # home widget
        self._home_widget = QWidget()
        self._home_widget.setStyleSheet("background: transparent;")
        home_layout = QVBoxLayout(self._home_widget)
        home_layout.setAlignment(Qt.AlignCenter)

        home_card = QFrame()
        home_card.setFixedSize(600, 460)
        home_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
            }
        """)
        card_inner = QVBoxLayout(home_card)
        card_inner.setAlignment(Qt.AlignCenter)
        card_inner.setContentsMargins(50, 40, 50, 40)

        card_inner.addStretch(1)

        icon = QLabel("🌾")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 70px;")
        card_inner.addWidget(icon)

        title = QLabel("Fazenda Lagoa Bonita")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #000; font-size: 26px; font-weight: 900; letter-spacing: 4px;")
        card_inner.addWidget(title)

        self.lbl_relogio = QLabel()
        self.lbl_relogio.setAlignment(Qt.AlignCenter)
        self.lbl_relogio.setStyleSheet("color: #000; font-size: 36px; font-weight: 700; letter-spacing: 3px; margin: 8px 0;")
        card_inner.addWidget(self.lbl_relogio)

        self.lbl_data = QLabel()
        self.lbl_data.setAlignment(Qt.AlignCenter)
        self.lbl_data.setStyleSheet("color: #000; font-size: 15px; margin-bottom: 12px;")
        card_inner.addWidget(self.lbl_data)

        self._atualizar_relogio()
        self._timer_relogio = QTimer(self)
        self._timer_relogio.timeout.connect(self._atualizar_relogio)
        self._timer_relogio.start(1000)

        sub = QLabel(f"Bem-vindo, {self.user['nome_completo']}")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #000; font-size: 16px; margin: 8px 0 15px 0;")
        card_inner.addWidget(sub)

        home_layout.addWidget(home_card)
        self.stack.addWidget(self._home_widget)

        layout.addWidget(self.content_area, 1)

        # clima
        self._atualizar_clima()
        self._timer_clima = QTimer(self)
        self._timer_clima.timeout.connect(self._atualizar_clima)
        self._timer_clima.start(1800000)

    def _create_status_bar(self):
        status = QStatusBar()
        status.setStyleSheet("""
            QStatusBar {
                background: #0f1f0f;
                color: rgba(255,255,255,0.5);
                padding: 4px;
                font-size: 11px;
            }
        """)
        status.showMessage(f"Conectado como: {self.user['username']}  |  Tipo: {self.user['tipo']}")
        self.setStatusBar(status)

    def _atualizar_relogio(self):
        agora = datetime.now()
        self.lbl_relogio.setText(agora.strftime("%H:%M:%S"))
        dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_data.setText(f"{dias_semana[agora.weekday()]}, {agora.day} de {meses[agora.month-1]} de {agora.year}")

    def _atualizar_clima(self):
        self._clima_thread = QThread()
        self._clima_worker = ClimaWorker()
        self._clima_worker.moveToThread(self._clima_thread)
        self._clima_thread.started.connect(self._clima_worker.run)
        self._clima_worker.finished.connect(self._exibir_clima)
        self._clima_worker.finished.connect(self._clima_thread.quit)
        self._clima_worker.finished.connect(self._clima_worker.deleteLater)
        self._clima_thread.finished.connect(self._clima_thread.deleteLater)
        self._clima_thread.start()

    def _exibir_clima(self, dados):
        if "erro" in dados or "previsao_semanal" not in dados:
            self._previsao_widget.setVisible(False)
            return
        previsao = dados.get("previsao_semanal", [])
        if previsao:
            self._previsao_widget.definir_previsao(previsao)
            self._previsao_widget.setVisible(True)

    def _nav_btn_style(self):
        return """
            QPushButton {
                padding: 8px 18px;
                background: rgba(255,255,255,0.1);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.05);
            }
        """
