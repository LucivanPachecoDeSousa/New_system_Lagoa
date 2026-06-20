import hashlib
from database.connection import Database

class AuthController:
    def __init__(self):
        self.db = Database()

    def login(self, username: str, password: str) -> tuple:
        if not username or not password:
            return False, "Usuário e senha obrigatórios."

        conn = self.db.connect()
        cursor = conn.cursor()

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "SELECT * FROM usuarios WHERE LOWER(username) = LOWER(?) AND ativo = 1",
            (username,),
        )
        user = cursor.fetchone()

        if user is None:
            return False, "Usuário não encontrado."

        if user["password_hash"] != password_hash:
            return False, "Senha incorreta."

        return True, dict(user)

    def verificar_senha(self, password: str) -> bool:
        if not password:
            return False
        conn = self.db.connect()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "SELECT id FROM usuarios WHERE password_hash = ? AND ativo = 1",
            (password_hash,),
        )
        return cursor.fetchone() is not None
