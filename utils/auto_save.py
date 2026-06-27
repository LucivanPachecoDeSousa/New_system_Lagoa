from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox


class AutoSaveMixin:
    def _iniciar_auto_save(self, controller, registro=None):
        if not hasattr(self, "_auto_save_timer"):
            self._auto_save_id = None
            self._auto_save_timer = QTimer(self)
            self._auto_save_timer.setSingleShot(True)
            self._auto_save_timer.timeout.connect(self._executar_auto_save)
            self._auto_save_pendente = False
            self._auto_save_bloqueado = False
        self._auto_save_controller = controller
        if registro and registro.get("id"):
            self._auto_save_id = registro["id"]

    def _conectar_auto_save(self):
        tipos = [QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox]
        for tipo in tipos:
            for widget in self.findChildren(tipo):
                try:
                    if isinstance(widget, QLineEdit):
                        widget.textChanged.connect(self._marcar_alterado)
                    elif isinstance(widget, QComboBox):
                        widget.currentIndexChanged.connect(self._marcar_alterado)
                    elif isinstance(widget, (QDateEdit, QSpinBox, QDoubleSpinBox)):
                        widget.valueChanged.connect(self._marcar_alterado)
                except RuntimeError:
                    pass

    def _marcar_alterado(self):
        if self._auto_save_bloqueado:
            return
        self._auto_save_pendente = True
        self._auto_save_timer.start(500)

    def _executar_auto_save(self):
        if not self._auto_save_pendente:
            return
        self._auto_save_pendente = False
        try:
            dados = self.obter_dados()
            if self._auto_save_id is None:
                self._auto_save_id = self._auto_save_controller.salvar(dados)
            else:
                self._auto_save_controller.atualizar(self._auto_save_id, dados)
        except (ValueError, Exception):
            pass

    def _salvar_antes_fechar(self):
        if hasattr(self, "_auto_save_timer") and self._auto_save_timer.isActive():
            self._auto_save_timer.stop()
            if self._auto_save_pendente:
                self._executar_auto_save()
