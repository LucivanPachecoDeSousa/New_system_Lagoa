from database.connection import Database


class FenoController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True, tipo=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM entradas_feno"
        conds = []
        params = []
        if apenas_ativos:
            conds.append("ativo = 1")
        if tipo:
            conds.append("tipo = ?")
            params.append(tipo)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY data DESC, created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entradas_feno WHERE id = ?", (registro_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO entradas_feno
               (data, tipo, placa, peso_bruto, tara, peso_liquido, quantidade, media_peso)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados["tipo"],
                dados.get("placa", ""),
                dados.get("peso_bruto", 0),
                dados.get("tara", 0),
                dados.get("peso_liquido", 0),
                dados.get("quantidade", 0),
                dados.get("media_peso", 0),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(self, registro_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE entradas_feno
               SET data = ?, tipo = ?, placa = ?,
                   peso_bruto = ?, tara = ?, peso_liquido = ?,
                   quantidade = ?, media_peso = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                dados["tipo"],
                dados.get("placa", ""),
                dados.get("peso_bruto", 0),
                dados.get("tara", 0),
                dados.get("peso_liquido", 0),
                dados.get("quantidade", 0),
                dados.get("media_peso", 0),
                registro_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def remover(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE entradas_feno SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
        return cursor.rowcount > 0
