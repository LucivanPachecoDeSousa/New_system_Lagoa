from database.connection import Database


class ManutencaoController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT m.*, s.nome AS servico_nome
            FROM manutencoes m
            LEFT JOIN servico_tipos s ON m.servico_tipo_id = s.id
        """
        conds = []
        if apenas_ativos:
            conds.append("m.ativo = 1")
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY m.data DESC, m.created_at DESC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, s.nome AS servico_nome
            FROM manutencoes m
            LEFT JOIN servico_tipos s ON m.servico_tipo_id = s.id
            WHERE m.id = ?
        """, (registro_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO manutencoes
               (data, veiculo, servico_tipo_id, descricao_pecas,
                responsavel, kilometragem_horimetro)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados["veiculo"],
                dados.get("servico_tipo_id"),
                dados.get("descricao_pecas", ""),
                dados["responsavel"],
                dados.get("kilometragem_horimetro", 0),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(self, registro_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE manutencoes
               SET data = ?, veiculo = ?, servico_tipo_id = ?,
                   descricao_pecas = ?, responsavel = ?,
                   kilometragem_horimetro = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                dados["veiculo"],
                dados.get("servico_tipo_id"),
                dados.get("descricao_pecas", ""),
                dados["responsavel"],
                dados.get("kilometragem_horimetro", 0),
                registro_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def remover(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE manutencoes SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
        return cursor.rowcount > 0

    def listar_tipos_servico(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM servico_tipos ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

    def adicionar_tipo_servico(self, nome):
        conn = self.db.connect()
        cursor = conn.cursor()
        nome = nome.strip().upper()
        cursor.execute("SELECT id FROM servico_tipos WHERE nome = ?", (nome,))
        existing = cursor.fetchone()
        if existing:
            return existing["id"]
        cursor.execute("INSERT INTO servico_tipos (nome) VALUES (?)", (nome,))
        conn.commit()
        return cursor.lastrowid
