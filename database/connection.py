import sqlite3
import os
from pathlib import Path

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def connect(self):
        if self._connection is None:
            db_path = Path(__file__).parent.parent / "data" / "fazenda.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(db_path))
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    @property
    def connection(self):
        return self.connect()
