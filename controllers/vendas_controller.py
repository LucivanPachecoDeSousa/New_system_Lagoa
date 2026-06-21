from database.connection import Database


class VendasController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True, comprador=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM vendas"
        conds = []
        params = []
        if apenas_ativos:
            conds.append("ativo = 1")
        if comprador:
            conds.append("comprador LIKE ?")
            params.append(f"%{comprador}%")
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY data DESC, created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendas WHERE id = ?", (registro_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO vendas
               (data, produto, quantidade_kg, comprador, valor_unitario, valor_total)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados.get("produto", ""),
                dados.get("quantidade_kg", 0),
                dados.get("comprador", ""),
                dados.get("valor_unitario", 0),
                dados.get("valor_total", 0),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(self, registro_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE vendas
               SET data = ?, produto = ?, quantidade_kg = ?,
                   comprador = ?, valor_unitario = ?, valor_total = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                dados.get("produto", ""),
                dados.get("quantidade_kg", 0),
                dados.get("comprador", ""),
                dados.get("valor_unitario", 0),
                dados.get("valor_total", 0),
                registro_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def remover(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE vendas SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
        return cursor.rowcount > 0
