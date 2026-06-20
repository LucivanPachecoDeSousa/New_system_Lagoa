from database.connection import Database

class ProdutoController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        if apenas_ativos:
            cursor.execute("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome")
        else:
            cursor.execute("SELECT * FROM produtos ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, produto_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome) VALUES (?)",
            (dados["nome"],),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(self, produto_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (dados["nome"], produto_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def remover(self, produto_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
        conn.commit()
        return cursor.rowcount > 0

    def restaurar(self, produto_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET ativo = 1 WHERE id = ?", (produto_id,))
        conn.commit()
        return cursor.rowcount > 0
