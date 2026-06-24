from database.connection import Database


class FenoController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True, tipo=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """SELECT e.*, l.nome_lote, lt.nome AS nome_talhao
                   FROM entradas_feno e
                   LEFT JOIN lotes l ON e.lote_id = l.id
                   LEFT JOIN lote_talhoes lt ON e.talhao_id = lt.id"""
        conds = []
        params = []
        if apenas_ativos:
            conds.append("e.ativo = 1")
        if tipo:
            conds.append("e.tipo = ?")
            params.append(tipo)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY e.data DESC, e.created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.*, l.nome_lote, lt.nome AS nome_talhao
               FROM entradas_feno e
               LEFT JOIN lotes l ON e.lote_id = l.id
               LEFT JOIN lote_talhoes lt ON e.talhao_id = lt.id
               WHERE e.id = ?""",
            (registro_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO entradas_feno
               (data, tipo, placa, peso_bruto, tara, peso_liquido, quantidade, media_peso, lote_id, talhao_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados["tipo"],
                dados.get("placa", ""),
                dados.get("peso_bruto", 0),
                dados.get("tara", 0),
                dados.get("peso_liquido", 0),
                dados.get("quantidade", 0),
                dados.get("media_peso", 0),
                dados.get("lote_id"),
                dados.get("talhao_id"),
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
                   lote_id = ?, talhao_id = ?,
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
                dados.get("lote_id"),
                dados.get("talhao_id"),
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
