import shutil
from pathlib import Path
from datetime import datetime
from database.connection import Database


class BackupController:
    def __init__(self):
        self.db = Database()

    def _get_db_path(self):
        return self.db._get_db_path()

    def fazer_backup(self, destino: str) -> tuple:
        try:
            origem = self._get_db_path()
            if not origem.exists():
                return False, "Banco de dados não encontrado."

            destino_path = Path(destino)
            if destino_path.is_dir():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                destino_path = destino_path / f"backup_fazenda_{timestamp}.db"

            shutil.copy2(str(origem), str(destino_path))
            return True, str(destino_path)
        except Exception as e:
            return False, str(e)

    def restaurar_backup(self, origem: str) -> tuple:
        try:
            origem_path = Path(origem)
            if not origem_path.exists():
                return False, "Arquivo de backup não encontrado."

            destino = self._get_db_path()

            self.db.close()

            shutil.copy2(str(origem_path), str(destino))
            return True, "Backup restaurado com sucesso."
        except Exception as e:
            return False, str(e)
