import hashlib
from database.connection import Database

class UsuarioController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        if apenas_ativos:
            cursor.execute("SELECT * FROM usuarios WHERE ativo = 1 ORDER BY nome_completo")
        else:
            cursor.execute("SELECT * FROM usuarios ORDER BY nome_completo")
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, usuario_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def criar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (dados["username"],))
        if cursor.fetchone():
            return False, "Nome de usuário já existe."

        password_hash = hashlib.sha256(dados["password"].encode()).hexdigest()
        cursor.execute(
            """INSERT INTO usuarios (username, password_hash, nome_completo, tipo)
               VALUES (?, ?, ?, ?)""",
            (dados["username"], password_hash, dados["nome_completo"], dados["tipo"]),
        )
        conn.commit()
        return True, cursor.lastrowid

    def atualizar(self, usuario_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()

        if dados.get("password"):
            password_hash = hashlib.sha256(dados["password"].encode()).hexdigest()
            cursor.execute(
                """UPDATE usuarios
                   SET username = ?, password_hash = ?, nome_completo = ?, tipo = ?
                   WHERE id = ?""",
                (dados["username"], password_hash, dados["nome_completo"], dados["tipo"], usuario_id),
            )
        else:
            cursor.execute(
                """UPDATE usuarios
                   SET username = ?, nome_completo = ?, tipo = ?
                   WHERE id = ?""",
                (dados["username"], dados["nome_completo"], dados["tipo"], usuario_id),
            )
        conn.commit()
        return True

    def desativar(self, usuario_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (usuario_id,))
        conn.commit()
        return cursor.rowcount > 0

    def ativar(self, usuario_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET ativo = 1 WHERE id = ?", (usuario_id,))
        conn.commit()
        return cursor.rowcount > 0
