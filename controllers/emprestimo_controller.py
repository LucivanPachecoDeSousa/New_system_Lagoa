from database.connection import Database


class EmprestimoController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT * FROM emprestimos
        """
        conds = []
        if apenas_ativos:
            conds.append("ativo = 1")
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY data DESC, created_at DESC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM emprestimos WHERE id = ?
        """, (registro_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO emprestimos
               (data, tipo, entidade, produto_descricao, quantidade, unidade, devolvido, observacao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados["tipo"],
                dados.get("entidade", ""),
                dados.get("produto_descricao", ""),
                int(dados.get("quantidade", 0)),
                dados.get("unidade", "un"),
                1 if dados.get("devolvido") else 0,
                dados.get("observacao", ""),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(self, registro_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE emprestimos
               SET data = ?, tipo = ?, entidade = ?, produto_descricao = ?,
                   quantidade = ?, unidade = ?, devolvido = ?,
                   observacao = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                dados["tipo"],
                dados.get("entidade", ""),
                dados.get("produto_descricao", ""),
                int(dados.get("quantidade", 0)),
                dados.get("unidade", "un"),
                1 if dados.get("devolvido") else 0,
                dados.get("observacao", ""),
                registro_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def remover(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE emprestimos SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
        return cursor.rowcount > 0
